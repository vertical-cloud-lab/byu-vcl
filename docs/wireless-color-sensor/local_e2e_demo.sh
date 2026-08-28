#!/usr/bin/env bash
# Run the whole upload pipeline locally, with no cloud accounts and no hardware.
#
# Stands up a mosquitto broker configured to behave like HiveMQ Cloud (TLS on
# 8883, username/password auth) plus a MongoDB container, then publishes
# simulated AS7341 readings through the bridge into the database.
#
# The point is to have a known-good reference: if this passes on your machine
# but the real pipeline fails, the difference is in the credentials or the
# cloud services, not in the code.
#
#   ./local_e2e_demo.sh
#
# Requires: docker, mosquitto, openssl, python3 with paho-mqtt and pymongo.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$(mktemp -d)"
PASS='local-demo-password'   # local only; nothing here reaches the internet
MQTT_PORT="${MQTT_PORT:-8883}"
MONGO_PORT="${MONGO_PORT:-27017}"

# A already-running local MongoDB or broker is the most likely reason this
# script fails, and docker reports it as an opaque networking error. Say so
# plainly instead.
for p in "$MQTT_PORT" "$MONGO_PORT"; do
  if (command -v ss >/dev/null && ss -ltn 2>/dev/null | grep -q ":$p ") ||
     (command -v lsof >/dev/null && lsof -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1); then
    echo "port $p is already in use -- stop whatever is on it, or re-run with" >&2
    echo "  MQTT_PORT=18883 MONGO_PORT=37017 $0" >&2
    exit 1
  fi
done

cleanup() {
  [ -n "${MOSQ_PID:-}" ] && kill "$MOSQ_PID" 2>/dev/null || true
  docker rm -f vcl-demo-mongo >/dev/null 2>&1 || true
  rm -rf "$WORK"
}
trap cleanup EXIT

echo "==> generating certificates"
openssl req -x509 -newkey rsa:2048 -days 1 -nodes \
  -keyout "$WORK/ca.key" -out "$WORK/ca.crt" -subj "/CN=vcl-demo-ca" 2>/dev/null
openssl req -newkey rsa:2048 -nodes \
  -keyout "$WORK/server.key" -out "$WORK/server.csr" -subj "/CN=localhost" 2>/dev/null
printf 'subjectAltName=DNS:localhost,IP:127.0.0.1\n' > "$WORK/ext.cnf"
openssl x509 -req -in "$WORK/server.csr" -CA "$WORK/ca.crt" -CAkey "$WORK/ca.key" \
  -CAcreateserial -out "$WORK/server.crt" -days 1 -extfile "$WORK/ext.cnf" 2>/dev/null

echo "==> starting broker on $MQTT_PORT (TLS + password, like HiveMQ)"
mosquitto_passwd -c -b "$WORK/passwd" vcl-sensor "$PASS" 2>/dev/null
cat > "$WORK/mosquitto.conf" <<CONF
listener $MQTT_PORT 127.0.0.1
cafile $WORK/ca.crt
certfile $WORK/server.crt
keyfile $WORK/server.key
require_certificate false
allow_anonymous false
password_file $WORK/passwd
CONF
mosquitto -c "$WORK/mosquitto.conf" > "$WORK/mosquitto.log" 2>&1 &
MOSQ_PID=$!

echo "==> starting MongoDB"
docker rm -f vcl-demo-mongo >/dev/null 2>&1 || true
docker run -d --name vcl-demo-mongo -p "127.0.0.1:$MONGO_PORT:27017" mongo:7 >/dev/null
python3 -c "import time; time.sleep(12)"

export HIVEMQ_HOST=localhost HIVEMQ_PORT="$MQTT_PORT"
export HIVEMQ_USERNAME=vcl-sensor HIVEMQ_PASSWORD="$PASS"
export MQTT_CA_CERT="$WORK/ca.crt"
export PICO_ID=local-demo
export MONGODB_CONNECTION_STRING="mongodb://localhost:$MONGO_PORT"
export MONGODB_DATABASE=vcl MONGODB_COLLECTION=color_sensor_readings

echo "==> bridge subscribing, expecting 5 readings"
python3 "$HERE/mqtt_to_mongodb.py" --loopback --expect 5 --timeout 60 &
BRIDGE_PID=$!
python3 -c "import time; time.sleep(5)"

echo "==> simulated sensor publishing"
python3 "$HERE/simulate_sensor.py" --colors off red green blue white --interval 0.8

wait "$BRIDGE_PID"; RC=$?

echo "==> what actually landed in the database"
docker exec vcl-demo-mongo mongosh --quiet --eval '
db = db.getSiblingDB("vcl");
print("documents: " + db.color_sensor_readings.countDocuments({}));
print("malformed: " + db.color_sensor_readings.countDocuments({malformed: true}));
print("loopback probes leaked: " + db.color_sensor_readings.countDocuments({raw: /loopback_probe/}));'

if [ "$RC" -eq 0 ]; then
  echo "==> PASS: the upload path works end to end"
else
  echo "==> FAIL: see the bridge output above"
fi
exit "$RC"

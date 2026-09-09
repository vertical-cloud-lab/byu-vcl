"""Command the wireless color sensor over MQTT and return the 8-channel reading.

Small, dependency-light helper shared by ``run_xscan_test.py``. One class,
``SensorLink``, holds a single broker connection open for the whole test so
each read costs one round trip (~1.4 s) rather than a fresh TLS handshake.

Credentials come from the environment (``MQTT_BROKER``, ``MQTT_PORT``,
``MQTT_USERNAME``, ``MQTT_PASSWORD``, ``PICO_ID``) so nothing is committed.
On a GitHub Actions runner these arrive from the ``env:`` block of
``claude.yml``; on the OT-2 stream-cam Pi, export them in your shell first.

Payload shape matters. The firmware indexes ``incoming["command"]["R"]`` and
``incoming["experiment_id"]``, so the command has to be nested:

    {"command": {"R": 0, "Y": 0, "B": 0}, "experiment_id": "..."}

A flat ``{"R": 0, ...}`` raises inside the board's handler, which swallows it
and publishes nothing.
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import uuid

import paho.mqtt.client as mqtt

CHANNELS = ("ch410", "ch440", "ch470", "ch510", "ch550", "ch583", "ch620", "ch670")

# 3.1.1 and 5 use different CONNACK numbering; map both to the same advice.
_CONNACK_ADVICE = {
    4: "bad username or password (MQTT 3.1.1)",
    5: "not authorized for this broker/topic (MQTT 3.1.1)",
    134: "bad username or password (MQTT 5)",
    135: "not authorized for this broker/topic (MQTT 5)",
}


class SensorError(RuntimeError):
    """Raised when the sensor link cannot be established or a read times out."""


class SensorLink:
    """A live MQTT connection to the AS7341 sensor package.

    Usage::

        with SensorLink() as link:
            link.check_delivery()          # broker really delivers to us
            reading = link.read(label="pos-1")
    """

    def __init__(self, broker=None, port=None, username=None, password=None,
                 pico_id=None, timeout=20.0):
        self.broker = broker or os.environ.get("MQTT_BROKER")
        self.port = int(port or os.environ.get("MQTT_PORT") or 8883)
        self.username = username or os.environ.get("MQTT_USERNAME")
        self.password = password or os.environ.get("MQTT_PASSWORD")
        self.pico_id = pico_id or os.environ.get("PICO_ID")
        self.timeout = timeout

        missing = [n for n, v in (
            ("MQTT_BROKER", self.broker), ("MQTT_USERNAME", self.username),
            ("MQTT_PASSWORD", self.password), ("PICO_ID", self.pico_id),
        ) if not v]
        if missing:
            raise SensorError("missing environment variable(s): " + ", ".join(missing))

        self.command_topic = f"command/picow/{self.pico_id}/as7341/read"
        self.data_topic = f"color-mixing/picow/{self.pico_id}/as7341"
        self.probe_topic = f"{self.data_topic}/_probe"

        self._inbox = []
        self._lock = threading.Lock()
        self._connected = threading.Event()
        self._connack = None
        self._client = None

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *exc):
        self.close()
        return False

    def connect(self):
        client = mqtt.Client(client_id=f"ot2-xscan-{uuid.uuid4().hex[:8]}")
        client.username_pw_set(self.username, self.password)
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.connect(self.broker, self.port, keepalive=60)
        client.loop_start()
        self._client = client

        if not self._connected.wait(self.timeout):
            self.close()
            raise SensorError(f"no CONNACK from {self.broker}:{self.port} in {self.timeout}s")
        if self._connack:
            advice = _CONNACK_ADVICE.get(self._connack, f"CONNACK rc={self._connack}")
            self.close()
            raise SensorError(f"broker refused the connection: {advice}")

        client.subscribe([(self.data_topic, 1), (self.probe_topic, 1)])
        return self

    def close(self):
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:  # noqa: BLE001 - closing must never mask a real error
                pass
            self._client = None

    # -- callbacks ---------------------------------------------------------
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self._connack = int(rc) if rc else 0
        self._connected.set()

    def _on_message(self, client, userdata, msg):
        with self._lock:
            self._inbox.append((msg.topic, msg.payload))

    def _drain(self):
        with self._lock:
            items, self._inbox = self._inbox, []
        return items

    # -- operations --------------------------------------------------------
    def check_delivery(self, timeout=10.0):
        """Publish to our own topic and wait for the echo.

        A broker can grant a subscription and then deliver nothing when the
        credential lacks read permission, which from here is indistinguishable
        from a silent board. This tells the two apart before the robot moves.
        """
        token = uuid.uuid4().hex
        self._drain()
        self._client.publish(self.probe_topic, json.dumps({"probe": token}), qos=1)
        deadline = time.time() + timeout
        while time.time() < deadline:
            for topic, payload in self._drain():
                if topic == self.probe_topic and token in payload.decode("utf-8", "replace"):
                    return True
            time.sleep(0.05)
        raise SensorError(
            "the broker accepted the subscription but did not deliver our own probe "
            "back to us -- this is a broker permission problem, not the sensor. "
            "Grant this credential both publish AND subscribe."
        )

    def read(self, label=None, rgb=(0, 0, 0), timeout=None, retries=2):
        """Command one reading and return a dict of the 8 channels plus metadata."""
        timeout = timeout or self.timeout
        r, y, b = rgb
        last_error = None
        for attempt in range(1, retries + 2):
            experiment_id = f"{label or 'read'}-{int(time.time() * 1000)}"
            payload = {"command": {"R": r, "Y": y, "B": b},
                       "experiment_id": experiment_id}
            self._drain()
            started = time.time()
            self._client.publish(self.command_topic, json.dumps(payload), qos=1)

            deadline = started + timeout
            while time.time() < deadline:
                for topic, raw in self._drain():
                    if topic != self.data_topic:
                        continue
                    try:
                        body = json.loads(raw.decode("utf-8", "replace"))
                    except ValueError:
                        continue
                    data = body.get("sensor_data") or body
                    if not any(c in data for c in CHANNELS):
                        continue
                    reading = {c: data.get(c) for c in CHANNELS}
                    return {
                        "experiment_id": experiment_id,
                        "label": label,
                        "command": {"R": r, "Y": y, "B": b},
                        "channels": reading,
                        "total": sum(v for v in reading.values() if isinstance(v, (int, float))),
                        "latency_s": round(time.time() - started, 3),
                        "attempt": attempt,
                        "raw": body,
                    }
                time.sleep(0.02)
            last_error = f"no reply within {timeout}s (attempt {attempt})"
        raise SensorError(
            f"the sensor did not answer: {last_error}. The broker link is fine "
            "(check_delivery passed), so the board is not running -- check it is "
            "switched on and its battery is charged."
        )


def total(reading):
    """Sum of the 8 channels, the single number used for lift/seat comparisons."""
    return reading["total"]

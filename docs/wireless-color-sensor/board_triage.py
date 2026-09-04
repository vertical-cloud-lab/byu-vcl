#!/usr/bin/env python3
"""Locate which link in the wireless color sensor chain is broken.

    this script --> HiveMQ --> Pico W (AS7341) --> HiveMQ --> this script

Silence at the far end has several causes that look identical from here: the
broker can refuse to deliver, the board can be off, or the board can be awake
but wedged before it reaches the radio. Each layer is therefore checked with
its own positive control, so a failure names a cause instead of a suspect.

    python board_triage.py                 # broker + board
    python board_triage.py --lan-check     # also look for the board on the LAN
                                           # (run from a host on the lab wifi)
    python board_triage.py --lan-check --sweep   # ... and sweep, if its lease moved

Requires MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD, PICO_ID.
"""
import argparse, json, os, ssl, subprocess, sys, time

import paho.mqtt.client as mqtt

# The Pico W answers ICMP with a TTL of 255 (lwIP), where Linux hosts answer 64.
# That is what separates the board from the several Raspberry Pis sharing its
# 88:a2:9e OUI on this subnet.
BOARD_MAC = "88:a2:9e:16:48:b6"
LWIP_TTL = 255


def check_broker(pico, attempts, wait):
    """Layer 1+2: can we reach the broker, and does the board answer a command?"""
    data_topic = f"color-mixing/picow/{pico}/as7341"
    cmd_topic = f"command/picow/{pico}/as7341/read"
    probe_topic = f"{data_topic}/_probe"
    state = {"connack": None, "suback": None, "loopback": False, "readings": []}

    def on_connect(c, u, flags, rc, props=None):
        state["connack"] = str(rc)
        c.subscribe([(data_topic, 1), (probe_topic, 1)])

    def on_subscribe(c, u, mid, granted, props=None):
        state["suback"] = [str(g) for g in granted]

    def on_message(c, u, msg):
        if msg.topic == probe_topic:
            state["loopback"] = True
        elif msg.topic == data_topic:
            state["readings"].append(msg.payload.decode("utf-8", "replace"))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)
    client.username_pw_set(os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.on_connect, client.on_subscribe, client.on_message = on_connect, on_subscribe, on_message
    client.connect(os.environ["MQTT_BROKER"], int(os.environ.get("MQTT_PORT", "8883")), 60)
    client.loop_start()

    deadline = time.time() + 20
    while state["suback"] is None and time.time() < deadline:
        time.sleep(0.2)
    print(f"  CONNACK  : {state['connack']}")
    print(f"  SUBACK   : {state['suback']}")
    if state["suback"] is None:
        client.loop_stop(); client.disconnect()
        return False, False

    # Positive control. A broker may grant a subscription and then deliver
    # nothing when the credential lacks read permission, which is
    # indistinguishable from a board that never publishes.
    client.publish(probe_topic, "probe", qos=1)
    time.sleep(3)
    print(f"  loopback : {'PASS -- the broker does deliver to us' if state['loopback'] else 'FAIL -- broker permissions, not the board'}")

    for i in range(attempts):
        payload = json.dumps({"command": {"R": 0, "Y": 0, "B": 0},
                              "experiment_id": f"triage-{i}-{int(time.time())}"})
        before, sent = len(state["readings"]), time.time()
        client.publish(cmd_topic, payload, qos=1)
        while len(state["readings"]) == before and time.time() - sent < wait:
            time.sleep(0.2)
        got = len(state["readings"]) > before
        print(f"  command {i + 1}/{attempts}: {'REPLY in %.2fs' % (time.time() - sent) if got else 'no reply within %gs' % wait}")

    client.loop_stop(); client.disconnect()
    return state["loopback"], bool(state["readings"])


def _sweep(prefix):
    """Ping every host in prefix.0.0/17 and return the ones answering with a lwIP TTL.

    The board takes a fresh DHCP lease every time it boots, so checking only its
    last known address reports a false "not on the network" whenever the lease
    moved. Sweeping and filtering on TTL finds it wherever it landed.
    """
    hits = []
    for b in range(128):
        procs = [(f"{prefix}.{b}.{d}",
                  subprocess.Popen(["ping", "-c", "1", "-W", "1", "-n", f"{prefix}.{b}.{d}"],
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True))
                 for d in range(256)]
        for ip, proc in procs:
            if f"ttl={LWIP_TTL}" in (proc.communicate()[0] or ""):
                hits.append(ip)
    return hits


def check_lan(last_known_ip, sweep):
    """Layer 0: is the board on the wifi at all? Only meaningful from the lab LAN."""
    out = subprocess.run(["ping", "-c", "5", "-W", "2", "-n", last_known_ip],
                         capture_output=True, text=True).stdout
    replied = " 0% packet loss" in out
    print(f"  ping {last_known_ip}: {'reachable' if replied else 'no response'}")
    if replied:
        ttls = {int(t.split("ttl=")[1].split()[0]) for t in out.splitlines() if "ttl=" in t}
        print(f"  reply TTL: {sorted(ttls)}  ({'lwIP -- this is the Pico' if LWIP_TTL in ttls else 'not the Pico; a Linux host holds this address now'})")

    if sweep and not replied:
        prefix = ".".join(last_known_ip.split(".")[:2])
        print(f"  sweeping {prefix}.0.0/17 for a new lease (a few minutes) ...")
        for ip in _sweep(prefix):
            # Re-ping immediately before reading the table: a sweep of 32k hosts
            # takes long enough that early neighbour entries have already expired,
            # which would report the board's own MAC as unknown.
            subprocess.run(["ping", "-c", "1", "-W", "1", "-n", ip],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            neigh = subprocess.run(["ip", "neigh", "show", ip], capture_output=True, text=True).stdout
            lladdr = neigh.split("lladdr")[1].split()[0] if "lladdr" in neigh else "?"
            is_board = lladdr.lower() == BOARD_MAC.lower()
            print(f"    TTL-255 host {ip}  lladdr={lladdr}  <- {'THE BOARD' if is_board else 'another lwIP device, not ours'}")
            replied = replied or is_board

    arp = subprocess.run(["ip", "neigh", "show"], capture_output=True, text=True).stdout
    found = BOARD_MAC.lower() in arp.lower()
    print(f"  board MAC {BOARD_MAC} in ARP table: {'yes' if found else 'no'}")
    # A sweep that finds nothing only means something if it can find anything, so
    # report the other Raspberry Pi devices it did turn up as a positive control.
    peers = [l for l in arp.splitlines() if BOARD_MAC[:8].lower() in l.lower()]
    print(f"  control -- other {BOARD_MAC[:8]} devices discovered: {len(peers)}")
    return replied, found


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--attempts", type=int, default=3, help="read commands to send")
    p.add_argument("--wait", type=float, default=30.0, help="seconds to await each reply")
    p.add_argument("--lan-check", action="store_true", help="also probe the LAN (run from the lab wifi)")
    p.add_argument("--sweep", action="store_true", help="with --lan-check, sweep the /17 in case the DHCP lease moved")
    p.add_argument("--last-known-ip", default="10.60.98.128")
    args = p.parse_args()

    pico = os.environ["PICO_ID"]
    print(f"=== broker + board (device {pico}) ===")
    loopback, answered = check_broker(pico, args.attempts, args.wait)

    on_lan = None
    if args.lan_check:
        print("\n=== lan ===")
        replied, found = check_lan(args.last_known_ip, args.sweep)
        on_lan = replied or found

    print("\n=== verdict ===")
    if answered:
        print("  The whole chain works. Collect data with sensor_collect.py.")
        return 0
    if not loopback:
        print("  The BROKER is not delivering to this credential. Grant it subscribe")
        print("  (not just publish) on color-mixing/#. The board is not implicated.")
        return 1
    if on_lan is True:
        print("  The board is ON THE NETWORK but not answering, so it booted and joined")
        print("  wifi yet never reached the broker. Suspect its my_secrets.py broker")
        print("  credentials, or main.py wedged after connectWiFi.")
        return 1
    if on_lan is False:
        print("  The board is NOT ON THE NETWORK and the broker is fine, so it is not")
        print("  running: no power, or it resets before wifi associates. On battery,")
        print("  check the SHIM's power button and the charge state first -- the Pico W")
        print("  browns out on the radio's current spikes when the cell is low.")
        return 1
    print("  The broker is fine and the board is silent. Re-run with --lan-check from")
    print("  a host on the lab wifi to tell 'not powered' from 'powered but wedged'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

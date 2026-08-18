"""Copy to ``my_secrets.py`` (git-ignored) and fill in.

Only needed for the wireless MQTT path (``request_over_mqtt.py``). The USB
path (``collect_over_serial.py``) needs none of this.

These must match what is on the Pico W's own ``my_secrets.py``.
"""

HIVEMQ_HOST = ""      # e.g. "abcdef123.s1.eu.hivemq.cloud"
HIVEMQ_USERNAME = ""
HIVEMQ_PASSWORD = ""
PICO_ID = ""          # the ID used in the MQTT topics on the Pico

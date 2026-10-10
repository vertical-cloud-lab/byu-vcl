# The Pico W's files on 2026-10-10, before the settings change

Listed on the board (USB serial `e6647c15673a2438`) with `inventory.py` from RAM at 10:38 MDT,
and copied off it with `mpremote` straight afterwards. Every hash was computed **on the
board** (`hashlib.sha256`) and matched the copy on the Pi. Hashes of the four credential files are
withheld here, as on 10-09.
MicroPython: `v1.29.0 on 2026-08-24 (GNU 16.1.0 MinSizeRel)`, `Raspberry Pi Pico W with RP2040`.
AS7341 registers, read straight off the chip: ID 0x24, CFG1 8 (128x),
ATIME 100, ASTEP 999, CONFIG 0, LED 0 (off), AZ_CONFIG 255.

Only [`main.py`](main.py) is copied into this folder: every other file is byte-identical to
[`../board-2026-10-09/`](../board-2026-10-09/MANIFEST.md), except the board's own
`main.py.before-gain`, which is that folder's `main.py`. The full backup, secrets included, is on the
robot Pi (`RPI_STREAM_CAM_HOSTNAME`) in `~/pico-backups/20261010_103827_before-settings/`
(mode 700). See [`../README.md`](../README.md#rolling-back) to restore.

Differs from 10-09: `main.py` (the gain change) and the new `main.py.before-gain`. In 10-09's list but not on the board now: none.

After the install (10:42 MDT) the board differs from this table in `main.py`, `main.py.before-settings` only.

| file | bytes | sha256 (on the board) | |
| --- | --- | --- | --- |
| `as7341_test.py` | 2052 | `9c5381b440f284e9fdb63733ea5e474af3bb9be861e2695a2b473bd40e3409c8` | same as 10-09 |
| `blink.py` | 254 | `c84c785bd754058288e71dd6049fd060ebe9f627b1637fa89da61c1078d84805` | same as 10-09 |
| `error.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same as 10-09 |
| `finn_trial.py` | 363 | `fa9e3cf926a15c22a7c7881dc91af7d290cc2f0f7f1ea179e4fd1b3bda9a6bce` | same as 10-09 |
| `hivemq-com-chain.der` | 1391 | `96bcec06264976f37460779acf28c5a7cfe8a3c0aae11a8ffcee05c0bddf08c6` | same as 10-09 |
| `kernel.toolsets.jsonc` | 5926 | `d11ed03a80ad617c6a6640f6c9d0ccaeffca727451c1f200481766b83edfb04f` | same as 10-09 |
| `lib/as7341.py` | 24554 | `7e7f4c75d5e7fdbbc104a7cac1f7684f55b2166f8897ace4b1e357b9c9be24cc` | same as 10-09 |
| `lib/as7341_sensor.py` | 4577 | `d9b673c5cf0bb98f0a8eabac26b1c75ffaa8ad953d89b25f5d42b1a98cb55b88` | same as 10-09 |
| `lib/as7341_smux_select.py` | 2181 | `71d87ba02dd4046524d69d2da2af1f6080e04a8e7848832997e4dd8096d392ed` | same as 10-09 |
| `lib/data_logging.py` | 4392 | `a775e68b97f258e6aa061ad1a30b7eb64b7761aa751786472c5c1cb45d133b51` | same as 10-09 |
| `lib/functools.py` | 586 | `db31ac5f6cf30ed21904faaac50e226251a529511d775aa303a180c8e089a1fd` | same as 10-09 |
| `lib/mqtt_as.py` | 29501 | `f21f4c3bd5e6dfb4969de476b16e37101fe4e8873f7bcd031e3e4a8fd57731c7` | same as 10-09 |
| `lib/netman.py` | 2654 | `25ed9dd806fc1ab0a8c8179e1b34bc264fd9917fbdb73ffc161e3f8644a1a30e` | same as 10-09 |
| `lib/sdcard/LICENSE` | 1089 | `513e4284ffef669355593834ba8c4ce38b7ef2c7996610592e238459b684385a` | same as 10-09 |
| `lib/sdcard/sdcard.py` | 9766 | `0aac564ca1bf5e4c57a5c0447b81f07d164e2eaec96c45ad0121af1ee6858e6f` | same as 10-09 |
| `lib/sdl_demo_utils.py` | 8257 | `dfad3853efb3e8c8407edabe17d8faddb0f838323fc08a77d9d259cdc7092171` | same as 10-09 |
| `lib/ufastrsa/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same as 10-09 |
| `lib/ufastrsa/genprime.py` | 3471 | `19455b0215419a268b70f13bea7afce20d0bb73d163df74cdd1e8238b7dc6684` | same as 10-09 |
| `lib/ufastrsa/rsa.py` | 1602 | `f22236a641580e47f276090844d2e221da76e937fd37049a5acac36d51ed067a` | same as 10-09 |
| `lib/ufastrsa/srandom.py` | 1242 | `bc73779dfd1e28feabc47c6e18123b63db67a81f65f5fc927d9dc3c3144ad09c` | same as 10-09 |
| `lib/ufastrsa/util.py` | 226 | `d7bf6aa28317dc64871de932a483fed6bcd9a3e7978be54736cd49aac1ca88bf` | same as 10-09 |
| `lib/umqtt/robust.py` | 1046 | `57da9d670e9232f33983a3e87943e310599d0dbcb61c8b6379494e0f92ea9ed3` | same as 10-09 |
| `lib/umqtt/simple.py` | 6634 | `5ce3477fa56d4c56fbb65eb5a1639015d6967b21f15eaa1463c05141e14e3c86` | same as 10-09 |
| `lib/urequests_2.py` | 5731 | `39cf541ae8745a50dcaf260116e925288961971200f24ec89a5b83f5b49be3ba` | same as 10-09 |
| `log.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | same as 10-09 |
| `main.py` | 8990 | `0876445a803439e469aa9795b105832de9ff738f70770872b34889572fef4a94` | **changed 10-09** (the gain change): in this folder |
| `main.py.before-gain` | 6432 | `469a5a6d03f4b673c3645b7369ab2ec526c4f404592ce2dae932278640476196` | new since 10-09: the board's own copy of its pre-gain `main.py` |
| `my_secrets.py` | 2281 | withheld | **not in the repo:** Wi-Fi and MQTT credentials. Byte-identical to the 10-09 backup (compared on the Pi). On the board and in the Pi backups only |
| `my_secrets.py.bak` | 698 | withheld | **not in the repo:** older credentials file. Byte-identical to the 10-09 backup (compared on the Pi). On the board and in the Pi backups only |
| `pico_id.txt` | 16 | `3aab1c564a837ab49aafc7716c8d4151f2b6348d7e67c35fdbfbf041a96ca999` | same as 10-09 |
| `rsa.json` | 193 | withheld | **not in the repo:** key material for lib/ufastrsa (unused by main.py). Byte-identical to the 10-09 backup (compared on the Pi). On the board and in the Pi backups only |
| `sam_trial.py` | 267 | `2cd4af4d18075816d2749e8c37b7db63d4b9debe7d3be64f093cc7c00d02c604` | same as 10-09 |
| `secrets.py` | 700 | withheld | **not in the repo:** credentials (unused by main.py). Byte-identical to the 10-09 backup (compared on the Pi). On the board and in the Pi backups only |

# A stand-in printer for testing `bambu_print.py`

[`fake_printer.py`](fake_printer.py) plays an A1 mini on a local MQTT broker. It answers
`pushall` and `get_version`, runs a short fake print on `project_file`, obeys
pause/resume/stop, and serves camera frames with the real login and framing. Together with a
local implicit-TLS FTPS server, it lets every subcommand be run with no printer involved.
Use it after any change to the tooling, before running that change on the real printer.

```bash
# a certificate, an FTPS server that insists on TLS session reuse like the printer's, and a broker
openssl req -x509 -newkey rsa:2048 -nodes -keyout /tmp/vsftpd.key -out /tmp/vsftpd.pem -days 2 -subj /CN=TESTSERIAL
sudo apt-get install -y vsftpd mosquitto
sudo useradd -M -d /tmp/ftphome2 bblp && echo 'bblp:testcode1' | sudo chpasswd
sudo mkdir -p /tmp/ftphome2 /var/run/vsftpd/empty && sudo chown bblp /tmp/ftphome2
# /tmp/vsftpd.conf (owned by root): listen=YES, listen_port=9990, local_enable=YES,
#   write_enable=YES, ssl_enable=YES, implicit_ssl=YES, require_ssl_reuse=YES,
#   force_local_data_ssl=YES, force_local_logins_ssl=YES, strict_ssl_read_eof=YES,
#   chroot_local_user=YES, allow_writeable_chroot=YES, pasv_min_port=40000,
#   pasv_max_port=40100, seccomp_sandbox=NO, background=NO,
#   rsa_cert_file=/tmp/vsftpd.pem, rsa_private_key_file=/tmp/vsftpd.key
sudo vsftpd /tmp/vsftpd.conf &
# /tmp/mosq.conf: listener 18883 / certfile /tmp/vsftpd.pem / keyfile /tmp/vsftpd.key /
#   allow_anonymous false / password_file /tmp/mosq.passwd  (mosquitto_passwd -b ... bblp testcode1)
mosquitto -c /tmp/mosq.conf &
python test/fake_printer.py --fault none &        # or hms, hot, cold-bed

export TEST_IP=127.0.0.1 TEST_ACCESS_CODE=testcode1 TEST_SERIAL=TESTSERIAL
export BAMBU_PORT_MAP=8883:18883,990:9990,6000:16000
python bambu_lan.py preflight --printer TEST --via '' --3mf FILE --out /tmp/t_out
python bambu_print.py upload FILE --printer TEST --via ''
python bambu_print.py start FILE --printer TEST --via '' --preflight /tmp/t_out/<stamp>_preflight.json \
    --ams-slot 0 --confirmed-by someone
python bambu_print.py watch --printer TEST --via '' --3mf FILE --minutes 2 --frame-every 8
```

What the runs on 2026-09-27 showed, with the lid mount's 3MF:

| Case | Result |
|---|---|
| upload, then read back over a fresh connection | 2,444,660 bytes, MD5 matches |
| file name with a space | refused before connecting |
| `start` without `--confirmed-by`, with a stale or NO-GO preflight, or on a busy printer | refused |
| `--fault none` | PREPARE → RUNNING → FINISH; `watch` exits 0 with a frame per interval |
| `--fault hms` | the printer pauses with HMS `0700_0200_0002_0001` (serious); `watch` exits 20 |
| `--fault hot` with `--auto-stop` | nozzle 280 °C; `watch` exits 40 and `stop` is confirmed by the FAILED state |
| `--fault cold-bed` | bed falls to 40 °C against a 65 °C target; `watch` exits 20 after 90 s |
| `stop` without `--yes-stop` | refused |
| `watch` on an idle printer | exits 20 at once: nothing is printing |

The stand-in is only as faithful as what is known about the printer. It can't show how the
real firmware answers a command it rejects, or which states it passes through on the way.

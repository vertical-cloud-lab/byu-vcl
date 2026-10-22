# EZstat-Pro: first hardware runs

Dr. Porter's NuVant **EZstat-Pro**, serial `EZST15073101 V2`, borrowed for
[#231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231). The label says
EZstat-Pro, not EZstat-Pro EIS, so it has **no EIS**. It does have cyclic,
linear-sweep and pulse voltammetry, battery cycling, potential steps, a
galvanostat mode and step impedance spectroscopy (SIS) (manual p. 9).

This folder holds the runbook (this file), the [run log](run-log.csv), two
PowerShell scripts for the Windows PC, a script that checks the first runs, and
[`results/`](results/) for the exported data.

Manual: [EZware Operating Manual, EZware 7.0 (2013)](https://www.nuvant.com/sites/default/files/2022-05/EZware-2013-Manual-compressed2.pdf),
which NuVant lists for EZstats from April 2013 on. Page numbers below are the
manual's.

## 1. It plugs into a Windows PC, not the Pi

The EZstat-Pro is NuVant's analog front end around a National Instruments USB
data-acquisition board. All the software that talks to it is Windows-only:

- EZware-2013 is a 32-bit Windows program built with LabVIEW 2011 SP1 (it
  ships LabVIEW's 11.0.1 analysis library).
- It needs NI's LabVIEW 2011 Run-Time Engine and NI's NI-DAQmx driver.
- NI-DAQmx comes for Windows, and for Linux only on x86-64 PCs ("NI-DAQmx for
  Linux/x86 64-bit Architecture"). There is no build for ARM, so the CubXL's
  Raspberry Pi 5 can't load the driver. Plugged into the Pi, the EZstat would
  just be a USB device that nothing can talk to.

Use the Windows PC that may have come with it (the one with the Watlow
EZ-ZONE programs), or any Windows laptop you have administrator rights on.

That PC runs Windows 7, which no longer gets security updates, so it stays off
BYU's network and the internet. Its Ethernet port is cabled to the CubXL Pi
(des4) and nothing else, and the Pi forwards Remote Desktop to it from the
tailnet ([setup on #231](https://github.com/vertical-cloud-lab/byu-vcl/issues/231#issuecomment-6327249004)).
The Pi only passes that traffic along. The EZstat's USB cable still goes into
the PC.

### The PC, as a Claude session sees it (2026-10-21)

| | |
|---|---|
| PC | Windows 7 Professional SP1 (build 7601), 64-bit, PowerShell 2.0. It's in a workgroup, not a BYU domain, so it uses local accounts. Its clock was within 1 s of UTC |
| Open ports | Remote Desktop (3389) only. File sharing (139, 445), RPC (135) and WinRM (5985, 5986) are closed, so there's no way in without a Remote Desktop login |
| Remote Desktop | NLA is offered but not required, so a client gets to the Windows login screen without a password ([screenshot](images/2026-10-21-pc-login-screen-from-ci.png)) |
| Login | `POTENTIOSTAT_PC_USERNAME` / `POTENTIOSTAT_PC_PASSWORD`, passed to `@claude` runs since #294. The account is a member of Administrators, behind UAC: windows start without admin rights, and installers need **Run as administrator** |
| EZstat | Its board is a **USB-6221 OEM** (`USB\VID_3923&PID_72E0`), plugged into the PC. Not plugged into des4, which is right. Since 2026-10-22 it has its driver: NI MAX lists it as **NI USB-6221 (OEM) "Dev1"**, status Present ([screenshot](images/2026-10-22-nimax-usb-6221-dev1.png)) |

The first check over Remote Desktop is in [`pc-check-2026-10-21.md`](pc-check-2026-10-21.md);
what it means is under [step 0](#step-0-check-the-pc-5-minutes-changes-nothing).

### Driving the PC from a Claude session

The runner can't reach `192.168.231.10` itself, so the Remote Desktop client
runs **on des4**, on a virtual display, and the session drives it over SSH with
[`scripts/ezstat-pc-rdp/`](../../scripts/ezstat-pc-rdp/). `drive.sh` runs on
the runner and copies `pi_drive.sh` to a temporary folder on des4 for each
session. des4 has FreeRDP 3 and Xvfb. `xdotool` isn't installed, but unpacked
in `~/ezrdp/xdo` (`apt-get download xdotool libxdo3 libxtst6`, then `dpkg -x`
each, no `sudo`, 2026-10-21).

```bash
# Screenshots need numpy and Pillow. drive.sh runs Python with -I, which skips
# user site-packages, so put them in a venv.
python3 -m venv /tmp/ezvenv && /tmp/ezvenv/bin/pip install numpy pillow
export PY=/tmp/ezvenv/bin/python

# 1. Log in. The credentials reach xfreerdp3 over stdin, never in a process
#    list. 3300 is a hard stop in seconds, after which the client is killed
#    (a disconnect, not a log-off). RDP_SHARE is optional: the PC then sees
#    that des4 folder as \\tsclient\ez.
RDP_SHARE="/home/$CUBXL_PI_USERNAME/ezrdp/share" scripts/ezstat-pc-rdp/drive.sh start 3300

# 2. Run something: Win+R, type, Enter, wait, screenshot. One step per line;
#    see pi_seq.sh. The PNG lands in /tmp/ezmap/png/s1-a.png, and the
#    script's output in the share, on des4.
printf '%s\n' 'key super+r' 'sleep 2' \
  't cmd /c powershell -NoProfile -ExecutionPolicy Bypass -File \\tsclient\ez\check-ezstat-pc.ps1 > \\tsclient\ez\check.out 2>&1' \
  'key Return' 'sleep 60' 'shot a' | scripts/ezstat-pc-rdp/drive.sh seq s1

# 3. Leave: this disconnects without logging off, and cleans up on des4.
scripts/ezstat-pc-rdp/drive.sh stop
```

- **Check who's on the PC before doing anything.** `query user` and
  `query session` list every Windows session, and `tasklist /v` what's
  running. Run them with `cmd /c ... > \\tsclient\ez\who.txt` and read the file
  on des4. On 2026-10-22 ours was the only session, with the PC's own screen at
  the login prompt.
- **`(` and `)` don't arrive.** FreeRDP drops them from Xvfb's keymap. Type them
  as `key shift+9` and `key shift+0`, or better, put the commands in a `.ps1` in
  the share and type only the `-File` line.
- **Copying files to the PC goes through the share.** robocopy from
  `\\tsclient\ez` ran at about 30 MB/s over the 1 Gbit/s cable: 1,241 files,
  1.95 GB, in 66 s ([`windows/stage-from-des4.ps1`](windows/stage-from-des4.ps1)).
  The slow part is des4's own download, over its Wi-Fi.
- **PowerShell's `Add-Content` writes nothing to `\\tsclient`**, and raises no
  error (2026-10-22). `[IO.File]::AppendAllText`, robocopy's `/LOG:` and
  `cmd`'s `>` all do write there. A `powershell -File` window closes when the
  script ends, taking its output with it, so start scripts as
  `cmd /c powershell ... > \\tsclient\ez\<name>.out 2>&1`.
- **A login takes over the PC's only desktop.** Windows 7 allows one session at
  a time, so whoever is at the PC is locked out until the session ends.
- **Disconnect, don't log off.** Stopping the client leaves the Windows session
  and its programs running, with the PC at its lock screen. Whoever logs in at
  the PC with the same account gets that session back. Logging off would close
  whatever they had open.
- **`/tls:seclevel:0` is required.** Without it OpenSSL 3 refuses Windows 7's
  TLS (`ERRCONNECT_TLS_CONNECT_FAILED`). FreeRDP 3 logs a parse error for that
  line but applies it. FreeRDP 2 on a runner spells it `/tls-seclevel:0`.
- **To test the login without taking over the desktop, add `/auth-only`.** It
  logs Kerberos errors (expected, as this is a workgroup PC) and *Authentication
  only, exit status 1*, yet got as far as licensing with the right password.
  With NLA the PC goes on to licensing only after it accepts the password. A
  wrong password hasn't been tried, so its output is unknown.
- **Don't commit desktop screenshots.** The desktop shows other people's folder
  names, and this repo is public. Crop to the window you need.

## 2. Accounts and subscriptions: none needed

| Software | Cost and accounts |
|---|---|
| EZware-2013 | Comes with the instrument. The installer asks for no serial number or activation code. Licence: one program on one machine (manual p. 2) |
| LabVIEW 2011 SP1 Run-Time Engine | Free. It's NI's engine for running finished LabVIEW programs, and needs no activation |
| NI-DAQmx | Free driver, no activation |
| **Not needed** | The LabVIEW development system (a paid subscription), EZware-EIS (EIS model only), NI-Serial (temperature and mass-flow options only), an NI or NuVant account |

The one catch is downloading. NI's download pages now say "Log in to download",
and "Downloading older versions of software requires an active subscription or
service agreement." The direct links in §3 are NI's own file server and
downloaded without logging in on 2026-10-20. If they stop working, ask NuVant
for the installers (info@a3global.com, or the
[support form](https://www.nuvant.com/request-support)).

Installing drivers needs administrator rights on the PC. On a BYU-managed PC
that may mean asking IT.

## 3. Software

All four files were downloaded on 2026-10-20 and checked: version, size,
SHA-256, and that the NI installers carry a code signature.

| Step | What | Version | File (link) | Bytes | SHA-256 |
|---|---|---|---|---|---|
| 1 | LabVIEW Run-Time Engine, 32-bit | 2011 SP1 | [`LVRTE2011SP1std.exe`](https://download.ni.com/support/softlib/labview/labview_runtime/2011%20SP1/LVRTE2011SP1std.exe) | 224,373,344 | `b31615048274ec23c6b181a7a93b786828738f18a7cf8c784a3eec251cbcf29c` |
| 2 | NI-DAQmx, **Windows 7 or 8.0** | 9.7.0 | [`NIDAQ970f0.zip`](https://download.ni.com/support/softlib/multifunction_daq/nidaqmx/9.7.0/NIDAQ970f0.zip) | 1,673,463,452 | `2bbf32fd84a5f593a872c1571f02aba8b03de5b638777e429da9447f854f084f` |
| 2 | NI-DAQmx, **Windows 8.1, 10 or 11** | 14.5.1 | [`NIDAQ1451f1.zip`](https://download.ni.com/support/softlib/multifunction_daq/nidaqmx/14.5.1/NIDAQ1451f1.zip) | 1,748,101,421 | `0e3cba22e4b6cac59cd7d16e45158eabdb51c384810dff343607ed0d1f43708d` |
| 3 | EZware-2013 | 7.1.16.1025 | [`Ins EZware-2013 v.7.1.16.1025.exe`](https://web.archive.org/web/20190517053447id_/http://nuvant.com/downloads/Ins%20EZware-2013%20v.7.1.16.1025.exe) | 14,491,458 | `5f8e8cd4e28f8443441ea05ac530949988a82f2856bded73c28af7ca93349101` |

- **The run-time is 2011 SP1, not the 2012 that the manual links.** The EZware
  program inside the installer asks for LabVIEW Run-Time 11.0, which is 2011.
- **EZware comes from the Wayback Machine.** NuVant listed this installer on
  its downloads page until at least January 2022; its own link now returns 404.
  This copy was saved from nuvant.com in May 2019. It isn't code-signed, so
  Windows will warn about an unknown publisher: check the hash first.
- **No NI-DAQmx release supports both LabVIEW 2011 and Windows 10 or 11.**
  - 9.7 lists Windows 8, 7, Vista and XP, and LabVIEW 2009–2012. It's the
    version NuVant's manual names.
  - 14.5.1 lists Windows 8.1, 8, 7, Vista and XP, and LabVIEW 2011–2014.
  - From 15.0 on, LabVIEW 2011 is dropped.

  So on Windows 10 or 11, 14.5.1 is the best guess, not a supported
  combination. If it fails, ask NuVant which versions they use on Windows 10/11.
- **On Windows 11, "Memory integrity"** (Windows Security → Device security →
  Core isolation) can stop old drivers from loading. The PC check reports
  whether it's on. Whether to turn it off is a decision for whoever looks after
  the PC.
- **The board inside is a USB-6221 OEM** (NI M Series, 16-bit, 250 kS/s),
  as Windows on the lab PC reported it on 2026-10-21. Not a USB-621x, as
  this runbook first guessed from the spec. NI-DAQmx 9.7.0 drives it: its
  driver file `nixswv.inf` lists `USB\VID_3923&PID_72E0` as *USB-6221 (OEM)*,
  and the lab PC's board has worked with it since 2026-10-22. 14.5.1 hasn't
  been checked.

**To download:** run [`windows/get-ezstat-software.ps1`](windows/get-ezstat-software.ps1).
It picks the NI-DAQmx for the PC's Windows version, saves everything to
`Downloads\ezstat-software`, and checks every hash. It downloads only and
installs nothing. It's about 2 GB, so if the lab PC has no internet, run it on
any Windows laptop and carry the folder over on a USB stick. Or use the links
in the table and check each file with `certutil -hashfile "<file>" SHA256`.

**Downloading on a laptop for the Windows 7 PC? Add `-DAQmx 9.7`:**
```
powershell -ExecutionPolicy Bypass -File .\get-ezstat-software.ps1 -DAQmx 9.7
```
Otherwise the script picks the NI-DAQmx for the Windows it's running on, so a
Windows 10 or 11 laptop would fetch 14.5.1. On Windows 7, 9.7 is the supported
version, and the one the manual names. The set is then about 1.9 GB.

## 4. Steps

### Step 0. Check the PC (5 minutes; changes nothing)

1. Open [`windows/check-ezstat-pc.ps1`](windows/check-ezstat-pc.ps1) on GitHub,
   click **Download raw file**, and save it on the PC. The Windows 7 PC is
   offline, so download it on a laptop and bring it over on a USB stick, or
   copy it across in Remote Desktop.
2. In that folder, Shift + right-click → **Open command window here** (Windows 7)
   or **Open PowerShell window here** (Windows 10 or 11), and run:
   ```
   powershell -ExecutionPolicy Bypass -File .\check-ezstat-pc.ps1
   ```
3. It copies its report to the clipboard. Paste it into a comment on the PR.
   - Over Remote Desktop, the clipboard is shared, so paste it on your laptop.
   - Sitting at the offline PC, paste it into Notepad and save it to the USB
     stick.

It reports the Windows version, admin rights, Secure Boot and Memory integrity,
any NuVant, NI and Watlow software with versions, where EZware is installed, any
EZware data files (`*.nuvdt`) and their dates, and any NI USB device plugged in.

If EZware, Run-Time 2011 and an NI-DAQmx that supports LabVIEW 2011 are all
there, skip step 1 and don't update anything.

**Result on the lab PC, 2026-10-21** ([report](pc-check-2026-10-21.md)): only
NI-DAQmx is missing.

| Needed | Found |
|---|---|
| EZware-2013 | 7.1.16.1025, installed 2026-10-20, in `C:\Program Files (x86)\EZware-2013 v.7.1.16.1025\` |
| LabVIEW Run-Time 2011 SP1 | 11.0.448.0, installed 2013 (Run-Times 2012 SP1, 2013 and 2014 too) |
| NI-DAQmx | **Missing.** Only *NI-DAQmx/LabVIEW shared documentation 9.7.5* is left, and no driver version in the registry |
| NI MAX | 5.5.1 |
| The EZstat | Windows sees a **USB-6221 OEM** with **problem code 28**, "the drivers for this device are not installed" |

So on this PC, step 1 was NI-DAQmx alone. A Claude session installed it from
des4 on 2026-10-22, with the EZstat left plugged in, then restarted the PC
([how](#installing-from-des4-with-nobody-at-the-pc)). NI-PAL 14.0 and NI-VISA
14.0.1 from 2019 were already there, newer than the ones NI-DAQmx 9.7 bundles;
the installer didn't object to them, and kept them.

**Result after the install and restart, 2026-10-22** ([report](pc-check-2026-10-22.md)):

| | |
|---|---|
| NI-DAQmx | **9.7.0**, in the registry and the programs list |
| The EZstat's board | **Working.** Device Manager error code 0 (was 28), status OK, NI's kernel driver `nixsrkw` loaded. Nobody unplugged it |
| NI MAX | **NI USB-6221 (OEM) "Dev1"**, serial 01A801CD, status Present ([screenshot](images/2026-10-22-nimax-usb-6221-dev1.png)). EZware's Tools → Configure should offer `Dev1` |
| Everything else | Nothing removed: the report has only additions. EZware, Run-Time 2011 SP1 and NI MAX 5.5.1 are as they were. The installer also added the older LabVIEW Run-Times it bundles (8.2.1, 2009 SP1, 2010 SP1) |
| Calibration | The board's last external calibration and self-calibration were both on 2015-07-16, and NI recommended the next external one for 2016-07-16. R1 and R2 in step 3 will show whether it still meets the 1 % slope check |

**9.7.0 does know this board.** Its driver file `nixswv.inf` (in
`Products\NI-DAQmx_Core\MIO\nimioi64.cab`, dated 2013-02-08) lists
`USB\VID_3923&PID_72E0` as *USB-6221 (OEM)*.

### Step 1. Install what's missing, in this order (manual p. 40)

Keep the EZstat's USB cable unplugged from the PC until step 2. If it's already
plugged in, and Device Manager shows the board with code 28 ("the drivers for
this device are not installed"), leave it: install, restart, and Windows finds
the board's new driver as it starts up. That's what happened on the lab PC on
2026-10-22. The manual's order only matters so that Windows finds the driver
the first time it sees the board; a restart gives it another look. A restart
also disables the cell (§5).

1. Run `LVRTE2011SP1std.exe` with the default options. Restart.
2. Unzip the NI-DAQmx zip and run `setup.exe` inside it, with the default
   options. Restart.
3. Run `Ins EZware-2013 v.7.1.16.1025.exe`. No restart needed.

#### Installing from des4, with nobody at the PC

The PC is offline, so des4 does the downloading. This is how NI-DAQmx 9.7.0
went onto the lab PC on 2026-10-22, and works for any installer in §3.

1. **On des4:** download at a capped rate, since des4 is on Wi-Fi, check the
   hash against §3, unzip into a new folder, and write a manifest of every file:
   ```bash
   mkdir -p ~/ezrdp/nidaqmx970/share && cd ~/ezrdp/nidaqmx970
   curl -fL --limit-rate 4M -C - -O https://download.ni.com/support/softlib/multifunction_daq/nidaqmx/9.7.0/NIDAQ970f0.zip
   sha256sum NIDAQ970f0.zip      # 2bbf32fd...f854f084f
   mkdir share/NIDAQ970f0 && (cd share/NIDAQ970f0 && unzip -q ../../NIDAQ970f0.zip)
   (cd share/NIDAQ970f0 && find . -type f -print0 | sort -z | xargs -0 sha256sum | sed 's#  \./#  #') > share/NIDAQ970f0.sha256
   ```
   At 4 MB/s the 1.67 GB took 6 min 38 s. Put
   [`windows/stage-from-des4.ps1`](windows/stage-from-des4.ps1) and
   [`windows/install-nidaqmx.ps1`](windows/install-nidaqmx.ps1) in `share/`
   with Windows line endings (`sed 's/$/\r/'`).
2. **Log in** with `RDP_SHARE` set to that `share` folder
   ([above](#driving-the-pc-from-a-claude-session)), and check nobody else is
   on the PC.
3. **Copy and check:** Win+R,
   `cmd /c powershell -NoProfile -ExecutionPolicy Bypass -File \\tsclient\ez\stage-from-des4.ps1 > \\tsclient\ez\stage.out 2>&1`.
   It copies the folder to `Downloads\ezstat-software\` and checks every file's
   SHA-256: 1,241 files in 66 s, then about 2 min to hash them.
4. **Install:** the same with `install-nidaqmx.ps1`. Windows asks for admin
   approval: check that the prompt names *National Instruments Installer*,
   verified publisher *National Instruments Corporation*, then press Alt+Y. It
   runs NI's `setup.exe /qb /AcceptLicenses yes /r:n`: default features, a
   progress bar and no questions. Those are the switches the installer's own
   help text documents. It doesn't mention `/log` or `/disableNotificationCheck`,
   so they weren't used. It took 23.5 min, including 6 min with the bar
   stopped at 65% and the PC nearly idle, probably waiting out a network
   timeout, since the PC has no internet.
   PowerShell 2.0's `Start-Process -Verb RunAs` returns no exit code, so the
   script reports the version in the registry instead.
5. **Check nobody else is on the PC, then restart** from the session:
   `cmd /c shutdown /r /t 10`. It needs no admin approval. This ends the
   Remote Desktop session too. The lab PC was back on port 3389 2.5 min later.
   Log in again and rerun the [PC check](windows/check-ezstat-pc.ps1).

des4 keeps the checked zip in `~/ezrdp/nidaqmx970/`; the unzipped copy there was
deleted afterwards. The PC keeps its copy in `Downloads\ezstat-software\NIDAQ970f0`.

### Step 2. Plug in the EZstat: now, and not before

1. Nothing connected to the leads, and the **Cell Enable** button out (off).
   Metal-cased EZstats have no such button; EZware enables the cell instead
   (manual p. 32).
2. Plug the USB cable into the back of the EZstat, but not into the PC yet.
3. Plug in the power supply, at least 1 ft from the EZstat to keep its noise
   out of the signal (manual p. 36). Press the power switch: it lights green and
   the fan starts.
4. Now plug the USB cable into the PC. Windows reports new hardware, then NI's
   Measurement & Automation Explorer (NI MAX) does (manual p. 40).
5. Open NI MAX → **Devices and Interfaces** and note the device's name, for
   example "NI USB-6211". **Don't open its Test Panels**: they can drive the
   outputs that set the cell potential.
6. Open EZware. Choose **Tools → Configure**, highlight the device, click
   **Done**. If it asks for the model, choose **EZstat-Pro**: the wrong model
   stops it working properly (manual p. 43).
7. For the session, turn off sleep and Windows Update. If the PC freezes, the
   cell can stay on, uncontrolled (manual p. 26). For Remote Desktop, leave
   sleep off for good (`powercfg -change -standby-timeout-ac 0`): a sleeping
   PC stops answering it.

### Step 3. First runs, on dummy loads (no chemistry)

**Leads** (manual pp. 31 and 35): counter red, reference white, working black,
working sense black (the second black one), ground green. Work out which black
lead is which and label them first. Connect only with the cell disabled, in the
order ground, reference, counter, working sense, working. Disconnect in the
reverse order.

**Parts:** 1 kΩ and 10 kΩ resistors (1 %), a 1 µF film capacitor, a
multimeter. Measure each resistor with the multimeter and write the value in the
run log, since the check is against that value rather than the label.

| Run | Load and wiring | Recipe | Passes if |
|---|---|---|---|
| R1 | 1 kΩ. Working and working sense on one end, reference and counter on the other (manual p. 103) | **Technique → Sweep Techniques → Cyclic Voltammetry.** Pretreatment 2 s at −0.5 V; initial −0.5 V; vertex 1 +0.5 V; vertex 2 −0.5 V; 4 segments (two cycles); final −0.5 V; 50 mV/s. **Method → General Settings**: potentiostat current range 10 mA, no auto-range. *Cell ON After Measurement* unticked | A straight line through zero, ±0.5 mA at ±0.5 V, and both cycles on top of each other. Slope within 1 % of 1/R from the meter |
| R2 | 10 kΩ, same wiring | Same CV, with current range 100 µA | ±50 µA, slope within 1 % |
| R3 | Dummy cell: 1 kΩ in series with (10 kΩ in parallel with 1 µF). Working and working sense on the 1 kΩ end, reference and counter on the other | **Technique → Step Techniques → Step Impedance Spectroscopy** (runs at controlled current). Initial current 0 A; pulse amplitude 50 µA; pulse width 0.1 s; relaxation 0.5 s; sampling interval as short as it allows, ideally 0.01 ms | At the pulse edge the potential jumps 50 mV (the 1 kΩ), then rises to about 0.55 V with a 10 ms time constant. EZware's SIS analysis (manual p. 90) gives Rs ≈ 1 kΩ, Rct ≈ 10 kΩ, Cdl ≈ 1 µF. With 1 ms sampling, only the 0.55 V plateau and the 10 ms time constant can be checked: the 50 mV jump can't be told apart from the start of the rise |

- R1 is NuVant's own instrument check (manual p. 103). If it fails, the
  instrument or software is at fault, not a cell.
- R2 checks a second current range.
- R3 checks the galvanostat and the step-impedance analysis. Without EIS, SIS is
  this instrument's way to measure solution resistance from a current step, which
  is what a conductivity reading needs (Block B in #231).
- Write down any field EZware shows that isn't listed here, such as a sampling
  interval for the CV, and keep its default.

### Step 4. Save every run and add it here

1. **File → Save** as `<run_id>.nuvdt`. That's EZware's own format, and it keeps
   the recipe (manual p. 79).
2. **Tools → File Export → Data Configuration**: tick time, potential and current,
   plus anything else offered. Then **File → Export as** `<run_id>.csv`.
3. Fill in a row of [`run-log.csv`](run-log.csv). Use run IDs like
   `20261021-R1`.
4. Put the files in `results/<YYYYMMDD>_<short-name>/` on this PR's branch
   ([how](results/README.md)), or attach a zip to a comment on the PR.
5. Mention Claude in a comment on the PR. It will check the runs against the
   "passes if" column and plot them with
   [`analysis/check_dummy_runs.py`](analysis/check_dummy_runs.py), which anyone
   can run too (Python with numpy and matplotlib):
   ```
   python analysis/check_dummy_runs.py R1 results/20261021_dummy-loads/20261021-R1.csv --r-ohm 998.7
   python analysis/check_dummy_runs.py R3 results/20261021_dummy-loads/20261021-R3.csv
   ```
   It finds the time, potential and current columns by name, reads units such
   as "(mA)" from the header, and writes a `.check.png` plot and a
   `.check.json` summary next to each CSV. It was tested on made-up data, since
   no EZware export exists yet; if the real column names trip it up, it has
   options to name the columns.

## 5. Safety (manual pp. 26–35)

- Never connect or disconnect a lead while the cell is enabled.
- Don't leave a run unattended. A shutdown, restart or power cut disables the
  cell, but a frozen PC can leave it on and uncontrolled.
- Plug the power supply into an earthed outlet. Leave 2 in of space behind the
  EZstat and 3 in at the sides, and put nothing on top of it.
- Use only the cables that came with it.

## 6. After the dummy loads

Next come the chemistry runs from the 15 and 19 October plans in #231: the
ferricyanide CV (Block C), and the U of U probe (Block B). For the probe, use
SIS and reversing constant-current steps in place of EIS.

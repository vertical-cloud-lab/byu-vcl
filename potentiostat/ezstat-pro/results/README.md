# EZstat-Pro results

One folder per session, named `<YYYYMMDD>_<short-name>`, for example
`20261021_dummy-loads`. In it:

- every run's `<run_id>.nuvdt` and `<run_id>.csv` (see step 4 of
  [the runbook](../README.md));
- photos of the wiring, named after the run;
- a short `README.md`: who ran it, the PC, and the EZware, LabVIEW Run-Time and
  NI-DAQmx versions. Pasting the PC check's report is enough.

Add a row per run to [`../run-log.csv`](../run-log.csv) as well.

**Uploading from a browser:** name a folder on your computer as above and put
the session's files in it. Open this PR's branch on GitHub, go to
`potentiostat/ezstat-pro/results/`, choose **Add file → Upload files**, and drag
the whole folder onto the page; GitHub keeps the folder name. Commit straight to
the PR's branch, not a new one.

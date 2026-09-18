# AC Microcourses assignment templates (post–GitHub Classroom)

The [AC Microcourses](https://ac-microcourses.readthedocs.io/en/latest/) coding exercises were
distributed through GitHub Classroom. **Classroom was decommissioned on 28 August 2026**, so every
`https://classroom.github.com/a/<id>` link in the course docs is dead — they now `301` to the
[farewell discussion](https://github.com/orgs/community/discussions/205975). Verified 18 September 2026:

```console
$ curl -sI https://classroom.github.com/a/3yCVzX6I | grep -i '^http/\|^location'
HTTP/2 301
location: https://github.com/orgs/community/discussions/205975
```

The assignments themselves are fine. Accepting a Classroom assignment only ever did one thing —
copy a template repo into your account — and **the template repos are public and still there**.
GitHub's notice confirms "any accounts, repositories, and organisations you created through
Classroom are not affected by this service retirement." So you can do the copy yourself.

## Where the templates live

The AC keeps one org per course
([ac-microcourses README](https://github.com/AccelerationConsortium/ac-microcourses#readme)):
[ACC-HelloWorld](https://github.com/ACC-HelloWorld),
[ACC-DataScience](https://github.com/ACC-DataScience),
[ACC-Robotics](https://github.com/ACC-Robotics),
[ACC-SoftwareDev](https://github.com/ACC-SoftwareDev),
[ACC-DesignProject](https://github.com/ACC-DesignProject).

### Course 1 — Hello World (`ACC-HelloWorld`)

All eight are public, flagged `is_template`, and ship a `.devcontainer`, so each one is a working
Codespace out of the box. "Generate" is the one-click *create a copy* link.

| Course module | Template | Generate |
| --- | --- | --- |
| [1.0 orientation](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.0-orientation.html) (Python refresher) | [`python-refresher`](https://github.com/ACC-HelloWorld/python-refresher) | [generate](https://github.com/ACC-HelloWorld/python-refresher/generate) |
| [1.1 running the demo](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.1-running-the-demo.html) | [`1-running-the-demo`](https://github.com/ACC-HelloWorld/1-running-the-demo) | [generate](https://github.com/ACC-HelloWorld/1-running-the-demo/generate) |
| ” (static copy) | [`1-running-the-demo-public`](https://github.com/ACC-HelloWorld/1-running-the-demo-public) | [generate](https://github.com/ACC-HelloWorld/1-running-the-demo-public/generate) |
| [1.2 blink and read](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.2-blink-and-read.html) | [`2-blink-and-read`](https://github.com/ACC-HelloWorld/2-blink-and-read) | [generate](https://github.com/ACC-HelloWorld/2-blink-and-read/generate) |
| [1.3 Bayesian optimization](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.3-bayesian-optimization.html) | [`3-bayesian-optimization`](https://github.com/ACC-HelloWorld/3-bayesian-optimization) | [generate](https://github.com/ACC-HelloWorld/3-bayesian-optimization/generate) |
| [1.4 hardware/software comms](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.4-hardware-software-communication.html) | [`4-hardware-software-communication`](https://github.com/ACC-HelloWorld/4-hardware-software-communication) | [generate](https://github.com/ACC-HelloWorld/4-hardware-software-communication/generate) |
| [1.5 data logging](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.5-data-logging.html) | [`5-data-logging`](https://github.com/ACC-HelloWorld/5-data-logging) | [generate](https://github.com/ACC-HelloWorld/5-data-logging/generate) |
| [1.6 connecting the pieces](https://ac-microcourses.readthedocs.io/en/latest/courses/hello-world/1.6-connecting-the-pieces.html) | [`6-connecting-the-pieces`](https://github.com/ACC-HelloWorld/6-connecting-the-pieces) | [generate](https://github.com/ACC-HelloWorld/6-connecting-the-pieces/generate) |

### Other courses

| Org | Public templates |
| --- | --- |
| [ACC-DataScience](https://github.com/ACC-DataScience) | [`1-single-objective-bo`](https://github.com/ACC-DataScience/1-single-objective-bo), [`2-multi-objective-bo`](https://github.com/ACC-DataScience/2-multi-objective-bo), [`3-batch-opt`](https://github.com/ACC-DataScience/3-batch-opt), [`4-featurization`](https://github.com/ACC-DataScience/4-featurization), [`5-multi-task`](https://github.com/ACC-DataScience/5-multi-task), [`6-benchmarking`](https://github.com/ACC-DataScience/6-benchmarking) |
| [ACC-SoftwareDev](https://github.com/ACC-SoftwareDev) | [`4.4-Unit-testing`](https://github.com/ACC-SoftwareDev/4.4-Unit-testing), [`python-refresher`](https://github.com/ACC-SoftwareDev/python-refresher) |
| [ACC-Robotics](https://github.com/ACC-Robotics) | [`python-refresher`](https://github.com/ACC-Robotics/python-refresher) (plus two `python-refresher-<hash>` copies, most likely Classroom leftovers) |
| [ACC-DesignProject](https://github.com/ACC-DesignProject) | none visible |

This inventory is what is **publicly visible**. The AC describes these as private assignment repos,
so an org may hold more that only members can see — ask the AC if a module you want is missing.

## Making your own copy

### Web UI

1. Open the template repo and click **Use this template → Create a new repository** (or use the
   Generate link above, which is the same thing — `…/generate`).
2. Pick an owner. Your personal account is fine; use an org if the work should be shared.
3. Name it, set **Private** unless you want it public, and click **Create repository**.

A template copy is not a fork: it has no upstream link and starts with a single clean commit, which
is what you want for coursework.

### `gh` CLI

```bash
gh repo create my-blink-and-read \
  --template ACC-HelloWorld/2-blink-and-read \
  --private --clone
```

Swap `--private` for `--public` as needed. Drop `--clone` if you only want it on GitHub — which is
the case if you are going straight to a Codespace.

## Opening a Codespace

Every template carries a `.devcontainer` (Python 3.10-bullseye) whose `postCreateCommand` runs
`pip3 install --user -r requirements.txt`, and which preinstalls the Python, Pylance and GitHub
Actions VS Code extensions. So the environment builds itself — no local Python setup.

### Web UI

On **your copy** (not the template): **Code ▾ → Codespaces → Create codespace on main**. First boot
takes a minute or two while the image builds and requirements install. You land in VS Code in the
browser at `https://<generated-name>.github.dev/`. The README preview opens on its own.

### `gh` CLI

```bash
gh codespace create -r <your-username>/my-blink-and-read -b main
gh codespace code -w          # open in the browser
```

### Things worth knowing

- **Create the Codespace on your copy.** Starting one on the AC's template gives you a scratch
  environment you cannot push from.
- **Quota.** Personal accounts get 120 core-hours/month and 15 GB-month storage on GitHub Free
  (180 and 20 GB-month on Pro). On a 2-core machine 120 core-hours is 60 wall-clock hours. Without
  a payment method on file, usage is simply blocked when the quota is gone — no surprise bill.
  The AC previously covered this through GitHub Education, which is no longer in the picture.
- **Codespaces stop after 30 minutes idle** by default. Stopped ones keep their disk; stop them
  yourself (`gh codespace stop`) to avoid burning the quota.
- **You are not locked into Codespaces.** Clone the repo and open it in local VS Code, PyCharm or
  a plain venv — `pip install -r requirements.txt` is the whole setup. The course docs say the same.

## Caveats carried over from Classroom

- **Autograding still runs, but it is deprecated.** Each template has
  `.github/workflows/classroom.yml` using `classroom-resources/autograding-command-grader@v1` and
  `autograding-grading-reporter@v1`. Those action repos are still published and unarchived, so the
  workflow resolves and the `pytest` steps still execute in Actions — but the reporter's README now
  carries a deprecation warning, and there is no Classroom left to sync a grade to. **Treat
  `pytest` as the source of truth**: run it in the Codespace terminal and read the result yourself.
- **The "course identifier" no longer exists.** `1-running-the-demo` asks you to hardcode the
  Classroom student identifier (e.g. `funky-zebra`) into `course_identifier.py` and the demo's
  `main.py`. Classroom issued those; now just pick your own string and keep the two consistent.
- **The hardware modules need hardware.** 1.2, 1.4, 1.5 and 1.6 assume a Pico W plus the CLSLab:Light
  build; 1.4/1.5 also want HiveMQ and MongoDB Atlas credentials. The Codespace covers the software
  half only. This repo's own `CLAUDE.md` documents our Pico W, HiveMQ and Atlas setup.
- **Grades and quizzes were on Quercus/Canvas**, not in these repos. The self-report quizzes the
  orientation pages refer to are only available to enrolled UofT participants.

## References

- [AC Microcourses docs](https://ac-microcourses.readthedocs.io/en/latest/) · [ac-microcourses repo](https://github.com/AccelerationConsortium/ac-microcourses)
- [GitHub Classroom deprecated — changelog, 27 Aug 2026](https://github.blog/changelog/2026-08-27-github-classroom-deprecated/)
- [Classroom sign-ups closed — changelog, 26 May 2026](https://github.blog/changelog/2026-05-26-github-classroom-sign-ups-are-no-longer-available/)
- [Farewell discussion + partner alternatives (Codio, Classroom50)](https://github.com/orgs/community/discussions/205975)
- [Creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)
- [Creating a codespace for a repository](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository)

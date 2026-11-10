# Asset Inventory

An IT asset inventory manager written in Python, using object-oriented programming. It tracks equipments and vulnerabilities through a terminal menu, links each vulnerability to the equipments it affects, and estimates the risk of each equipment with a linear-algebra model.

Second graded assignment (sprints 3, 4 and 5) for the Cybersecurity course — School of Electrical Engineering, UFU, 2026/2. The first assignment is preserved in the tag [`trabalho-1`](../../tree/trabalho-1).

## Assignment 2 requirements

| # | Requirement | Weight | Status |
| --- | --- | --- | --- |
| 1 | Each asset is an object of an equipment class hierarchy | 20% | Done |
| 2 | Data stored as a JSON array of objects | 20% | Done |
| 3 | Application running in a Docker container for 24 hours | 45% | Done: ran for 24 hours on the course server (see [Deployment](#deployment-on-the-course-server)) |
| 4 | Effective risk of each equipment computed with a linear model | 15% | Done |

## Features

- **Equipments:** create, list, show, update and delete. Search by ID or by name (case-insensitive)
- **Vulnerabilities:** create, list, update (description, category, CVSS and status) and delete
- **Links:** link and unlink a vulnerability to an equipment, and list the vulnerabilities of an equipment
- **Validation** while typing, asking again instead of losing what was already typed:
  - IDs must be positive integers and unique
  - Equipment names must be unique (ignoring case) and cannot contain only digits, so a search by name is never ambiguous or confused with an ID
  - CVSS must be a number between 0.0 and 10.0
  - Linking an already linked vulnerability, or unlinking one that is not linked, is rejected
- **Referential integrity:** deleting a vulnerability also unlinks it from every equipment; deleting an equipment keeps the vulnerabilities, since they may affect other equipments
- **Confirmation** before any deletion
- Clean exit with `Ctrl+C` or `Ctrl+D`
- **Dependencies:** register that one equipment inherits a fraction of another equipment's risk, remove and list them
- **Risk report:** own risk and effective risk of every equipment, highest first, with the condition number of the system
- **Persistence:** everything is saved to JSON files after each successful change and loaded again when the program starts
- **Menu organized in submenus:** Equipments, Vulnerabilities, Links, Dependencies and Risk report
- **Logging:** every operation is recorded in `data/app.log` with time, level and origin

## How to run

Requirement: Python 3.10 or newer.

```bash
git clone https://github.com/larasoaresm2/Asset-Inventory.git
cd Asset-Inventory
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

The data is saved in the `data/` folder (created on the first save and ignored by Git). To start from the scenario solved by hand in the [Risk model](#risk-model) section, copy the example files before running:

```bash
mkdir -p data
cp examples/*.json data/
python3 main.py        # option 16 shows x = [8.98, 14.8, 7.45]
```

To run the tests and the style checks (the same ones the GitHub Actions workflow runs on every push):

```bash
pip install -r requirements-dev.txt
pytest
flake8 .
black --check .
```

## Run with Docker

Requirement: Docker with the Compose plugin (Docker Desktop on macOS or Windows, Docker Engine on Linux).

```bash
git clone https://github.com/larasoaresm2/Asset-Inventory.git
cd Asset-Inventory
docker compose up -d --build     # build the image and start the container in the background
docker compose ps                # after about a minute the status shows (healthy)
```

The container is named `trab02_2026_2_12621cbs221` (S5_20 convention: `trab02_2026_2_MATRICULA`, lowercase). The menu runs inside it and waits for input:

```bash
docker compose attach asset-inventory    # press Enter to show the menu
```

To leave the menu **without stopping the program**, press `Ctrl+P` and then `Ctrl+Q` (in the VS Code terminal, which captures `Ctrl+P`, use `docker compose attach --detach-keys="ctrl-x" asset-inventory` and leave with `Ctrl+X`).

| Task | Command |
| --- | --- |
| See the application log | `docker compose exec asset-inventory tail -n 20 data/app.log` |
| See what the menu printed | `docker compose logs --tail 20` |
| Update after a `git pull` | `docker compose up -d --build` |
| Stop on purpose | `docker compose stop` |
| Remove the container (data is kept) | `docker compose down` |

**Never run `docker compose down -v`:** the `-v` also deletes the volume, and with it all the data.

### How the container is built

| Decision | Where | Why |
| --- | --- | --- |
| `python:3.12-slim` base image | `Dockerfile` | Smaller image and fewer installed programs, so less attack surface |
| `requirements.txt` copied and installed before the code | `Dockerfile` | Layer cache: changing the code does not reinstall NumPy |
| NumPy version pinned | `requirements.txt` | Every build, here or on the server, gets the same library |
| Runs as `appuser`, not `root` | `Dockerfile` | Least privilege: the container shares the host kernel, so an exploited program must not be root |
| `HEALTHCHECK` | `Dockerfile` | Every minute Docker checks that the saved data still loads through the `Inventory` rules; the status shows as `healthy` or `unhealthy` |
| `.dockerignore` | `.dockerignore` | Keeps `data`, `.git`, `.venv` and test files out of the image |
| Named volume `asset-data` mounted at `/app/data` | `compose.yaml` | The JSON files and the log survive when the container is removed or rebuilt |
| `stdin_open` and `tty` | `compose.yaml` | Keep the interactive menu waiting for input instead of exiting |
| `restart: unless-stopped` | `compose.yaml` | If the program ends or the server reboots, Docker starts it again, unless someone stopped it on purpose |
| Docker log rotation (3 × 1 MB) | `compose.yaml` | The screen output kept by Docker never fills the disk |
| `LOG_LEVEL` variable | `compose.yaml` | Log level set from the environment or a `.env` file (default `INFO`) |

Tested locally: the container stays `healthy`; choosing *Exit* in the menu makes Docker restart it (`RestartCount` 1); after `docker compose down` and `up`, the registered equipments are still there.

## Deployment on the course server

The course server is a virtual machine (KVM) provided by the university: Ubuntu 26.04 LTS, reachable only from the university network at a private IP address and shared by the whole class. Docker 29 and Docker Compose 2.40 were already installed, running and enabled at boot.

### Steps

1. **SSH key instead of password.** A key pair was generated on the laptop (`ssh-keygen -t ed25519`), the public key was copied to the server (`ssh-copy-id`), and an alias in `~/.ssh/config` makes the connection `ssh ufu`. The default password was changed on the first login.
2. **Docker without `sudo`.** The user was added to the `docker` group (`sudo usermod -aG docker $USER`). Members of this group can control the whole machine through Docker, so it is as sensitive as `sudo`; the user already had `sudo`, so no privilege was added.
3. **Clone into a folder named with the project identifier** (`trab02_2026_2_MATRICULA`, as required by S5_20). The `name:` in `compose.yaml` keeps the Compose project, volume and network names unique on the shared server:

   ```bash
   git clone https://github.com/larasoaresm2/Asset-Inventory.git ~/trab02_2026_2_12621cbs221
   cd ~/trab02_2026_2_12621cbs221
   docker compose up -d --build
   ```

4. **Restart test without disturbing other users.** Rebooting the server or changing its firewall would affect the whole class, so only this container was restarted (`docker compose restart`). Surviving a server reboot is guaranteed by Docker being enabled at boot and by `restart: unless-stopped`.
5. **Firewall.** `ufw` is inactive on the server and was not changed, because it is shared. If it were enabled, only port 22 (SSH) would need to be open: the application does not listen on any port.

### 24-hour run

This first run used the old container name `trab_02_12621CBS221`, before the S5_20 naming convention.

The container started on 2026-11-05 at 23:59:41 UTC (20:59 in Brasília) and was checked on 2026-11-06 at 21:21 (Brasília):

```
$ docker compose ps
NAME                  IMAGE             COMMAND            SERVICE           CREATED        STATUS                  PORTS
trab_02_12621CBS221   asset-inventory   "python main.py"   asset-inventory   24 hours ago   Up 24 hours (healthy)

$ docker inspect --format "{{.State.StartedAt}} restarts={{.RestartCount}}" trab_02_12621CBS221
2026-11-05T23:59:41.124911768Z restarts=0

$ docker compose exec asset-inventory grep -c "Application started" data/app.log
2
```

- **Up 24 hours (healthy)** with **0 restarts**: the program ran without interruption and the data loaded correctly at every health check
- The two starts in the log are the first `up` and the manual restart test, both before the 24 hours began
- The complete log of the run is in [`docs/evidence/app-24h.log`](docs/evidence/app-24h.log)

To bring the application up again on the server (for example, on the day of the presentation):

```bash
ssh ufu
cd ~/trab02_2026_2_12621cbs221
git pull
docker compose up -d --build
```

## Logging

The application writes to `data/app.log` (inside the volume, so it survives the container):

```
2026-11-05T22:42:56Z INFO main: Application started
2026-11-05T22:42:56Z INFO main: Loaded 1 equipments, 0 vulnerabilities and 0 dependencies
2026-11-05T22:43:52Z INFO asset_inventory.menu: list_equipments done
2026-11-05T22:44:06Z WARNING asset_inventory.menu: show_equipment refused: Equipment not found.
```

- **Levels:** `INFO` for operations that worked, `WARNING` for operations refused by the rules, `ERROR` when the saved data cannot be loaded, and the full traceback for unexpected errors
- **Times in UTC** (the `Z`), the usual choice on servers
- **Rotation:** the file is rotated at 1 MB and three old files are kept
- **No personal data:** the log records counts and operation names, never owners or other personal fields (LGPD)
- Every start and stop is logged, so automatic restarts and the 24-hour run can be checked in the log

## Data files

Each file in `data/` is a JSON array of objects. Equipments store their subclass in `"type"`, so the right class is rebuilt when loading, and refer to vulnerabilities by ID instead of copying them:

```json
[
  {
    "type": "Notebook",
    "id": 1,
    "name": "E1",
    "owner": "Lara",
    "location": "Lab",
    "description": "hand-solved scenario",
    "vulnerability_ids": [1]
  }
]
```

| File | Content |
| --- | --- |
| `equipments.json` | Equipments, with their type and the IDs of their vulnerabilities |
| `vulnerabilities.json` | Vulnerabilities, with CVSS and status (`"OPEN"`, `"FIXED"`...) |
| `dependencies.json` | Dependencies: `dependent_id`, `source_id` and `fraction` (matrix `A`) |

- **Loading goes through the business rules.** Every object is rebuilt and added with the same `Inventory` methods the menu uses, so a file edited by hand with a repeated ID, a CVSS of 12 or a link to a missing vulnerability is refused.
- **Broken files are reported, never overwritten.** A missing or empty file means an empty list; a malformed file, a file that is not an array or a missing field stops the program with a message naming the file.
- **Atomic writes.** Each file is written to a temporary `.tmp` file and then swapped in with `os.replace`, so a crash in the middle of a save never leaves a half-written file.
- **UTF-8.** Files are written with `ensure_ascii=False`, so accented names are stored as they are.

## Class design

```
Equipment (base class)
├── Server
├── Notebook
├── Router
├── WebApplication
└── Database

Vulnerability ── Status (Enum)

Inventory ── has many ──> Equipment, Vulnerability, Dependency
RiskAnalysis ── reads ──> Inventory
JsonStorage ── saves and loads ──> Inventory
Menu ── uses ──> Inventory, RiskAnalysis, JsonStorage
```

| Class | File | Responsibility |
| --- | --- | --- |
| `Equipment` and subclasses | `asset_inventory/equipment.py` | One IT asset: ID, name, owner, location, description and the IDs of the vulnerabilities that affect it |
| `Vulnerability` | `asset_inventory/vulnerability.py` | One security weakness: ID, description, category, CVSS score and status. Validates the CVSS score |
| `Status` | `asset_inventory/enums.py` | Remediation status: OPEN, IN_PROGRESS, FIXED, RISK_ACCEPTED |
| `Inventory` | `asset_inventory/inventory.py` | Stores all objects and enforces the business rules (unique IDs and names, links, integrity) |
| `Dependency` | `asset_inventory/dependency.py` | One entry of the dependency matrix: the dependent equipment inherits a fraction of the source equipment's risk |
| `RiskAnalysis` | `asset_inventory/risk.py` | Builds the matrices with NumPy, checks that the system can be solved and computes own and effective risk |
| `Menu` | `asset_inventory/menu.py` | The only class that talks to the user (`print` and `input`) |
| `JsonStorage` | `asset_inventory/storage.py` | Saves the inventory to JSON files and loads it back through the `Inventory` rules (Repository pattern) |
| — | `asset_inventory/helpers.py` | Input functions: `read_text()`, `read_int()`, `read_float()`, `choose_from_list()`, `ask_yes_no()` |
| — | `asset_inventory/log_config.py` | `setup_logging()`: rotating log file in `data/app.log` |
| — | `main.py` | Entry point: sets up logging, loads the data, then creates the `Menu` |

### Object-oriented concepts used

- **Inheritance:** each equipment type is a subclass of `Equipment` and reuses all its attributes and methods
- **Polymorphism:** every subclass overrides `exposure_factor()`, which weights the equipment's own risk. The menu creates any type through the same call, `equipment_class(...)`
- **Composition:** `Inventory` *has* equipments, vulnerabilities and dependencies; `Menu` *has* an `Inventory`; `RiskAnalysis` *reads* an `Inventory`
- **Factory:** `equipment_from_dict()` reads the `"type"` saved in the JSON and creates an object of the matching subclass
- **Encapsulation of rules:** validation lives in `Inventory` and `Vulnerability`, so it protects the data whatever the source (menu today, JSON file and web API later). The menu validates again while typing only to improve the user experience (defense in depth)

### Exposure factor by equipment type

| Type | Factor | Rationale |
| --- | --- | --- |
| `WebApplication` | 1.5 | Exposed to the internet by design |
| `Router` | 1.3 | Sits on the network perimeter, reachable from outside |
| `Server` | 1.2 | Exposes network services to many clients |
| `Notebook` | 1.0 | Reference value |
| `Database` | 0.8 | Should not be directly reachable; its risk arrives through the applications that depend on it |

The factor measures **exposure** only. How risk spreads from one equipment to another is modeled separately by the dependency matrix of the risk model, so it is not counted twice.

## Risk model

For *n* equipments and *m* active vulnerabilities (status OPEN or IN_PROGRESS; FIXED and RISK_ACCEPTED do not add risk):

| Element | Size | Meaning |
| --- | --- | --- |
| `M` | n × m | Incidence matrix: `M[i][j] = 1` if equipment *i* has vulnerability *j* |
| `v` | m | Severity vector: CVSS score of each vulnerability |
| `F` | n × n | Diagonal matrix with the exposure factor of each equipment |
| `A` | n × n | Dependency matrix: `A[i][j]` is the fraction of the risk of equipment *j* inherited by equipment *i* |

```
Own risk:        b = F · M · v
Effective risk:  x = b + A · x   ⟺   (I − A) · x = b
```

**Why the system always has a solution.** When a dependency is registered, the sum of each row of `A` must stay below 1 (and `A[i][i] = 0`). Then `I − A` is strictly diagonally dominant, and therefore invertible.

**Numerical check before solving.** The program computes the condition number of `I − A` with `numpy.linalg.cond` and refuses to solve when it is infinite or above 10¹². The determinant is shown only for comparison: in floating point it is almost never exactly zero, so the condition number is the reliable test.

**Solving.** `numpy.linalg.solve(I − A, b)`, which is more precise and faster than computing the inverse.

### Validation by hand

Three `Notebook` equipments (exposure factor 1.0, so `b = M · v`), vulnerabilities V1 = 7.5, V2 = 5.0 and V3 = 9.8:

- E1 has V1; E2 has V2 and V3; E3 has none → `b = [7.5, 14.8, 0]`
- E1 inherits 0.1 of E2; E3 inherits 0.5 of E1 and 0.2 of E2 (row sums 0.1, 0 and 0.7)
- By hand: x₂ = 14.8; x₁ = 7.5 + 0.1 · 14.8 = 8.98; x₃ = 0 + 0.5 · 8.98 + 0.2 · 14.8 = 7.45

The program's risk report gives the same result:

```
Condition number of I - A: 1.728 (determinant: 1)
  ID  Equipment            Type             Own risk  Effective
   2  E2                   Notebook            14.80      14.80
   1  E1                   Notebook             7.50       8.98
   3  E3                   Notebook             0.00       7.45
```

## Development

Each stage is developed in its own branch and merged into `main` through a pull request.

| Branch | Content |
| --- | --- |
| `feature/base`, `feature/assets`, `docs/readme`, `refactor/clean-comments`, `docs/update-after-refactor` | Assignment 1 (see tag `trabalho-1`) |
| `refactor/oop-models` | Rewrite in object-oriented programming: classes, inheritance, polymorphism and the new menu |
| `feat/risk-analysis` | Dependencies between equipments and the risk model with NumPy |
| `test/quality-ci` | Tests with pytest, formatting with black, linting with flake8 and the GitHub Actions workflow |
| `feat/json-storage` | JSON persistence: `to_dict`/`from_dict`, `JsonStorage`, example files and storage tests |
| `refactor/menu-submenus` | Main menu with submenus and one generic menu loop |
| `feat/docker` | Dockerfile, `.dockerignore`, `compose.yaml`, pinned dependencies and logging |

Sprint 3 study exercises are in the [sprint3](https://github.com/larasoaresm2/sprint3) repository.

## Author

Lara Soares — Federal University of Uberlândia
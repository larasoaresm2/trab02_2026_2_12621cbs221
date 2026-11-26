# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-11-26

Version delivered for Assignment 2 (Cybersecurity, UFU, 2026/2).

### Added

- Object-oriented model: `Equipment` with five subclasses and a polymorphic `exposure_factor()`, `Vulnerability`, `Dependency` and `Inventory` with the business rules (#4)
- Risk model with NumPy: own risk `b = F·M·v` and effective risk from `(I − A)·x = b`, with a condition-number check before solving (#5)
- Tests with pytest, formatting with black, linting with flake8 and a GitHub Actions workflow (#6)
- JSON persistence: three files with arrays of objects, validation through the `Inventory` rules and atomic writes (#7)
- Docker image, `.dockerignore`, `compose.yaml` with a named volume, `restart: unless-stopped`, healthcheck and log rotation; application log in `data/app.log` (`feat/docker`)
- Deployment on the course server and evidence of the first 24-hour run (#10)
- Read-only HTTP API (`/health`, `/v1/equipments`, `/v1/vulnerabilities`, `/v1/risk`) with Problem Details errors, served by Gunicorn as a second Compose service on port 2221 (#13)
- Requirement-to-code table, API documentation and evidence of the second 24-hour run (4 days, 0 restarts) (#14)
- Read-only web interface served by the API, with summary, risk report, equipments and vulnerabilities (#16)
- Type hints on the domain classes and `mypy` in the CI

### Changed

- Main menu reorganized into submenus with one generic menu loop (#8)
- Project, container, image and repository renamed to `trab02_2026_2_12621cbs221` (course convention S5_20) (#11, #12)

### Security

- Containers run as a non-root user, with `no-new-privileges` and `cap_drop: ALL`; the API mounts the data volume read-only (#13)
- `pip-audit` in the CI; Debian security patches applied at build time, reducing the image's high vulnerabilities from 7 to 4 (#15)
- Web page protected against XSS (`textContent`) and served with Content Security Policy, `X-Content-Type-Options` and `Referrer-Policy` headers (#16)

## [trabalho-1] - 2026-09-25

Assignment 1: procedural version of the asset inventory with a terminal menu.

[1.0.0]: https://github.com/larasoaresm2/trab02_2026_2_12621cbs221/compare/trabalho-1...v1.0.0
[trabalho-1]: https://github.com/larasoaresm2/trab02_2026_2_12621cbs221/releases/tag/trabalho-1

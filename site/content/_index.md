---
title: libfprint-plus
---

# libfprint-plus

Fingerprint reader support that Fedora, RHEL-family and SUSE do not ship, packaged as signed RPMs.

## Supported readers

| Reader | USB ID | Status |
|---|---|---|
| Goodix Fingerprint Sensor | `27c6:538d` | Builds and passes emulated tests on Fedora 44. Hardware testing in progress. |
| Chipsailing CS9711 | `2541:0236` | Planned. Driver not merged yet. |

More readers will be added over time, which is why the project is not named after one device.

## Status

This project is pre-release. No repository is published yet, and nothing here should be installed on a machine you depend on. See [Install](install/) for what exists today and [Security](security/) for how packages are built and signed.

## Where the code comes from

We build from upstream sources and publish our changes as a visible patch series, not as a bundled fork. The source of every package is pinned by version and checksum in the project repository.

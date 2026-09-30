---
title: Install
---

# Install

No repository is published yet. This page will describe the supported ways to install once one is.

## Planned

- **Fedora Workstation and Server:** enable the repository, then `dnf install` the package for your reader.
- **Fedora Atomic (Silverblue, Kinoite, Bazzite):** layer or override with `rpm-ostree`.
- **RHEL, Rocky, AlmaLinux 10:** the same repository layout, built against your release.
- **openSUSE and SLES:** a zypper repository.

Until then, the [source repository]({{< param repo >}}) documents how to build the packages yourself.

## Verify before you install

Every package and repository will be signed. See [Security](../security/) for the key and how to check it.

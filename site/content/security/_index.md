---
title: Security
---

# Security

## Signing key

Packages and repository metadata are signed with an Ed25519 key.

| | |
|---|---|
| Fingerprint | `{{< param signingKeyFingerprint >}}` |
| Public key | [RPM-GPG-KEY-libfprint-plus](../keys/RPM-GPG-KEY-libfprint-plus) |
| Purpose | Signing RPM packages only |

Check the fingerprint here against the one in the [source repository]({{< param repo >}}) before you trust the key. Import it with `sudo rpm --import` on the downloaded file.

## How packages are built

- Sources are fetched only from allowlisted upstream hosts, pinned by version and checked against a SHA-256.
- Every change is a signed commit and is scanned for secrets, known vulnerabilities and code-quality problems before it is pushed.
- Builds run on a schedule against the current Fedora updates, so a broken or patched dependency shows up before users hit it.

## What signing does not tell you

A signature shows a package came from the project and was not altered. It says nothing about whether the driver code is free of bugs. Fingerprint drivers run in a root service and parse data from a USB device, so treat them as sensitive code.

# Security Policy

## Supported Versions

Only the latest release of ChunkLab receives security fixes.

| Version | Supported |
|---------|-----------|
| 0.2.x (latest) | ✅ |
| < 0.2.0 | ❌ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues.**

To report a vulnerability, email **https://github.com/ziffan/ChunkLab/security/advisories/new** with:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept if available)
- Affected version(s)

You can expect an acknowledgement within **72 hours** and a resolution timeline within **14 days** for confirmed issues.

## Scope

This policy covers the ChunkLab application code in this repository. Third-party dependencies (pip packages, npm packages) are out of scope for direct reporting — please report those to the upstream projects. ChunkLab uses `pip-audit` and `npm audit` in CI to track dependency vulnerabilities.

## Disclosure

We follow coordinated disclosure. Once a fix is available, we will publish a GitHub Security Advisory and credit the reporter (unless anonymity is requested).

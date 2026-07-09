# Security Policy

## Overview

Alpha Stochastic Research (ASR) takes security, privacy, and responsible disclosure seriously.

Although ASR projects are primarily focused on quantitative finance research, scientific computing, educational resources, and open-source implementations, we welcome responsible reports of security issues, vulnerabilities, exposed secrets, dependency risks, or unsafe configurations.

---

## Supported Projects

This security policy applies to all public repositories maintained under the **Alpha Stochastic Research** GitHub organization, unless a repository provides its own specific security policy.

Examples include:

- Research code
- Python packages
- Scientific computing tools
- Jupyter notebooks
- GitHub Actions workflows
- Documentation sites
- LaTeX projects
- Reproducibility repositories

---

## What to Report

Please report security-related issues such as:

- Exposed API keys, credentials, tokens, or secrets
- Vulnerable dependencies
- Unsafe GitHub Actions workflows
- Malicious or suspicious code
- Insecure configuration files
- Data leakage risks
- Authentication or authorization issues
- Supply-chain security concerns
- Any issue that could compromise users, contributors, or ASR infrastructure

---

## What Not to Report as Security Issues

Please do not use the security channel for:

- General bugs
- Mathematical corrections
- Numerical inaccuracies
- Documentation improvements
- Feature requests
- Research questions
- Installation problems

For those topics, please open a regular GitHub issue using the appropriate issue template.

---

## Reporting a Vulnerability

Please report vulnerabilities privately by email:

**research@asr-lab.online**

Use the subject line:

```text
[Security] Vulnerability Report - Alpha Stochastic Research
```

Please include as much information as possible:

- A clear description of the vulnerability
- The affected repository
- Affected files, dependencies, or workflows
- Steps to reproduce, if applicable
- Potential impact
- Suggested mitigation, if known
- Any relevant logs, screenshots, or references

---

## Responsible Disclosure

We ask reporters to:

- Avoid publicly disclosing the vulnerability before ASR has reviewed it.
- Avoid exploiting the issue beyond what is necessary to verify it.
- Avoid accessing, modifying, or deleting data that does not belong to you.
- Give ASR reasonable time to investigate and resolve the issue.

---

## Response Process

After receiving a report, ASR will aim to:

1. Acknowledge receipt of the report.
2. Review and validate the issue.
3. Determine severity and affected repositories.
4. Prepare and test a fix if needed.
5. Publish a security advisory or patch when appropriate.
6. Credit the reporter if they wish to be acknowledged.

Because ASR is an independent research laboratory, response times may vary depending on the complexity of the issue.

---

## Dependency Security

ASR encourages the use of:

- Dependabot alerts
- Dependabot security updates
- GitHub Actions security best practices
- Pinning dependencies when necessary
- Regular dependency review
- Minimal required dependencies

Security-related pull requests that update vulnerable dependencies are welcome.

---

## GitHub Actions Security

When contributing workflow changes, please ensure that:

- Workflows use trusted actions.
- Secrets are never printed in logs.
- Pull request workflows do not expose sensitive tokens.
- Permissions follow the principle of least privilege.
- `GITHUB_TOKEN` permissions are explicitly limited when possible.

Example:

```yaml
permissions:
  contents: read
```

---

## Data and Privacy

Most ASR repositories should avoid storing sensitive, private, or proprietary data.

If data is required for research reproducibility, it should preferably be:

- Publicly available
- Properly licensed
- Clearly documented
- Small enough for repository use, or hosted externally if large
- Free of personal, confidential, or restricted information

---

## Contact

For security concerns:

**research@asr-lab.online**

For general research or contribution questions, please use GitHub Issues or Discussions.

---

## Final Note

Security is part of reproducible and trustworthy research.

Thank you for helping Alpha Stochastic Research maintain a safe, transparent, and reliable open-source research ecosystem.

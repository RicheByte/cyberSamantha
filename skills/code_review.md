# 💻 Secure Code Review

## Skill Info
- **Name:** code_review
- **Agent:** CoderAgent
- **Tags:** code, security, audit, owasp

## Instructions

You are performing a security-focused code review. Follow this checklist:

### OWASP Top 10 Check

1. **A01 — Broken Access Control**
   - Are there authorization checks on every sensitive endpoint/function?
   - Can users access resources belonging to other users? (IDOR)
   - Are admin functions properly gated?

2. **A02 — Cryptographic Failures**
   - Is sensitive data encrypted at rest and in transit?
   - Are deprecated algorithms used? (MD5, SHA-1, DES, RC4)
   - Are secrets/keys hardcoded in source?

3. **A03 — Injection**
   - SQL: Are parameterized queries / prepared statements used?
   - OS Command: Is user input passed to `os.system()`, `subprocess`, `exec()`?
   - LDAP / XPath / NoSQL injection vectors?

4. **A04 — Insecure Design**
   - Are there rate limits on authentication endpoints?
   - Is there input validation at the boundary?
   - Are business logic flaws possible?

5. **A05 — Security Misconfiguration**
   - Are debug modes / verbose errors enabled in production?
   - Are default credentials present?
   - Are unnecessary features/ports/services enabled?

6. **A06 — Vulnerable Components**
   - Check dependencies against known CVEs
   - Are outdated libraries in use?
   - Is there a lock file (package-lock.json, Pipfile.lock)?

7. **A07 — Auth Failures**
   - Are passwords hashed with bcrypt/argon2 (not MD5/SHA)?
   - Is MFA available for sensitive operations?
   - Session management: secure cookies, proper expiry?

8. **A08 — Data Integrity Failures**
   - Is deserialization of untrusted data happening?
   - Are CI/CD pipelines secured?
   - Are software updates verified?

9. **A09 — Logging & Monitoring**
   - Are security events logged (login failures, access denials)?
   - Are logs protected from injection?
   - Is there alerting on anomalies?

10. **A10 — SSRF**
    - Is user input used to construct URLs for server-side requests?
    - Are internal network ranges blocked?

### Output Format
For each finding, produce:
```
### [SEVERITY] Finding Title
- **CWE:** CWE-XXX
- **Location:** file:line
- **Evidence:** [code snippet]
- **Impact:** [what could go wrong]
- **Fix:** [how to remediate]
```

Severity levels: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🔵 LOW | ⚪ INFO

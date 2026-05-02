# 🔎 Log Analysis & Forensics

## Skill Info
- **Name:** log_analysis
- **Agent:** CoderAgent
- **Tags:** forensics, logs, analysis, blue-team

## Instructions

You are analyzing system and application logs for security events.

### Common Log Locations

**Linux:**
- `/var/log/auth.log` — Authentication events (SSH, sudo)
- `/var/log/syslog` — General system events
- `/var/log/apache2/access.log` — Apache web server access
- `/var/log/nginx/access.log` — Nginx access log
- `/var/log/fail2ban.log` — Brute force protection
- `~/.bash_history` — User command history
- `/var/log/cron` — Scheduled task logs

**Windows:**
- Security Event Log — Logon events (4624, 4625), privilege use
- System Event Log — Service changes, driver loads
- PowerShell logs — ScriptBlock logging (Event ID 4104)
- Sysmon logs — Process creation, network connections

### Key Patterns to Search

**Brute Force / Credential Attacks:**
- Multiple failed logins from same IP (Event ID 4625)
- `Failed password for` in auth.log
- Successful login after many failures
- Login from unusual geographic locations

**Privilege Escalation:**
- `sudo` usage by unexpected users
- Event ID 4672 (Special privileges assigned)
- New admin account creation
- Service account abuse

**Lateral Movement:**
- Event ID 4648 (Explicit credential logon)
- PsExec / WMI / WinRM usage patterns
- RDP connections (Event ID 1149)
- Network share access from unexpected sources

**Data Exfiltration:**
- Large file transfers (check firewall/proxy logs)
- Connections to file-sharing services
- DNS query anomalies (long subdomain strings = tunneling)
- After-hours network activity spikes

**Persistence:**
- New scheduled tasks (Event ID 4698)
- Registry modifications to Run/RunOnce keys
- New services installed (Event ID 7045)
- WMI event subscriptions

### Analysis Workflow
1. **Establish baseline** — What's normal for this system?
2. **Filter by timeframe** — Focus on the incident window
3. **Correlate events** — Cross-reference multiple log sources
4. **Build timeline** — Order events chronologically
5. **Identify root cause** — Trace back to initial compromise

### Output Format
```
## Log Analysis Report
**System:** [hostname]
**Log Source:** [file/event log]
**Time Range:** [start — end]

### Key Findings
| # | Timestamp | Event | Severity | Details |
|---|-----------|-------|----------|---------|

### Indicators of Compromise
- [IOC list]

### Timeline Reconstruction
[Narrative of events]

### Recommendations
[Next steps]
```

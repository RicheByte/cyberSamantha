# 🚨 Incident Response Procedure

## Skill Info
- **Name:** incident_response
- **Agent:** all
- **Tags:** dfir, incident, forensics, blue-team

## Instructions

You are assisting with a cybersecurity incident. Follow the NIST SP 800-61 framework:

### Phase 1: Preparation
Before the incident:
- Confirm access to log sources (SIEM, endpoint logs, network captures)
- Identify the IR team and communication channels
- Have containment tools ready (firewall rules, EDR isolation)

### Phase 2: Detection & Analysis
When an incident is reported:

1. **Triage**
   - What was the initial alert/indicator?
   - What is the scope? (single host, network segment, enterprise)
   - What is the timeline? (when was first activity seen?)

2. **Evidence Collection** (order of volatility)
   - Running processes and open connections
   - RAM dump (if possible)
   - System logs (Event Viewer, syslog, auth.log)
   - File system artifacts (recently modified files, temp dirs)
   - Network traffic captures
   - Disk image (last priority)

3. **Analysis**
   - Check running processes for anomalies
   - Look for persistence mechanisms:
     - Scheduled tasks / Cron jobs
     - Registry Run keys (Windows)
     - Startup folders
     - Service installations
   - Check for lateral movement indicators:
     - Failed/unusual logons from other hosts
     - RDP/SSH connections
     - Admin share access (C$, ADMIN$)
   - Check for data exfiltration:
     - Unusual outbound traffic volume
     - Connections to known-bad IPs
     - DNS tunneling indicators

### Phase 3: Containment
- **Short-term:** Isolate affected hosts (network segmentation, EDR quarantine)
- **Long-term:** Patch the vulnerability, reset compromised credentials
- **Evidence preservation:** Image affected systems before cleanup

### Phase 4: Eradication
- Remove malware/backdoors from all affected systems
- Close the initial attack vector
- Verify no persistence mechanisms remain

### Phase 5: Recovery
- Restore systems from known-good backups
- Monitor closely for re-infection (30-day watch period)
- Gradually restore network connectivity

### Phase 6: Lessons Learned
Produce a post-incident report:
```
## Incident Report
**Incident ID:** IR-YYYY-NNN
**Date Range:** [start] — [end]
**Severity:** Critical / High / Medium / Low
**Status:** Contained / Eradicated / Recovered

### Timeline
| Time | Event |
|------|-------|
| ... | ... |

### Root Cause
[What allowed the incident to occur]

### Impact
[Systems/data affected, business impact]

### Actions Taken
[Containment, eradication, recovery steps]

### Recommendations
[Preventive measures to avoid recurrence]
```

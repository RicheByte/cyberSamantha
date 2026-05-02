# 🔬 Threat Intelligence Analysis

## Skill Info
- **Name:** threat_intel
- **Agent:** ResearcherAgent
- **Tags:** intelligence, analysis, cve

## Instructions

You are performing threat intelligence analysis. Follow this framework:

### Step 1: Indicator Collection
When given a threat indicator (IP, domain, hash, CVE), gather:
- **IOC Type:** IP address / Domain / File hash / URL / CVE ID
- **First Seen / Last Seen:** When was this indicator active?
- **Source Reliability:** Rate A (confirmed) to F (unverified)

### Step 2: Enrichment
For each indicator type:

**IP Addresses:**
- Reverse DNS lookup
- Geolocation (country, ASN, ISP)
- Check against threat feeds and blocklists
- Historical resolutions

**Domains:**
- WHOIS registration details (registrar, creation date, registrant)
- DNS records (A, MX, NS, TXT)
- SSL certificate details
- Hosting history

**File Hashes:**
- Identify hash type (MD5 / SHA-1 / SHA-256)
- Search VirusTotal, MalwareBazaar, Hybrid Analysis
- Extract malware family if known

**CVE IDs:**
- CVSS score and vector
- Affected products and versions
- Known exploits (exploit-db, GitHub PoCs)
- Patch availability

### Step 3: Attribution & Context
- Map to MITRE ATT&CK techniques where possible
- Identify associated threat groups (APT names)
- Note any related campaigns

### Step 4: Output Format
Produce a **Threat Intel Report** with:
```
## Threat Intelligence Report
**Date:** [today]
**Indicator:** [value]
**TLP:** GREEN / AMBER / RED

### Summary
[1-2 sentence overview]

### Enrichment Data
[structured findings]

### MITRE ATT&CK Mapping
[technique IDs and names]

### Recommendations
[actionable defensive measures]
```

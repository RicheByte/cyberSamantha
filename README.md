# CyberSamatha - Cybersecurity RAG System

CyberSamatha is a Retrieval-Augmented Generation (RAG) system designed for cybersecurity professionals. It leverages local documentation and real-time data from multiple cybersecurity sources to provide accurate, context-aware answers to your security questions.

## Overview

This system combines your local cybersecurity documentation with regularly updated data from leading security repositories to create a comprehensive knowledge base. Using Google's Gemini AI, it provides intelligent responses to your queries with proper source citations.

## Features

- **Multi-format Document Support**: Handles PDF, DOCX, PPTX, JSON, YAML, TXT, and MD files
- **Automated Data Updates**: Regularly syncs with top cybersecurity repositories
- **Semantic Search**: Uses vector embeddings for intelligent document retrieval
- **Source Citation**: Provides references to original documents in all responses
- **Interactive CLI**: Natural conversation interface for querying your knowledge base
- **Change Detection**: Only reindexes modified documents to save processing time

## Data Sources

The system automatically maintains updated data from:

- **Awesome Cybersecurity Handbooks**: Comprehensive security guides and references
- **Exploit Database**: Latest exploits and proof-of-concepts
- **GitHub Advisory Database**: Official vulnerability advisories
- **NVD CVE Database**: Common Vulnerabilities and Exposures data

## Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- Git (for data updates)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/RicheByte/cyberSamantha
cd cyberSamantha
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
# Linux/Mac
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Windows PowerShell
"GEMINI_API_KEY=your_api_key_here" | Out-File -Encoding utf8 .env

# Windows CMD
echo GEMINI_API_KEY=your_api_key_here > .env
```

4. Make scripts executable (Linux/Mac only):
```bash
chmod +x ask.sh
```

### Initial Setup

1. Check your setup (cross-platform):
```bash
python setup_check.py
```

2. Update all data sources:
```bash
python update_data.py --update
```

3. Index the documents:
```bash
python cybersamatha.py --index
```

## Usage

### Interactive Mode
Start a conversation with your cybersecurity knowledge base:
```bash
python cybersamatha.py
```

### Single Query
Ask a specific question:
```bash
python cybersamatha.py --question "What are the latest Apache vulnerabilities?"
```

### Fast Query Mode (Optimized)
Use `--quiet` flag for faster execution:
```bash
# Cross-platform
python cybersamatha.py --question "What is XSS?" --quiet

# With ASCII banner
python cybersamatha.py --question "What is XSS?" --quiet --banner

# Quick launchers
./ask.sh "What is XSS?"        # Linux/Mac
.\ask.ps1 "What is XSS?"       # Windows PowerShell
ask.bat "What is XSS?"         # Windows CMD
```

### Force Reindex
Update the vector database with all documents:
```bash
python cybersamatha.py --index --force
```

## Data Management

### Storage Cleanup
Remove large Git pack files to save disk space:
```bash
python cleanup_storage.py --status                    # Show current sizes
python cleanup_storage.py --all                       # Full cleanup (~5.9 GB freed)
python cleanup_storage.py --temp                      # Remove temp packs only
python cleanup_storage.py --all --keep-handbooks      # Keep handbooks updatable
```

### Updating Sources
Update all cybersecurity data repositories:
```bash
python update_data.py --update                        # Update all sources
python update_data.py --update --cleanup              # Update + optimize storage
python update_data.py --status                        # Check current status
```

### Check Status
View current data status:
```bash
python update_data.py --status
```

### Automated Updates
Add to crontab for daily updates (Linux/Mac):
```bash
0 2 * * * cd /path/to/cybersamantha && python update_data.py --update --cleanup
```

Or use Task Scheduler on Windows:
```powershell
# Create a scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "update_data.py --update --cleanup" -WorkingDirectory "C:\path\to\cybersamantha"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "CyberSamantha Update" -Action $action -Trigger $trigger
```

## Project Structure

```
cybersamatha/
├── cybersamatha.py          # Main RAG system
├── update_data.py           # Data updater
├── data/                    # Local documents and fetched data
│   ├── handbooks/           # Cybersecurity handbooks
│   ├── exploits/            # Exploit database
│   ├── advisories/          # Security advisories
│   └── nvdcve/              # CVE database
├── chroma_db/               # Vector database (auto-generated)
├── .env                     # Environment variables
└── README.md
```

## Configuration

### Environment Variables
Create a `.env` file with:
```
GEMINI_API_KEY=your_gemini_api_key
```

### Configuration File
Customize `config.yaml` to control:
- **Data sources**: Enable/disable repos (handbooks, exploits, advisories, nvdcve)
- **Storage**: Auto-cleanup Git history to save disk space
- **RAG settings**: Embedding model, Gemini model, chunk sizes

Example to keep only handbooks (saves ~5.9 GB):
```yaml
data_sources:
  handbooks:
    enabled: true
  exploits:
    enabled: false  # Disable large repos
  advisories:
    enabled: false
  nvdcve:
    enabled: false
```

### Custom Data Sources
Add your own documents to the `data/` directory in any supported format. The system will automatically index them.

## Supported File Formats

- **Text**: TXT, MD
- **Documents**: PDF, DOCX, PPTX
- **Data**: JSON, YAML, YML

## API Integration

- **AI Provider**: Google Gemini
- **Vector Database**: ChromaDB
- **Embeddings**: Google Generative AI Embeddings

## Use Cases

- **Vulnerability Research**: Quick access to CVE details and exploits
- **Security Advisory Lookup**: Find relevant security advisories
- **Procedure Reference**: Access security handbooks and guides
- **Incident Response**: Rapid information retrieval during security incidents
- **Security Training**: Learn from comprehensive cybersecurity documentation

## Troubleshooting

### Common Issues

1. **Missing API Key**
   - Ensure GEMINI_API_KEY is set in .env file

2. **Document Indexing Failures**
   - Check file permissions in data directory
   - Verify supported file formats

3. **Update Failures**
   - Ensure git is installed and accessible
   - Check network connectivity to repositories

### Performance Tips

- Use `--quiet` flag for faster queries (skips verbose output)
- Keep only handbooks enabled (6.89 MB) for minimal storage
- The system only reindexes changed files by default
- Vector database persists between sessions
- First query is slower (model loading), subsequent queries are fast
- Use quick launcher scripts for one-off queries
- Stay in interactive mode for multiple questions

For detailed performance optimization, see `PERFORMANCE.md`

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.


## Acknowledgments

- Google Gemini AI for language model capabilities
- ChromaDB for vector storage
- All data source maintainers for their valuable cybersecurity content

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

*CyberSamatha - Your intelligent cybersecurity knowledge companion*

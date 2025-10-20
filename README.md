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
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### Initial Setup

1. Update all data sources:
```bash
python update_data.py --update
```

2. Index the documents:
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

### Force Reindex
Update the vector database with all documents:
```bash
python cybersamatha.py --index --force
```

## Data Management

### Updating Sources
Update all cybersecurity data repositories:
```bash
python update_data.py --update
```

### Update with Cleanup
Update and optimize storage:
```bash
python update_data.py --update --cleanup
```

### Check Status
View current data status:
```bash
python update_data.py --status
```

### Automated Updates
Add to crontab for daily updates:
```bash
0 2 * * * cd /path/to/cybersamatha && python update_data.py --update --cleanup
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

- Use `--cleanup` with updates to save disk space
- The system only reindexes changed files by default
- Vector database persists between sessions

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

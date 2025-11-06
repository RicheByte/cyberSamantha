# Storage Management Guide

## Overview
Your CyberSamantha installation can range from **~20 MB to 6+ GB** depending on which data sources you enable.

## Current Setup
- **handbooks**: 6.89 MB (enabled, updatable)
- **exploits**: Disabled
- **advisories**: Disabled  
- **nvdcve**: Disabled
- **chroma_db**: 15.83 MB (vector embeddings)
- **Total**: ~23 MB ✅

## Configuration

### Enable/Disable Data Sources
Edit `config.yaml`:

```yaml
data_sources:
  handbooks:
    enabled: true           # Small, essential (6.89 MB)
    remove_git_history: false  # Keep .git for updates
    
  exploits:
    enabled: false          # Large (238 MB + history)
    remove_git_history: true   # Remove .git after clone
    
  advisories:
    enabled: false          # Very large (2.98 GB with history)
    remove_git_history: true
    
  nvdcve:
    enabled: false          # Very large (2.66 GB with history)
    remove_git_history: true
```

### Size Comparison

| Data Source | With .git | Without .git | Recommendation |
|------------|-----------|--------------|----------------|
| handbooks | 6.89 MB | 1.54 MB | ✅ Keep enabled with .git |
| exploits | ~400 MB | ~160 MB | ⚠️ Enable only if needed |
| advisories | ~3 GB | ~50 MB | ⚠️ Very large, disable unless needed |
| nvdcve | ~2.8 GB | ~100 MB | ⚠️ Very large, disable unless needed |

## Storage Commands

### Check Current Size
```bash
python cleanup_storage.py --status
```

### Free Up Space
```bash
# Remove all .git folders except handbooks (safe, keeps docs)
python cleanup_storage.py --remove-git --keep-handbooks

# Full cleanup (temp packs + backups + .git folders)
python cleanup_storage.py --all --keep-handbooks

# Remove temp pack files only
python cleanup_storage.py --temp
```

### Optimize Git Repos
```bash
# Run git garbage collection on remaining repos
python cleanup_storage.py --gc
```

## Recommended Configurations

### Minimal (Best for most users)
- **Size**: ~20 MB
- **Sources**: handbooks only
- **Use case**: General cybersecurity Q&A

```yaml
handbooks: enabled=true
exploits: enabled=false
advisories: enabled=false
nvdcve: enabled=false
```

### Medium
- **Size**: ~200 MB
- **Sources**: handbooks + exploits (without .git)
- **Use case**: Penetration testing, exploit research

```yaml
handbooks: enabled=true, remove_git_history=false
exploits: enabled=true, remove_git_history=true
advisories: enabled=false
nvdcve: enabled=false
```

### Full (Researchers only)
- **Size**: ~500 MB - 1 GB (without .git history)
- **Sources**: All enabled, .git removed
- **Use case**: Comprehensive vulnerability research

```yaml
# All enabled with remove_git_history=true
```

## Important Notes

1. **Removing .git folders**: Makes repos non-updatable via `git pull`. You'll need to re-clone to update.

2. **Temp pack files**: Large `tmp_pack_*` files are leftover from interrupted Git operations. Always safe to delete.

3. **Broken backups**: `.broken` folders are backups created during failed operations. Delete them after confirming your data is good.

4. **Reindexing**: After cleanup, reindex documents:
   ```bash
   python cybersamatha.py --index --force
   ```

## Troubleshooting

### "Access Denied" errors
Some Git pack files may be locked. Close all terminals and retry, or restart your computer.

### Updates fail after removing .git
If you removed .git folders and want to update:
1. Delete the entire repo folder
2. Re-enable in config.yaml
3. Run `python update_data.py --update`

### Out of disk space
Run `python cleanup_storage.py --all` to free maximum space (~5.9 GB).

## Automation

### Auto-cleanup on updates
In `config.yaml`, enable:
```yaml
storage:
  auto_cleanup_git_packs: true
  remove_temp_packs: true
```

Then updates will automatically cleanup temp files:
```bash
python update_data.py --update --cleanup
```

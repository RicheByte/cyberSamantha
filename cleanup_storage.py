#!/usr/bin/env python3
"""
CyberSamantha Storage Cleanup Tool
Removes large Git pack files and optimizes storage
"""

import os
import shutil
import glob
from pathlib import Path
import argparse

class StorageCleanup:
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.total_freed = 0
        
    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable size"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.2f} {size_names[i]}"
    
    def get_size(self, path: Path) -> int:
        """Get file or directory size in bytes"""
        if path.is_file():
            return path.stat().st_size
        
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception as e:
            print(f"⚠️  Error calculating size for {path}: {e}")
        return total
    
    def remove_temp_pack_files(self):
        """Remove temporary Git pack files (tmp_pack_*)"""
        print("\n🧹 Removing temporary Git pack files...")
        
        temp_packs = list(self.data_path.rglob("tmp_pack_*"))
        
        if not temp_packs:
            print("  ✅ No temporary pack files found")
            return
        
        for pack_file in temp_packs:
            try:
                size = self.get_size(pack_file)
                pack_file.unlink()
                self.total_freed += size
                print(f"  ✅ Removed: {pack_file.name} ({self.format_size(size)})")
            except Exception as e:
                print(f"  ❌ Failed to remove {pack_file.name}: {e}")
    
    def remove_git_history(self, repo_dirs: list = None):
        """Remove .git directories from specified repos"""
        print("\n🗑️  Removing Git history (.git folders)...")
        
        if repo_dirs is None:
            # Default to problematic repos
            repo_dirs = ["advisories", "nvdcve", "exploits"]
        
        for repo_name in repo_dirs:
            repo_path = self.data_path / repo_name
            git_dir = repo_path / ".git"
            
            if not git_dir.exists():
                print(f"  ⏭️  {repo_name}: No .git folder found")
                continue
            
            try:
                size_before = self.get_size(git_dir)
                shutil.rmtree(git_dir)
                self.total_freed += size_before
                print(f"  ✅ {repo_name}: Removed .git folder ({self.format_size(size_before)} freed)")
            except Exception as e:
                print(f"  ❌ {repo_name}: Failed to remove .git folder: {e}")
    
    def cleanup_broken_backups(self):
        """Remove .broken backup folders"""
        print("\n🗑️  Removing backup folders (.broken)...")
        
        broken_dirs = list(self.data_path.glob("*.broken"))
        
        if not broken_dirs:
            print("  ✅ No backup folders found")
            return
        
        for broken_dir in broken_dirs:
            try:
                size = self.get_size(broken_dir)
                shutil.rmtree(broken_dir)
                self.total_freed += size
                print(f"  ✅ Removed: {broken_dir.name} ({self.format_size(size)} freed)")
            except Exception as e:
                print(f"  ❌ Failed to remove {broken_dir.name}: {e}")
    
    def run_git_gc(self):
        """Run git garbage collection on remaining repos"""
        print("\n♻️  Running Git garbage collection...")
        
        import subprocess
        
        for repo_dir in self.data_path.iterdir():
            if not repo_dir.is_dir():
                continue
            
            git_dir = repo_dir / ".git"
            if not git_dir.exists():
                continue
            
            print(f"  🔄 Processing {repo_dir.name}...")
            
            try:
                # Expire reflog
                subprocess.run(
                    ["git", "reflog", "expire", "--all", "--expire=now"],
                    cwd=repo_dir,
                    capture_output=True,
                    timeout=60
                )
                
                # Run garbage collection
                size_before = self.get_size(git_dir)
                subprocess.run(
                    ["git", "gc", "--prune=now", "--aggressive"],
                    cwd=repo_dir,
                    capture_output=True,
                    timeout=300
                )
                size_after = self.get_size(git_dir)
                
                freed = size_before - size_after
                if freed > 0:
                    self.total_freed += freed
                    print(f"    ✅ Freed {self.format_size(freed)}")
                else:
                    print(f"    ✅ Already optimized")
                    
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  Timeout during gc")
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
    
    def show_current_sizes(self):
        """Display current data folder sizes"""
        print("\n📊 Current Storage Usage:")
        print("=" * 60)
        
        # Show individual repo sizes
        repos = ["handbooks", "exploits", "advisories", "nvdcve"]
        for repo_name in repos:
            repo_path = self.data_path / repo_name
            if repo_path.exists():
                size = self.get_size(repo_path)
                git_size = self.get_size(repo_path / ".git") if (repo_path / ".git").exists() else 0
                doc_size = size - git_size
                
                print(f"  {repo_name:15} Total: {self.format_size(size):>10}")
                if git_size > 0:
                    print(f"                  ├─ Documents: {self.format_size(doc_size):>10}")
                    print(f"                  └─ Git (.git): {self.format_size(git_size):>10}")
        
        # Show total
        print("-" * 60)
        total_size = self.get_size(self.data_path)
        print(f"  {'TOTAL':15} {self.format_size(total_size):>10}")
        
        # Show chroma_db size
        chroma_path = Path("chroma_db")
        if chroma_path.exists():
            chroma_size = self.get_size(chroma_path)
            print(f"  {'chroma_db':15} {self.format_size(chroma_size):>10}")
        
        print("=" * 60)
    
    def run_cleanup(self, remove_temp: bool = True, remove_git: bool = False, 
                   remove_backups: bool = True, run_gc: bool = False,
                   git_repos: list = None):
        """Run full cleanup process"""
        print("🚀 CyberSamantha Storage Cleanup")
        print("=" * 60)
        
        # Show sizes before
        size_before = self.get_size(self.data_path)
        print(f"\n📦 Data folder size before: {self.format_size(size_before)}")
        
        # Run cleanup operations
        if remove_backups:
            self.cleanup_broken_backups()
        
        if remove_temp:
            self.remove_temp_pack_files()
        
        if remove_git:
            self.remove_git_history(git_repos)
        
        if run_gc:
            self.run_git_gc()
        
        # Show results
        size_after = self.get_size(self.data_path)
        
        print("\n" + "=" * 60)
        print("✅ Cleanup Complete!")
        print("=" * 60)
        print(f"  Before:  {self.format_size(size_before)}")
        print(f"  After:   {self.format_size(size_after)}")
        print(f"  Freed:   {self.format_size(self.total_freed)}")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="CyberSamantha Storage Cleanup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_storage.py --status                    # Show current sizes
  python cleanup_storage.py --temp                      # Remove temp pack files only
  python cleanup_storage.py --remove-git                # Remove .git folders (advisories, nvdcve, exploits)
  python cleanup_storage.py --all                       # Full cleanup (temp + backups + git history)
  python cleanup_storage.py --all --keep-handbooks      # Full cleanup but keep handbooks .git
  python cleanup_storage.py --gc                        # Run git gc on all repos
        """
    )
    
    parser.add_argument("--status", action="store_true", 
                       help="Show current storage usage")
    parser.add_argument("--temp", action="store_true", 
                       help="Remove temporary pack files")
    parser.add_argument("--remove-git", action="store_true", 
                       help="Remove .git folders from advisories, nvdcve, exploits")
    parser.add_argument("--remove-backups", action="store_true", 
                       help="Remove .broken backup folders")
    parser.add_argument("--gc", action="store_true", 
                       help="Run git garbage collection")
    parser.add_argument("--all", action="store_true", 
                       help="Run all cleanup operations")
    parser.add_argument("--keep-handbooks", action="store_true", 
                       help="Keep .git folder in handbooks (for updates)")
    
    args = parser.parse_args()
    
    cleanup = StorageCleanup()
    
    if args.status:
        cleanup.show_current_sizes()
        return
    
    # Determine what to clean
    remove_temp = args.temp or args.all
    remove_git = args.remove_git or args.all
    remove_backups = args.remove_backups or args.all
    run_gc = args.gc
    
    # Determine which repos to remove .git from
    git_repos = None
    if remove_git:
        if args.keep_handbooks:
            git_repos = ["advisories", "nvdcve", "exploits"]
        else:
            git_repos = ["advisories", "nvdcve", "exploits", "handbooks"]
    
    if not any([remove_temp, remove_git, remove_backups, run_gc]):
        print("❌ No cleanup operation specified")
        print("\nUsage:")
        print("  python cleanup_storage.py --status        # Show sizes")
        print("  python cleanup_storage.py --temp          # Remove temp packs")
        print("  python cleanup_storage.py --all           # Full cleanup")
        print("\nFor more options, use --help")
        return
    
    cleanup.run_cleanup(
        remove_temp=remove_temp,
        remove_git=remove_git,
        remove_backups=remove_backups,
        run_gc=run_gc,
        git_repos=git_repos
    )
    
    print("\n💡 Next steps:")
    print("  • Run: python cybersamatha.py --index --force")
    print("  • This will reindex your documents with the cleaned data")

if __name__ == "__main__":
    main()

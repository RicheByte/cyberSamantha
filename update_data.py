# update_data.py
import os
import sys
import json
import yaml
import requests
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import time
from typing import Dict, List, Optional

class CyberSamathaDataUpdater:
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)
        self.repo_configs = {
            "handbooks": {
                "url": "https://github.com/0xsyr0/Awesome-Cybersecurity-Handbooks",
                "type": "github",
                "target_dir": "handbooks",
                "shallow": True,  # Use shallow clone
                "depth": 1
            },
            "exploits": {
                "url": "https://gitlab.com/exploit-database/exploitdb",
                "type": "gitlab",
                "target_dir": "exploits",
                "shallow": True,  # Use shallow clone for large repo
                "depth": 1,
                "skip": False  # Can be set to True to skip problematic repos
            },
            "advisories": {
                "url": "https://github.com/github/advisory-database",
                "type": "github",
                "target_dir": "advisories",
                "shallow": True,
                "depth": 1
            },
            "nvdcve": {
                "url": "https://github.com/olbat/nvdcve",
                "type": "github", 
                "target_dir": "nvdcve",
                "shallow": True,
                "depth": 1
            }
        }
        
        # Create data directory structure
        self.data_path.mkdir(exist_ok=True)
        for config in self.repo_configs.values():
            (self.data_path / config["target_dir"]).mkdir(exist_ok=True)
        
        # Create metadata file to track updates
        self.metadata_file = self.data_path / "update_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load update metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """Save update metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving metadata: {e}")
    
    def run_git_command(self, cmd: List[str], cwd: Optional[Path] = None, timeout: int = 600) -> tuple:
        """Run git command and return (success, output, error)"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                check=True
            )
            return (True, result.stdout, "")
        except subprocess.TimeoutExpired:
            return (False, "", "Command timed out")
        except subprocess.CalledProcessError as e:
            return (False, e.stdout, e.stderr)
        except Exception as e:
            return (False, "", str(e))
    
    def check_network_connectivity(self) -> bool:
        """Check if we can reach GitHub/GitLab"""
        print("🌐 Checking network connectivity...")
        
        test_urls = [
            "https://github.com",
            "https://gitlab.com"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ Can reach {url}")
                else:
                    print(f"  ⚠️  {url} returned status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Cannot reach {url}: {e}")
                return False
        
        return True
    
    def fix_detached_head(self, repo_dir: Path) -> bool:
        """Fix detached HEAD state in a git repository"""
        print(f"  🔧 Fixing detached HEAD state...")
        
        # Get the default branch name
        success, output, error = self.run_git_command(
            ["git", "remote", "show", "origin"], 
            cwd=repo_dir
        )
        
        if success and "HEAD branch:" in output:
            # Extract default branch name
            for line in output.split('\n'):
                if 'HEAD branch:' in line:
                    default_branch = line.split(':')[-1].strip()
                    break
            else:
                default_branch = "main"
        else:
            default_branch = "main"
        
        # Try to checkout the default branch
        success, _, _ = self.run_git_command(
            ["git", "checkout", default_branch], 
            cwd=repo_dir
        )
        
        if not success:
            # Try master if main doesn't work
            success, _, _ = self.run_git_command(
                ["git", "checkout", "master"], 
                cwd=repo_dir
            )
        
        return success
    
    def clone_or_update_repo(self, repo_name: str, config: Dict, retry_count: int = 3) -> bool:
        """Clone or update a repository with retry logic"""
        
        # Check if this repo should be skipped
        if config.get("skip", False):
            print(f"⏭️  Skipping {repo_name} (marked as skip)")
            return True
        
        repo_url = config["url"]
        target_dir = self.data_path / config["target_dir"]
        repo_type = config["type"]
        shallow = config.get("shallow", False)
        depth = config.get("depth", 1)
        
        print(f"🔄 Updating {repo_name}...")
        
        if (target_dir / ".git").exists():
            # Update existing repository
            print(f"  📥 Pulling latest changes for {repo_name}")
            
            # Check if we're in detached HEAD state
            success, output, error = self.run_git_command(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                cwd=target_dir
            )
            
            if success and output.strip() == "HEAD":
                # We're in detached HEAD state
                if not self.fix_detached_head(target_dir):
                    print(f"  ⚠️  Could not fix detached HEAD, trying to re-clone...")
                    shutil.rmtree(target_dir)
                    return self.clone_or_update_repo(repo_name, config, retry_count)
            
            # Now try to pull
            for attempt in range(retry_count):
                success, output, error = self.run_git_command(
                    ["git", "pull", "--rebase"], 
                    cwd=target_dir,
                    timeout=300
                )
                
                if success:
                    print(f"  ✅ Successfully updated {repo_name}")
                    return True
                else:
                    if attempt < retry_count - 1:
                        print(f"  ⚠️  Attempt {attempt + 1} failed, retrying...")
                        time.sleep(5)
                    else:
                        print(f"  ❌ Failed to update {repo_name} after {retry_count} attempts")
                        print(f"  Error: {error[:200]}")
            
            return False
        else:
            # Clone new repository
            print(f"  📥 Cloning {repo_name} from {repo_url}")
            
            # Remove existing directory if it exists (without .git)
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # Build clone command
            clone_cmd = ["git", "clone"]
            
            if shallow:
                clone_cmd.extend(["--depth", str(depth)])
            
            clone_cmd.extend([repo_url, str(target_dir)])
            
            # Try cloning with retries
            for attempt in range(retry_count):
                success, output, error = self.run_git_command(
                    clone_cmd,
                    timeout=600
                )
                
                if success:
                    print(f"  ✅ Successfully cloned {repo_name}")
                    return True
                else:
                    if attempt < retry_count - 1:
                        print(f"  ⚠️  Clone attempt {attempt + 1} failed, retrying in 10 seconds...")
                        time.sleep(10)
                    else:
                        print(f"  ❌ Failed to clone {repo_name} after {retry_count} attempts")
                        print(f"  Error: {error[:200]}")
                        
                        # Suggest marking as skip
                        print(f"  💡 Tip: You can skip this repo by editing the config")
            
            return False
    
    def update_handbooks(self) -> bool:
        """Update Awesome Cybersecurity Handbooks"""
        config = self.repo_configs["handbooks"]
        success = self.clone_or_update_repo("Awesome Cybersecurity Handbooks", config)
        
        if success:
            # Additional processing for handbooks if needed
            handbooks_dir = self.data_path / "handbooks"
            readme_files = list(handbooks_dir.glob("**/*.md")) + list(handbooks_dir.glob("**/*.txt"))
            print(f"  📚 Found {len(readme_files)} handbook files")
            
            self.metadata["handbooks"] = {
                "last_updated": datetime.now().isoformat(),
                "file_count": len(readme_files),
                "source": config["url"]
            }
        
        return success
    
    def update_exploits(self) -> bool:
        """Update Exploit Database"""
        config = self.repo_configs["exploits"]
        success = self.clone_or_update_repo("Exploit Database", config)
        
        if success:
            exploits_dir = self.data_path / "exploits"
            
            # Count exploit files (adjust patterns based on exploitdb structure)
            exploit_files = list(exploits_dir.glob("**/*.md")) + \
                           list(exploits_dir.glob("**/*.txt")) + \
                           list(exploits_dir.glob("**/*.json"))
            
            print(f"  💥 Found {len(exploit_files)} exploit files")
            
            self.metadata["exploits"] = {
                "last_updated": datetime.now().isoformat(),
                "file_count": len(exploit_files),
                "source": config["url"]
            }
        
        return success
    
    def update_advisories(self) -> bool:
        """Update GitHub Advisory Database"""
        config = self.repo_configs["advisories"]
        success = self.clone_or_update_repo("GitHub Advisory Database", config)
        
        if success:
            advisories_dir = self.data_path / "advisories"
            
            # Count advisory files (typically in advisories/**/*.json)
            advisory_files = list(advisories_dir.glob("**/*.json"))
            advisory_files += list(advisories_dir.glob("**/*.yml")) 
            advisory_files += list(advisories_dir.glob("**/*.yaml"))
            
            print(f"  🛡️  Found {len(advisory_files)} advisory files")
            
            self.metadata["advisories"] = {
                "last_updated": datetime.now().isoformat(),
                "file_count": len(advisory_files),
                "source": config["url"]
            }
        
        return success
    
    def update_nvdcve(self) -> bool:
        """Update NVD CVE Database"""
        config = self.repo_configs["nvdcve"]
        success = self.clone_or_update_repo("NVD CVE Database", config)
        
        if success:
            nvdcve_dir = self.data_path / "nvdcve"
            
            # Count CVE files
            cve_files = list(nvdcve_dir.glob("**/*.json")) + \
                       list(nvdcve_dir.glob("**/*.xml")) + \
                       list(nvdcve_dir.glob("**/*.csv"))
            
            print(f"  📊 Found {len(cve_files)} CVE data files")
            
            self.metadata["nvdcve"] = {
                "last_updated": datetime.now().isoformat(),
                "file_count": len(cve_files),
                "source": config["url"]
            }
        
        return success
    
    def cleanup_old_data(self):
        """Clean up git history to save space (optional)"""
        print("\n🧹 Cleaning up git histories to save space...")
        
        for repo_name, config in self.repo_configs.items():
            repo_dir = self.data_path / config["target_dir"]
            git_dir = repo_dir / ".git"
            
            if git_dir.exists():
                size_before = self.get_directory_size(repo_dir)
                
                # Clean git history
                self.run_git_command(["git", "reflog", "expire", "--all", "--expire=now"], cwd=repo_dir)
                self.run_git_command(["git", "gc", "--prune=now", "--aggressive"], cwd=repo_dir)
                
                size_after = self.get_directory_size(repo_dir)
                savings = size_before - size_after
                
                if savings > 0:
                    print(f"  ✅ {repo_name}: Saved {self.format_file_size(savings)}")
    
    def get_directory_size(self, path: Path) -> int:
        """Get directory size in bytes"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
        except Exception as e:
            print(f"  ⚠️  Error calculating size: {e}")
        return total
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def update_all(self, cleanup: bool = False, skip_network_check: bool = False):
        """Update all data sources"""
        print("🚀 Starting CyberSamatha Data Update")
        print("=" * 50)
        
        # Check network connectivity
        if not skip_network_check:
            if not self.check_network_connectivity():
                print("\n❌ Network connectivity issues detected!")
                print("💡 Tips:")
                print("  - Check your internet connection")
                print("  - Check if you're behind a proxy/firewall")
                print("  - Try using a VPN")
                print("  - Use --skip-network-check to bypass this check")
                return
        
        start_time = datetime.now()
        
        # Update each repository
        results = {
            "handbooks": self.update_handbooks(),
            "exploits": self.update_exploits(), 
            "advisories": self.update_advisories(),
            "nvdcve": self.update_nvdcve()
        }
        
        # Cleanup if requested
        if cleanup:
            self.cleanup_old_data()
        
        # Save metadata
        self.metadata["last_full_update"] = datetime.now().isoformat()
        self.save_metadata()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Update Summary:")
        print("=" * 50)
        
        successful = 0
        for repo_name, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {repo_name:15} {status}")
            if success:
                successful += 1
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n🎉 Updated {successful}/{len(results)} data sources in {total_time:.1f} seconds")
        
        if successful == len(results):
            print("💾 All data sources updated successfully!")
        elif successful > 0:
            print(f"⚠️  {len(results) - successful} update(s) failed. Check the logs above.")
            print("💡 You can still use the RAG system with successfully updated data.")
        else:
            print("❌ All updates failed. Check your network connection and try again.")
        
        # Show total file counts
        total_files = sum([
            self.metadata.get("handbooks", {}).get("file_count", 0),
            self.metadata.get("exploits", {}).get("file_count", 0),
            self.metadata.get("advisories", {}).get("file_count", 0),
            self.metadata.get("nvdcve", {}).get("file_count", 0)
        ])
        
        print(f"📁 Total documents in knowledge base: {total_files:,}")
        
        # Show data directory size
        total_size = self.get_directory_size(self.data_path)
        print(f"💾 Total data size: {self.format_file_size(total_size)}")
    
    def show_status(self):
        """Show current update status"""
        if not self.metadata:
            print("❌ No update metadata found. Run update first.")
            return
        
        print("📅 CyberSamatha Data Status:")
        print("=" * 70)
        print(f"{'Repository':<20} {'Last Updated':<25} {'Files':<10}")
        print("-" * 70)
        
        for repo_name in self.repo_configs.keys():
            repo_data = self.metadata.get(repo_name, {})
            last_updated = repo_data.get("last_updated", "Never")
            file_count = repo_data.get("file_count", 0)
            
            if last_updated != "Never":
                # Format timestamp
                try:
                    last_dt = datetime.fromisoformat(last_updated)
                    last_str = last_dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    last_str = "Invalid date"
            else:
                last_str = "Never"
            
            print(f"{repo_name:<20} {last_str:<25} {file_count:>9,}")
        
        print("-" * 70)
        
        # Show total
        total_files = sum([
            self.metadata.get(repo, {}).get("file_count", 0) 
            for repo in self.repo_configs.keys()
        ])
        print(f"{'TOTAL':<20} {'':<25} {total_files:>9,}")
        
        # Show last full update
        if "last_full_update" in self.metadata:
            last_full = datetime.fromisoformat(self.metadata["last_full_update"])
            print(f"\n📅 Last full update: {last_full.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show data directory size
        total_size = self.get_directory_size(self.data_path)
        print(f"💾 Total data size: {self.format_file_size(total_size)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CyberSamatha Data Updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_data.py --update                  # Update all data sources
  python update_data.py --update --cleanup        # Update and cleanup git histories
  python update_data.py --status                  # Show current status
  python update_data.py --update --skip-network-check  # Skip network check
        """
    )
    parser.add_argument("--update", action="store_true", help="Update all data sources")
    parser.add_argument("--cleanup", action="store_true", help="Clean up git histories after update")
    parser.add_argument("--status", action="store_true", help="Show current update status")
    parser.add_argument("--skip-network-check", action="store_true", help="Skip network connectivity check")
    
    args = parser.parse_args()
    
    updater = CyberSamathaDataUpdater()
    
    if args.update:
        updater.update_all(cleanup=args.cleanup, skip_network_check=args.skip_network_check)
    elif args.status:
        updater.show_status()
    else:
        print("❌ Please specify --update or --status")
        print("\nUsage:")
        print("  python update_data.py --update              # Update all data")
        print("  python update_data.py --status              # Show current status")
        print("  python update_data.py --update --cleanup    # Update and cleanup")
        print("\nFor more information, use --help")

if __name__ == "__main__":
    main()
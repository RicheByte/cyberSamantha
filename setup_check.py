#!/usr/bin/env python3
"""
Cross-platform setup helper for CyberSamantha
"""
import os
import sys
import platform

def main():
    print("🚀 CyberSamantha Platform Setup")
    print("=" * 60)
    
    os_type = platform.system()
    print(f"✅ Detected OS: {os_type}")
    
    # Make scripts executable on Unix-like systems
    if os_type in ["Linux", "Darwin"]:  # Darwin = macOS
        print("\n📝 Making scripts executable...")
        try:
            os.chmod("ask.sh", 0o755)
            print("  ✅ ask.sh is now executable")
            print("\nYou can now use: ./ask.sh \"your question\"")
        except Exception as e:
            print(f"  ⚠️  Could not make ask.sh executable: {e}")
            print("  Run manually: chmod +x ask.sh")
    
    elif os_type == "Windows":
        print("\n📝 Windows detected - scripts ready to use")
        print("\nQuick commands:")
        print("  PowerShell: .\\ask.ps1 \"your question\"")
        print("  CMD:        ask.bat \"your question\"")
    
    # Check Python version
    py_version = sys.version_info
    print(f"\n🐍 Python Version: {py_version.major}.{py_version.minor}.{py_version.micro}")
    
    if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 8):
        print("  ⚠️  Warning: Python 3.8+ recommended")
    else:
        print("  ✅ Python version OK")
    
    # Check for .env file
    print("\n🔑 Checking API key configuration...")
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            content = f.read()
            if "GEMINI_API_KEY" in content and "your_api_key" not in content:
                print("  ✅ .env file found with API key")
            else:
                print("  ⚠️  .env file found but API key not configured")
                print("  Edit .env and add your Gemini API key")
    else:
        print("  ❌ .env file not found")
        print("  Creating template...")
        try:
            with open(".env", "w") as f:
                f.write("GEMINI_API_KEY=your_api_key_here\n")
            print("  ✅ Created .env template - please add your API key")
        except Exception as e:
            print(f"  ⚠️  Could not create .env: {e}")
    
    # Check for data directory
    print("\n📁 Checking data directory...")
    if os.path.exists("data"):
        data_dirs = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
        if data_dirs:
            print(f"  ✅ Found data sources: {', '.join(data_dirs)}")
        else:
            print("  ⚠️  data/ exists but is empty")
            print("  Run: python update_data.py --update")
    else:
        print("  ❌ data/ directory not found (will be created on first run)")
    
    # Check for chroma_db
    print("\n💾 Checking vector database...")
    if os.path.exists("chroma_db"):
        print("  ✅ Vector database exists")
    else:
        print("  ❌ Vector database not found")
        print("  Run: python cybersamatha.py --index")
    
    print("\n" + "=" * 60)
    print("✅ Setup check complete!")
    print("\n📚 Next steps:")
    print("  1. Add your Gemini API key to .env")
    print("  2. Run: python update_data.py --update")
    print("  3. Run: python cybersamatha.py --index")
    print("  4. Ask questions: python cybersamatha.py --question \"What is XSS?\"")
    print("\n💡 For faster queries, use: --quiet flag")
    print("=" * 60)

if __name__ == "__main__":
    main()

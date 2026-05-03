import sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    try:
        from src.cli.app import CLIApp
        app = CLIApp()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to start CyberSamantha: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

import argparse
import sys
from bobj_manager import BusinessObjectsManager

def main():
    parser = argparse.ArgumentParser(description="Manage Business Objects Application Services")
    parser.add_argument("--action", choices=["start", "stop", "restart"], required=True, help="Action to perform")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        manager = BusinessObjectsManager(config_path=args.config)
        
        success = False
        if args.action == "start":
            success = manager.start_application()
        elif args.action == "stop":
            success = manager.stop_application()
        elif args.action == "restart":
            success = manager.restart_application()
            
        if success:
            print(f"Action '{args.action}' completed successfully.")
            sys.exit(0)
        else:
            print(f"Action '{args.action}' failed. Check logs for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

import argparse
import sys
from remote_bobj_manager import RemoteBusinessObjectsManager

def main():
    parser = argparse.ArgumentParser(description="Remote Manage Business Objects Application Services")
    parser.add_argument("--action", choices=["start", "stop", "restart"], required=True, help="Action to perform")
    parser.add_argument("--config", default="remote_config.json", help="Path to remote configuration file")
    
    args = parser.parse_args()
    
    manager = None
    try:
        manager = RemoteBusinessObjectsManager(config_path=args.config)
        success = manager.perform_action(args.action)
            
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        if manager:
            manager.close()

if __name__ == "__main__":
    main()

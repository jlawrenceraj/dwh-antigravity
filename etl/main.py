import argparse
import yaml
import sys
import os
from src.processor import Processor

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="ETL Validation Framework")
    parser.add_argument('--system-config', required=True, help="Path to system configuration YAML file")
    parser.add_argument('--file', required=True, help="Path to input file")
    parser.add_argument('--file-key', required=False, help="Key matching the config filename (without extension)")
    parser.add_argument('--file-config', required=False, help="Path to specific file configuration YAML")
    
    args = parser.parse_args()
    
    try:
        system_config = load_config(args.system_config)
        
        file_config = None
        file_key = args.file_key
        
        if args.file_config:
            if not os.path.exists(args.file_config):
                raise FileNotFoundError(f"Configuration file not found: {args.file_config}")
            file_config = load_config(args.file_config)
            if not file_key:
                file_key = os.path.splitext(os.path.basename(args.file_config))[0]
        elif args.file_key:
            # Load file specific config from directory
            file_config_dir = system_config.get('system', {}).get('file_config_dir')
            if not file_config_dir:
                 raise ValueError("file_config_dir not defined in system config")
                 
            file_config_path = os.path.join(file_config_dir, f"{args.file_key}.yaml")
            if not os.path.exists(file_config_path):
                raise FileNotFoundError(f"Configuration file not found for key: {args.file_key} at {file_config_path}")
                
            file_config = load_config(file_config_path)
        else:
            raise ValueError("Either --file-key or --file-config must be provided.")
        
        processor = Processor(system_config['system'], file_config, file_key)
        processor.process(args.file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import yaml
import glob
from typing import Dict, Any
from validator.file_validator import FileValidator

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    etl_dir = os.path.dirname(base_dir)
    data_dir = os.path.join(etl_dir, 'data')
    config_path = os.path.join(etl_dir, 'validation_config.yaml')

    print(f"Loading configuration from {config_path}")
    if not os.path.exists(config_path):
        print("Configuration file not found.")
        return

    config = load_config(config_path)
    
    # Iterate over files in data directory
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return

    print(f"Found {len(csv_files)} CSV files.")

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"\nProcessing {file_name}...")
        
        if file_name in config:
            file_config = config[file_name]
            validator = FileValidator(file_config)
            errors = validator.validate_file(file_path)
            
            if errors:
                print(f"Validation FAILED for {file_name}:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(f"Validation PASSED for {file_name}")
        else:
            print(f"No configuration found for {file_name}, skipping.")

if __name__ == "__main__":
    main()

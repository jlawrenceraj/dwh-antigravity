import argparse
import yaml
import logging
import os
from src.pipeline import EtlPipeline

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Generic ETL Framework")
    parser.add_argument('--config', required=True, help="Path to main config file")
    parser.add_argument('--schema', required=True, help="Path to schema file")
    parser.add_argument('--file', required=True, help="Path to input data file")
    
    args = parser.parse_args()

    try:
        config = load_yaml(args.config)
        schema = load_yaml(args.schema)
        
        pipeline = EtlPipeline(config, schema)
        pipeline.run(args.file)
        
    except Exception as e:
        logger.error(f"ETL Process Failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()

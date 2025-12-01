import os
import logging
from datetime import datetime
from .ingestors import get_ingestor
from .validators import DataValidator
from .loaders import DatabaseLoader
from .notifiers import EmailNotifier

class EtlPipeline:
    def __init__(self, config, schema):
        self.config = config
        self.schema = schema
        self.logger = logging.getLogger(__name__)
        
        self.loader = DatabaseLoader(config)
        self.notifier = EmailNotifier(config)

    def run(self, input_file_path: str):
        self.logger.info(f"Starting ETL pipeline for file: {input_file_path}")
        
        # 1. Ingest
        file_type = self.schema.get('file_type', 'csv')
        ingestor = get_ingestor(file_type, self.schema)
        try:
            df = ingestor.read_file(input_file_path)
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            raise

        # 2. Validate
        validator = DataValidator(self.schema)
        valid_df, error_df = validator.validate(df)

        # 3. Handle Errors
        if not error_df.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file_name = f"error_{os.path.basename(input_file_path)}_{timestamp}.csv"
            error_file_path = os.path.join(os.path.dirname(input_file_path), error_file_name)
            
            error_df.to_csv(error_file_path, index=False)
            self.logger.info(f"Error records saved to: {error_file_path}")
            
            # Send Email
            recipient = self.schema.get('notification_email')
            if recipient:
                self.notifier.send_error_report(error_file_path, recipient)
            else:
                self.logger.warning("No notification email configured in schema.")

        # 4. Load Valid Data
        if not valid_df.empty:
            table_name = self.schema.get('target_table')
            if table_name:
                self.loader.load_data(valid_df, table_name)
            else:
                self.logger.warning("No target table configured in schema.")
        else:
            self.logger.info("No valid records to load.")

        self.logger.info("ETL pipeline completed.")

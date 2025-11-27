import os
from typing import Dict, Any, List
from .readers import CSVReader, FixedWidthReader, XMLReader
from .validators import MandatoryValidator, DataTypeValidator, LengthValidator, DuplicateValidator
from .handlers import ErrorHandler, SuccessHandler, EmailNotifier, DBLoader

class Processor:
    def __init__(self, system_config: Dict[str, Any], file_config: Dict[str, Any], file_key: str):
        self.system_config = system_config
        self.file_config = file_config
        self.file_key = file_key
        
        # Determine input file path
        self.input_dir = self.system_config['input_dir']
        # In a real scenario, we might search for the file matching the pattern.
        # For simplicity, we assume the file path is passed or determined externally, 
        # but here let's assume we look for the first match or it's passed in.
        # To make it testable, let's allow passing the specific file path.
    
    def process(self, input_file_path: str):
        print(f"Processing file: {input_file_path}")
        
        # Initialize Reader
        reader = self._get_reader(input_file_path)
        
        # Initialize Validators
        validators = self._get_validators()
        
        # Initialize Handlers
        filename = os.path.basename(input_file_path)
        error_path = os.path.join(self.system_config['error_dir'], f"error_{filename}")
        success_path = os.path.join(self.system_config['processed_dir'], f"clean_{filename}")
        
        # We need to know fieldnames for CSV writer. 
        # For CSV/Fixed Width, we can get them from config.
        fieldnames = [col['name'] for col in self.file_config['columns']]
        
        error_handler = ErrorHandler(error_path, fieldnames)
        success_handler = SuccessHandler(success_path, fieldnames)
        
        error_count = 0
        success_count = 0
        
        try:
            for record in reader:
                record_errors = []
                for validator in validators:
                    record_errors.extend(validator.validate(record))
                
                if record_errors:
                    error_handler.handle(record, record_errors)
                    error_count += 1
                else:
                    success_handler.handle(record)
                    success_count += 1
        finally:
            reader.close()
            error_handler.close()
            success_handler.close()
            
        print(f"Processing complete. Success: {success_count}, Errors: {error_count}")
        
        # Post-processing actions
        if error_count > 0:
            email_notifier = EmailNotifier(self.system_config['email'])
            email_notifier.send_error_notification(error_path, error_count)
            
        if success_count > 0:
            db_loader = DBLoader(self.system_config['database']['connection_string'])
            db_loader.load(success_path)

    def _get_reader(self, file_path: str):
        file_type = self.file_config.get('file_type')
        if file_type == 'csv':
            return CSVReader(file_path, self.file_config)
        elif file_type == 'fixed_width':
            return FixedWidthReader(file_path, self.file_config)
        elif file_type == 'xml':
            return XMLReader(file_path, self.file_config)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _get_validators(self):
        validators = []
        columns = self.file_config.get('columns', [])
        
        validators.append(MandatoryValidator(columns))
        validators.append(DataTypeValidator(columns))
        validators.append(LengthValidator(columns))
        
        if 'unique_constraints' in self.file_config:
            validators.append(DuplicateValidator(self.file_config['unique_constraints']))
            
        return validators

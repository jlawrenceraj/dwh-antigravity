Summary
I created 
VALIDATION_COMMANDS.md
 with individual commands for validating each file:

1. Enterprise Survey Validation

python main.py --system-config config/system_config.yaml --file data/input/enterprise-survey-2024.csv --file-key enterprise_survey

2. Employee Data Validation

python main.py --system-config config/system_config.yaml --file data/input/employees-2024.txt --file-key employee_data
The documentation includes:

Command structure explanation
Prerequisites and setup instructions
Detailed validation rules for each file type
Alternative command syntax using --file-config
Output behavior (success/failure paths)
Each command is ready to use and validates the specific file according to its configuration in config/files/. The system automatically applies data type validation, length checks, unique constraints, and mandatory field validation based on the YAML configuration for each file.
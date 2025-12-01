# ETL Validation Framework Walkthrough

I have successfully implemented the generic, reusable, and configurable ETL framework.

## Features Implemented
- **Generic File Ingestion**: Supports CSV, Pipe-delimited, and Fixed-width (DAT) files.
- **Configurable Validation**:
    - Data Type Checks (Integer, etc.)
    - Length Validation
    - Mandatory Field Checks
    - Duplicate Checks (based on unique keys)
- **Database Loading**: Loads valid records into a database (SQLAlchemy).
- **Error Handling**: Separates invalid records into an error file with detailed messages.
- **Email Notification**: Sends the error file via email (SMTP).
- **Feature Flags**: Toggle DB load and Email via configuration.

## How to Run

### 1. Setup Configuration
Create a schema file in `config/schemas/`. Example `my_schema.yaml`:
```yaml
file_type: csv
target_table: "my_table"
columns:
  - name: "id"
    type: "integer"
    mandatory: true
    unique: true
```

### 2. Execute Pipeline
Run the `main.py` script:
```bash
python main.py --config config/config.yaml --schema config/schemas/my_schema.yaml --file data/my_file.csv
```

### 3. Fixed-Width (DAT) Configuration
For fixed-width files, define the `position` (start, end) for each column:
```yaml
file_type: dat
columns:
  - name: "id"
    position: [0, 5]
  - name: "name"
    position: [5, 25]
```

## Verification Results

I created a sample dataset `data/sample.csv` with intentional errors:
- Duplicate IDs
- Missing Name
- Name too long
- Invalid Integer ID

### Input Data
```csv
id,name,email,department
1,John Doe,john@example.com,IT
1,John Doe,john@example.com,IT
4,,missing@example.com,Finance
5,TooLongName...,long@example.com,Marketing
X,InvalidID,invalid@example.com,Sales
```

### Execution Output
The pipeline successfully processed the file:
- **Valid Records**: Loaded to `etl_database.db`.
- **Error Records**: Saved to `data/error_sample.csv_...`.

### Error Report Content
The generated error file correctly identified all issues:
```csv
id,name,email,department,error_message
1,John Doe,john@example.com,IT,"Duplicate record based on keys: ['id', 'email']; "
4,,missing@example.com,Finance,Missing mandatory field: name; 
5,TooLongName...,long@example.com,Marketing,Length exceeds 50: name; 
X,InvalidID,invalid@example.com,Sales,Invalid integer format: id; 
```

## Next Steps
- Configure your actual database connection in `config/config.yaml`.
- Configure your SMTP server for real email notifications.
- Create schema files for your specific upstream feeds.

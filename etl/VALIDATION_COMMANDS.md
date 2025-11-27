# File Validation Commands

This document provides individual commands to validate each file type in the ETL system.

## Prerequisites

Ensure you are in the `etl` directory and have activated the virtual environment:
```bash
cd c:\Lawrence\Workspace\Antigravity\dwh-antigravity\etl
.venv\Scripts\activate
```

## Command Structure

```bash
python main.py --system-config <system_config_path> --file <input_file_path> --file-key <config_key>
```

## Available File Validations

### 1. Enterprise Survey Validation

**Configuration:** `config/files/enterprise_survey.yaml`  
**File Pattern:** `enterprise-survey-*.csv`  
**File Type:** CSV

**Command:**
```bash
python main.py --system-config config/system_config.yaml --file data/input/enterprise-survey-2024.csv --file-key enterprise_survey
```

**Validations Applied:**
- Data type validation (Year: int, Value: float)
- Length validation (Industry_code_NZSIOC: max 10 chars)
- Unique constraint on [Year, Industry_code_NZSIOC, Variable_code]
- Mandatory field checks

---

### 2. Employee Data Validation

**Configuration:** `config/files/employee_data.yaml`  
**File Pattern:** `employees-*.txt`  
**File Type:** Fixed-width

**Command:**
```bash
python main.py --system-config config/system_config.yaml --file data/input/employees-2024.txt --file-key employee_data
```

**Validations Applied:**
- Data type validation (EmpID: int)
- Fixed-width column parsing (EmpID: 0-5, Name: 5-25)
- Unique constraint on [EmpID]
- Mandatory field checks

---

## Alternative: Using Direct Config Path

You can also specify the configuration file directly:

```bash
python main.py --system-config config/system_config.yaml --file data/input/enterprise-survey-2024.csv --file-config config/files/enterprise_survey.yaml
```

## Output

- **Success:** Processed file moves to `data/processed/`
- **Failure:** File moves to `data/error/` with error details logged

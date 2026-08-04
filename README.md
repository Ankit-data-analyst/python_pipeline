# Python ETL Pipeline

## Project Overview

This project implements a production-style ETL (Extract, Transform, Load) pipeline for processing automotive dealership datasets. The pipeline ingests raw data from Amazon S3, validates and cleans dealer, product, inventory, and sales log datasets, loads valid records into PostgreSQL, and generates audit logs, reject files, and processing summaries.

The pipeline is modular, idempotent, fault-tolerant, and follows industry-standard ETL practices including structured logging, retry mechanisms, and duplicate file detection.

---

## Project Structure

```
project/
│
├── config.py
├── etl.py
├── ingest.py
├── transform.py
├── load.py
├── logger.py
├── database.py
├── requirements.txt
│
├── data/
│   ├── raw/
│   ├── processed_data/
        ├── clean/
│       ├── rejected/
│       └── summary/
│
├── logs/
│   └── pipeline.log
│
└── README.md
```

---

## Setup Instructions


---

## Pipeline Workflow

```
Amazon S3
      │
      ▼
Ingestion
      │
      ▼
Validation & Cleaning
      │
      ▼
Clean / Reject Files
      │
      ▼
PostgreSQL Database
      │
      ▼
Audit Logs & Summary Reports
```

---

## Validation Checks

The pipeline performs the following validations.

### Dealer

- Required field validation
- Date validation
- Region validation
- Credit term range validation

### Product

- Required field validation
- Numeric range validation
- Date validation

### Inventory

- Required field validation
- Quantity range validation
- Date validation
- Foreign key validation

### Sales Logs

- JSON parsing validation
- Required field validation

Invalid records are written to reject files while valid records continue through the pipeline.

---

## Logging

The pipeline maintains structured logs for every stage.

Logs include:

- Pipeline start
- Ingestion
- Validation
- Database loading
- Errors
- Retry attempts
- Pipeline completion

Log file:

```
logs/pipeline.log
```

---

## Idempotency

This pipeline implements idempotent processing using SHA-256 file hashing.

Workflow:

1. Download raw file from S3.
2. Generate SHA-256 hash.
3. Compare hash against the `load_tracking` table.
4. Skip files that have already been processed.
5. Record successful processing after database load completes.

This prevents duplicate data insertion during repeated executions.

---

## Retry Mechanism

S3 downloads use exponential backoff retry.

Configuration:

- Maximum retries: 3
- Exponential delay
- Automatic logging for each retry attempt

---

## Output Files

After execution the following files are generated.

```
data/clean/
```

- clean_dealer.csv
- clean_product.csv
- clean_inventory.csv
- clean_sales_logs.jsonl

```
data/rejected/
```

- reject_dealer.csv
- reject_product.csv
- reject_inventory.csv
- reject_sales_logs.jsonl

```
data/summary/
```

- dealer_summary.json
- product_summary.json
- inventory_summary.json
- sales_logs_summary.json

---

## Running the Pipeline

Execute:

```bash
python etl.py
```

Expected output:

```
Pipeline Started

Starting Ingestion...
Ingestion Completed

Starting Validation...
Validation Completed

Starting Database Load...
Database Load Completed

Pipeline Completed Successfully
```

Execution time:

Approximately 20–60 seconds depending on network speed and database performance.

---

## Technologies Used

- Python 3.x
- PostgreSQL
- Amazon S3
- boto3
- psycopg2
- python-dotenv
- hashlib
- JSON
- CSV

---

## Error Handling

The pipeline handles:

- Missing files
- S3 download failures
- Invalid JSON
- Invalid dates
- Missing mandatory fields
- Invalid numeric values
- Foreign key violations
- Database exceptions

Invalid records are redirected to reject files while valid records continue processing.

---

## Author

Ankit Panda

Python Data Engineering Bootcamp Project
# Martadinata CSV Imputer & 3NF Normalizer

[![CLI Tool](https://img.shields.io/badge/CLI_Tool-Production_Ready-emerald?style=for-the-badge&logo=python&logoColor=white)](#)
[![Normalization](https://img.shields.io/badge/Normalization-3NF_Certified-blue?style=for-the-badge&logo=databricks&logoColor=white)](#)
[![High Throughput](https://img.shields.io/badge/Throughput-8%2C700+_rows%2Fsec-purple?style=for-the-badge&logo=apachespark&logoColor=white)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](#)

> **Industrial-grade, vectorized CLI utility** designed to clean, impute missing values, and normalize uncurated transaction spreadsheets (e.g., Online Retail 1M+ rows) into strict **Third Normal Form (3NF)** relational database schemas.

---

## 📌 Problem Statement

Raw retail datasets frequently suffer from severe data quality deficiencies:
1. **Missing Customer Identifiers**: Up to 20–25% of transactions lack account IDs due to guest checkouts, point-of-sale cash purchases, or anonymous sessions.
2. **Missing Product Metadata**: Item titles and descriptions are often missing, corrupt, or replaced with informal notes (`damaged`, `check`, `?`).
3. **Flawed Relational Modeling**: Single flat-file exports cause massive redundancy, update anomalies, and prohibit efficient relational database indexing.

**Martadinata CSV Imputer** solves this deterministically at scale without discarding valid business telemetry.

---

## 💡 Engineering Highlights & Imputation Logic

### 1. The Deterministic Regional Guest Account Pattern
* Instead of dropping records with missing `Customer ID` (which would obliterate ~22% of revenue telemetry), the engine dynamically maps anonymous transactions to dedicated **Regional Guest Customer IDs** based on sovereign territory:
  - `90001` → *Guest (Bahrain)*
  - `90003` → *Guest (EIRE)*
  - `90004` → *Guest (France)*
  - `90015` → *Guest (United Kingdom)*
* **Result**: Preserves 100% Foreign Key referential integrity (`NOT NULL` constraints intact) while keeping individual VIP spending analytics undistorted.

### 2. Cross-Referenced Product Mode Recovery
* If a `StockCode` SKU has missing descriptions in certain lines, the engine scans historical verified transactions and imputes the **statistical mode** (most frequent valid title).
* For uncataloged items, it assigns a standardized label: `UNLISTED RETAIL ITEM [StockCode]`.
* **Result**: Restores >85% of missing product titles with zero manual guesswork.

### 3. Vectorized 3NF Relational Deconstruction
Deconstructs flat files into 5 ACID-compliant relational entities:
- **`customers.csv`** (`customer_id` PK, `country`, `customer_type`)
- **`products.csv`** (`stock_code` PK, `description`, `standard_price`)
- **`inventory.csv`** (`stock_code` PK/FK, `stock_level`, `last_updated`)
- **`invoices.csv`** (`invoice_no` PK, `invoice_date`, `customer_id` FK, `status`)
- **`invoice_items.csv`** (`item_id` PK, `invoice_no` FK, `stock_code` FK, `quantity`, `unit_price`)

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Recommended fast runner: [`uv`](https://github.com/astral-sh/uv) (or standard `python`)

### Installation & Run

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/geraldmartadinata/martadinata-csv-imputer.git
   cd martadinata-csv-imputer
   ```

2. **Run Demo (Out of the box with sample data):**
   ```powershell
   # Windows PowerShell runner:
   .\run.ps1
   ```
   Or via `uv`:
   ```bash
   uv run imputer.py
   ```

3. **Process Your Own Datasets (Custom Input & Output):**
   ```bash
   uv run imputer.py --input "path/to/my_retail_data.xlsx" --output "path/to/cleaned_output"
   ```

---

## ⚙️ CLI Options

```text
usage: imputer.py [-h] [--input INPUT] [--output OUTPUT] [--guest-prefix GUEST_PREFIX]

Martadinata CSV Imputer & 3NF Normalizer

options:
  -h, --help            Show this help message and exit
  --input INPUT, -i INPUT
                        Path to raw retail input file (.csv or .xlsx)
                        [default: sample/raw_sample.csv]
  --output OUTPUT, -o OUTPUT
                        Directory to save 3NF normalized CSV files
                        [default: output]
  --guest-prefix GUEST_PREFIX
                        Base numeric ID prefix for generated regional Guest Customer accounts
                        [default: 90000]
```

---

## 📊 Performance Benchmark

Tested on a live commercial dataset of **1,048,575 rows**:

```text
                  Martadinata Retail - 3NF Database Entity Audit                   
┌────────────────┬─────────────┬────────────┬───────────┬───────────────────┐
│ Entity / Table │ Primary Key │ Total Rows │ File Size │ Destination File  │
├────────────────┼─────────────┼────────────┼───────────┼───────────────────┤
│ customers      │ customer_id │      5,939 │   0.18 MB │ customers.csv     │
│ products       │ stock_code  │      5,130 │   0.20 MB │ products.csv      │
│ inventory      │ stock_code  │      5,130 │   0.16 MB │ inventory.csv     │
│ invoices       │ invoice_no  │     52,961 │   2.23 MB │ invoices.csv      │
│ invoice_items  │ item_id     │  1,048,575 │  28.38 MB │ invoice_items.csv │
└────────────────┴─────────────┴────────────┴───────────┴───────────────────┘

Execution Speed: ~8,740 records/second
Referential Integrity: 100% PASS (Zero Orphan Keys)
3NF Compliance: Fully Verified
```

---

## 📁 Repository Layout

```text
martadinata-csv-imputer/
├── sample/
│   └── raw_sample.csv        # Lightweight demo file demonstrating missing values
├── imputer.py                # Standalone vectorized CLI tool with Rich UI
├── run.ps1                   # One-click Windows PowerShell runner
├── LICENSE                   # MIT License
├── .gitignore
└── README.md
```

---

## 📄 License
Released under the [MIT License](LICENSE).  
Authored by **Gerald Martadinata**. Contributions and feature requests are welcome!

# Martadinata CSV Imputer & 3NF Normalizer

[![CLI Tool](https://img.shields.io/badge/CLI_Tool-Production_Ready-emerald?style=for-the-badge&logo=python&logoColor=white)](#)
[![Interactive Menu](https://img.shields.io/badge/UI-Interactive_Terminal_Menu-cyan?style=for-the-badge&logo=gnubash&logoColor=white)](#)
[![Normalization](https://img.shields.io/badge/Normalization-3NF_Certified-blue?style=for-the-badge&logo=databricks&logoColor=white)](#)
[![High Throughput](https://img.shields.io/badge/Throughput-8%2C700+_rows%2Fsec-purple?style=for-the-badge&logo=apachespark&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](#)

> **Industrial-grade, vectorized CLI utility** designed to clean, impute missing values, normalize transaction spreadsheets into strict **Third Normal Form (3NF)** relational database schemas, and verify dataset integrity with automated audit reports.

---

## 📌 Features

1. **Interactive Terminal Menu**: Run without flags to get an intuitive menu for choosing cleaning, verification, or full pipeline.
2. **Missing Customer Imputation**: Deterministically maps anonymous transactions to dedicated **Regional Guest Customer IDs** (`90001+`), preserving 100% of telemetry without breaking Foreign Key constraints.
3. **Missing Product Title Recovery**: Scans historical verified transactions for matching `StockCode` SKUs and imputes the statistical mode.
4. **3NF Relational Deconstruction**: Outputs 5 normalized tables (`customers`, `products`, `inventory`, `invoices`, `invoice_items`).
5. **Built-in Quality & Integrity Audit**: Verifies zero-null completeness and tests all Foreign Key relationships for zero orphan keys.

---

## 🚀 Quickstart & How to Run

### Method 1: Double-Click Runner (Windows)
Simply double-click **`run.bat`** in File Explorer. Windows will launch the terminal and display the interactive menu immediately!

### Method 2: Direct Command in Terminal
From PowerShell or CMD inside the repository folder:

```powershell
# Interactive Menu Mode (Recommended)
uv run imputer.py

# Or run specific actions directly via flags:
uv run imputer.py --all       # Run Clean + Audit Verification
uv run imputer.py --clean     # Run Clean & Normalize only
uv run imputer.py --verify    # Run Data Integrity Audit only
```

---

## 🖥️ Interactive Terminal Menu Preview

When you run `imputer.py`, you will see:

```text
 __  __             _             _ _            _         
|  \/  | __ _ _ __ | |_ __ _   __| (_)_ __   __ _| |_ __ _  
| |\/| |/ _` | '__|| __/ _` | / _` | | '_ \ / _` | __/ _` | 
| |  | | (_| | |   | || (_| || (_| | | | | | (_| | || (_| | 
|_|  |_|\__,_|_|    \__\__,_| \__,_|_|_| |_|\__,_|\__\__,_| 
            C S V   I M P U T E R   &   3 N F               
 High-Performance Data Engineering & Quality Assurance CLI • v1.1.0

┌─────────────────────── Martadinata Data Core: ONLINE ───────────────────────┐
│ Target Architecture: PostgreSQL / MySQL 3NF Compliant Schema                │
│ Engine Capability: Vectorized Imputation • 3NF Deconstruction • Zero-Null    │
│ Data Quality Standard: ACID Compliant • 3NF Normalized • Zero Orphan Keys   │
└─────────────────────────────────────────────────────────────────────────────┘

Available Operations:
 [1] Clean & Impute Raw Data -> Generate 3NF CSV Files
 [2] Verify & Audit Processed Data (Zero-Null & Foreign Key Check)
 [3] Full End-to-End Pipeline (Clean + Audit)
 [4] Change Input / Output Paths
 [5] Exit

Enter option [1-5] (default: 3):
```

---

## ⚙️ CLI Options & Custom Datasets

To process external datasets outside the default paths:

```bash
uv run imputer.py --input "path/to/my_data.xlsx" --output "path/to/output_dir"
```

| Flag | Short | Description |
| :--- | :--- | :--- |
| `--input` | `-i` | Path to raw retail input file (`.csv` or `.xlsx`) |
| `--output` | `-o` | Destination directory for 3NF normalized CSV files |
| `--clean` | | Execute cleaning and normalization directly |
| `--verify` | | Execute automated quality and referential integrity audit directly |
| `--all` | | Execute both cleaning and audit consecutively |
| `--guest-prefix` | | Base numeric ID prefix for regional Guest Accounts (default: `90000`) |

---

## 📊 3NF Deconstruction Output

| Entity | Primary Key | Description |
| :--- | :--- | :--- |
| **`customers.csv`** | `customer_id` | Customer directory (Registered accounts + Regional Guest mappings) |
| **`products.csv`** | `stock_code` | Product catalog with sanitized descriptions and standard catalog prices |
| **`inventory.csv`** | `stock_code` | Initial stock level ledger (ready for database inventory trigger integration) |
| **`invoices.csv`** | `invoice_no` | Order master ledger with transaction timestamp, customer FK, and order status |
| **`invoice_items.csv`** | `item_id` | Line-item detail ledger with quantity and historical billed unit price |

---

## 📁 Repository Layout

```text
martadinata-csv-imputer/
├── sample/
│   └── raw_sample.csv        # Lightweight demo file demonstrating missing values
├── imputer.py                # All-in-one CLI tool (interactive menu + ETL + audit suite)
├── run.bat                   # Native Windows batch launcher (double-click friendly)
├── run.ps1                   # PowerShell launcher
├── LICENSE                   # MIT License
├── .gitignore
└── README.md
```

---

## 📄 License
Released under the [MIT License](LICENSE).  
Authored by **Gerald Martadinata**.

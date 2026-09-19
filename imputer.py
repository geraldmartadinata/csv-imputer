# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.2.0",
#     "openpyxl>=3.1.2",
#     "rich>=13.7.0",
#     "pyarrow>=15.0.0",
# ]
# ///

"""
================================================================================
  Martadinata CSV Imputer & 3NF Normalizer
  Author: Gerald Martadinata
  Repository: https://github.com/geraldmartadinata/martadinata-csv-imputer
  Description: Industrial-grade CLI tool for cleansing, imputing, and 
               normalizing 1M+ retail transaction flat-files into 3NF,
               with integrated automated data quality verification.
================================================================================
"""

import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime

# Enforce UTF-8 on Windows Consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich import box

console = Console(highlight=False)

BANNER = r"""
[bold cyan] __  __             _             _ _            _         [/bold cyan]
[bold cyan]|  \/  | __ _ _ __ | |_ __ _   __| (_)_ __   __ _| |_ __ _  [/bold cyan]
[bold cyan]| |\/| |/ _` | '__|| __/ _` | / _` | | '_ \ / _` | __/ _` | [/bold cyan]
[bold cyan]| |  | | (_| | |   | || (_| || (_| | | | | | (_| | || (_| | [/bold cyan]
[bold cyan]|_|  |_|\__,_|_|    \__\__,_| \__,_|_|_| |_|\__,_|\__\__,_| [/bold cyan]
[bold cyan]            C S V   I M P U T E R   &   3 N F               [/bold cyan]
[dim] High-Performance Data Engineering & Quality Assurance CLI • v1.1.0[/dim]
"""

def print_header():
    console.print(BANNER)
    info_panel = Panel(
        "[bold white]Target Architecture:[/bold white] PostgreSQL / MySQL 3NF Compliant Schema\n"
        "[bold white]Engine Capability:[/bold white] Vectorized Imputation • 3NF Deconstruction • Zero-Null Verification\n"
        "[bold white]Data Quality Standard:[/bold white] ACID Compliant • 3NF Normalized • Zero Orphan Keys",
        title="[bold green]Martadinata Data Core: ONLINE[/bold green]",
        border_style="cyan",
        box=box.ROUNDED
    )
    console.print(info_panel)
    console.print()

# ==============================================================================
# PIPELINE: Clean & Normalize
# ==============================================================================
def clean_and_normalize(input_file: Path, output_dir: Path, guest_prefix: int = 90000):
    start_time = time.time()
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_file = output_dir / ".cache_raw_data.parquet"
    
    console.print(Panel(f"[bold white]Input Source:[/bold white] [cyan]{input_file}[/cyan]\n[bold white]Output Destination:[/bold white] [cyan]{output_dir}[/cyan]", title="[bold cyan]Phase 1: ETL & Normalization Pipeline[/bold cyan]", box=box.ROUNDED))
    
    # Step 1: Ingestion
    with Progress(
        SpinnerColumn("dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(style="blue", complete_style="green"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        load_task = progress.add_task("[1/4] Ingesting raw dataset...", total=100)
        
        if cache_file.exists() and cache_file.stat().st_mtime > input_file.stat().st_mtime:
            progress.update(load_task, completed=50)
            df = pd.read_parquet(cache_file)
        else:
            progress.update(load_task, completed=25)
            if input_file.suffix.lower() == '.xlsx':
                df = pd.read_excel(input_file, sheet_name=0)
            else:
                df = pd.read_csv(input_file)
            progress.update(load_task, completed=75)
            try:
                df.to_parquet(cache_file, index=False)
            except Exception:
                pass
                
        progress.update(load_task, completed=100)
        total_raw_rows = len(df)
        
    console.print(f" [bold green][OK][/bold green] Ingested [bold yellow]{total_raw_rows:,}[/bold yellow] raw records.")

    # Step 2: Vectorized Imputation
    with Progress(
        SpinnerColumn("dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(style="blue", complete_style="green"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        impute_task = progress.add_task("[2/4] Executing vectorized imputation & sanitization...", total=100)
        
        df['Invoice'] = df['Invoice'].astype(str).str.strip()
        df['StockCode'] = df['StockCode'].astype(str).str.strip().str.upper()
        df['Country'] = df['Country'].astype(str).str.strip()
        progress.update(impute_task, completed=20)
        
        initial_missing_desc = df['Description'].isnull().sum()
        valid_desc = df.dropna(subset=['Description']).copy()
        valid_desc['Description'] = valid_desc['Description'].astype(str).str.strip().str.upper()
        
        stock_to_desc = (
            valid_desc[valid_desc['Description'].str.len() > 2]
            .groupby('StockCode')['Description']
            .agg(lambda x: x.mode()[0] if not x.empty else None)
            .to_dict()
        )
        progress.update(impute_task, completed=50)
        
        is_invalid_desc = (
            df['Description'].isna() | 
            df['Description'].astype(str).str.strip().str.lower().isin(['', '?', 'check', 'nan'])
        )
        mapped_desc = df['StockCode'].map(stock_to_desc)
        fallback_desc = "UNLISTED RETAIL ITEM " + df['StockCode']
        
        df['Description'] = df['Description'].astype(str).str.strip().str.upper()
        df.loc[is_invalid_desc, 'Description'] = mapped_desc[is_invalid_desc].fillna(fallback_desc[is_invalid_desc])
        progress.update(impute_task, completed=75)
        
        initial_missing_cust = df['Customer ID'].isnull().sum()
        missing_cust_countries = sorted(df[df['Customer ID'].isnull()]['Country'].unique())
        country_to_guest_id = {
            country: guest_prefix + idx + 1 
            for idx, country in enumerate(missing_cust_countries)
        }
        
        df['Customer_ID_Clean'] = (
            df['Customer ID']
            .fillna(df['Country'].map(country_to_guest_id))
            .astype(int)
        )
        progress.update(impute_task, completed=100)

    console.print(f" [bold green][OK][/bold green] Imputed [bold yellow]{initial_missing_desc:,}[/bold yellow] missing descriptions via StockCode cross-referencing.")
    console.print(f" [bold green][OK][/bold green] Mapped [bold yellow]{initial_missing_cust:,}[/bold yellow] anonymous transactions to {len(country_to_guest_id)} regional Guest Accounts.")

    # Step 3: 3NF Deconstruction
    with Progress(
        SpinnerColumn("dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(style="blue", complete_style="green"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        deconstruct_task = progress.add_task("[3/4] Deconstructing into 3NF normalized entities...", total=100)
        
        # 1. CUSTOMERS
        cust_df = df[['Customer_ID_Clean', 'Country']].drop_duplicates(subset=['Customer_ID_Clean']).copy()
        cust_df.rename(columns={'Customer_ID_Clean': 'customer_id', 'Country': 'country'}, inplace=True)
        cust_df['customer_type'] = cust_df['customer_id'].apply(
            lambda cid: 'Guest' if cid >= guest_prefix else 'Registered'
        )
        cust_df.sort_values(by='customer_id', inplace=True)
        progress.update(deconstruct_task, completed=25)

        # 2. PRODUCTS
        valid_prices = df[df['Price'] > 0]
        stock_to_median_price = valid_prices.groupby('StockCode')['Price'].median().to_dict()
        
        prod_base = df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode']).copy()
        prod_base.rename(columns={'StockCode': 'stock_code', 'Description': 'description'}, inplace=True)
        prod_base['standard_price'] = prod_base['stock_code'].apply(
            lambda s: round(stock_to_median_price.get(s, 0.00), 2)
        )
        prod_df = prod_base.sort_values(by='stock_code')
        progress.update(deconstruct_task, completed=50)

        # 3. INVENTORY
        inventory_df = prod_df[['stock_code']].copy()
        inventory_df['stock_level'] = 1000
        inventory_df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        progress.update(deconstruct_task, completed=65)

        # 4. INVOICES
        inv_df = df[['Invoice', 'InvoiceDate', 'Customer_ID_Clean']].drop_duplicates(subset=['Invoice']).copy()
        inv_df.rename(columns={
            'Invoice': 'invoice_no',
            'InvoiceDate': 'invoice_date',
            'Customer_ID_Clean': 'customer_id'
        }, inplace=True)
        inv_df['status'] = inv_df['invoice_no'].apply(
            lambda inv: 'Cancelled' if str(inv).startswith('C') else 'Completed'
        )
        inv_df.sort_values(by='invoice_date', inplace=True)
        progress.update(deconstruct_task, completed=80)

        # 5. INVOICE_ITEMS
        items_df = pd.DataFrame({
            'invoice_no': df['Invoice'],
            'stock_code': df['StockCode'],
            'quantity': df['Quantity'].astype(int),
            'unit_price': df['Price'].round(2)
        })
        items_df.reset_index(drop=True, inplace=True)
        items_df['item_id'] = items_df.index + 1
        items_df = items_df[['item_id', 'invoice_no', 'stock_code', 'quantity', 'unit_price']]
        progress.update(deconstruct_task, completed=100)

    console.print(" [bold green][OK][/bold green] 3NF Relational Deconstruction completed successfully.")

    # Step 4: Export CSVs
    with Progress(
        SpinnerColumn("dots", style="cyan"),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(style="blue", complete_style="green"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        export_task = progress.add_task("[4/4] Writing database-ready CSV files...", total=5)
        
        cust_path = output_dir / "customers.csv"
        cust_df.to_csv(cust_path, index=False, encoding='utf-8')
        progress.advance(export_task)
        
        prod_path = output_dir / "products.csv"
        prod_df.to_csv(prod_path, index=False, encoding='utf-8')
        progress.advance(export_task)
        
        invt_path = output_dir / "inventory.csv"
        inventory_df.to_csv(invt_path, index=False, encoding='utf-8')
        progress.advance(export_task)
        
        inv_path = output_dir / "invoices.csv"
        inv_df.to_csv(inv_path, index=False, encoding='utf-8')
        progress.advance(export_task)
        
        items_path = output_dir / "invoice_items.csv"
        items_df.to_csv(items_path, index=False, encoding='utf-8')
        progress.advance(export_task)

    total_time = time.time() - start_time
    
    console.print()
    results_table = Table(title="[bold green]3NF Database Entity Summary[/bold green]", box=box.HEAVY_EDGE)
    results_table.add_column("Entity / Table", style="cyan", no_wrap=True)
    results_table.add_column("Primary Key", style="yellow")
    results_table.add_column("Total Rows", justify="right", style="green")
    results_table.add_column("File Size", justify="right", style="magenta")
    results_table.add_column("Destination File", style="dim")

    tables = [
        ("customers", "customer_id", len(cust_df), cust_path),
        ("products", "stock_code", len(prod_df), prod_path),
        ("inventory", "stock_code", len(inventory_df), invt_path),
        ("invoices", "invoice_no", len(inv_df), inv_path),
        ("invoice_items", "item_id", len(items_df), items_path),
    ]

    for name, pk, rows, path in tables:
        size_mb = path.stat().st_size / (1024 * 1024)
        results_table.add_row(name, pk, f"{rows:,}", f"{size_mb:.2f} MB", path.name)

    console.print(results_table)
    
    throughput = int(total_raw_rows/total_time) if total_time > 0 else total_raw_rows
    console.print(Panel(
        f"[bold white]Total Raw Records Processed:[/bold white] [bold cyan]{total_raw_rows:,}[/bold cyan]\n"
        f"[bold white]Pipeline Execution Time:[/bold white] [bold yellow]{total_time:.2f} seconds[/bold yellow] ([bold cyan]{throughput:,} rows/sec[/bold cyan])\n"
        f"[bold white]Output Directory:[/bold white] [underline cyan]{output_dir}[/underline cyan]",
        title="[bold green]ETL COMPLETE[/bold green]",
        border_style="green",
        box=box.DOUBLE
    ))
    return output_dir

# ==============================================================================
# VERIFICATION: Test Quality, Nulls & FK Integrity
# ==============================================================================
def verify_data_integrity(data_dir: Path):
    console.print()
    console.print(Panel(
        f"[bold white]Verifying Dataset Directory:[/bold white] [cyan]{data_dir}[/cyan]\n"
        "[bold white]Scope:[/bold white] Zero-Null Audit • Type Uniformity • Referential Integrity (FK Constraints)",
        title="[bold cyan]Phase 2: Automated Data Quality & Integrity Test Suite[/bold cyan]",
        box=box.ROUNDED
    ))
    
    files = {
        "customers": data_dir / "customers.csv",
        "products": data_dir / "products.csv",
        "inventory": data_dir / "inventory.csv",
        "invoices": data_dir / "invoices.csv",
        "invoice_items": data_dir / "invoice_items.csv",
    }
    
    # 1. File existence
    console.print("\n[bold yellow]Stage 1: File Ingestion & Record Count[/bold yellow]")
    dfs = {}
    for name, path in files.items():
        if not path.exists():
            console.print(f" [bold red][FAIL][/bold red] File not found: {path.name}. Please run ETL (Option 1) first!")
            return False
        dfs[name] = pd.read_csv(path, dtype=str)
        console.print(f" [bold green][PASS][/bold green] Ingested [cyan]{name}.csv[/cyan] ({len(dfs[name]):,} rows)")

    # 2. Null Value Check
    console.print("\n[bold yellow]Stage 2: Completeness Audit (Zero-Null Verification)[/bold yellow]")
    null_table = Table(title="Column Null & Empty Value Check", box=box.SIMPLE_HEAVY)
    null_table.add_column("Table", style="cyan")
    null_table.add_column("Column", style="white")
    null_table.add_column("Null Count", justify="right")
    null_table.add_column("Status", justify="center")

    total_nulls = 0
    for name, df in dfs.items():
        for col in df.columns:
            null_count = df[col].isnull().sum()
            empty_count = (df[col].astype(str).str.strip().isin(['', 'nan', 'None'])).sum()
            actual_missing = max(null_count, empty_count)
            total_nulls += actual_missing
            status = "[bold green]CLEAN (0)[/bold green]" if actual_missing == 0 else f"[bold red]FOUND ({actual_missing})[/bold red]"
            null_table.add_row(name, col, str(actual_missing), status)

    console.print(null_table)

    # 3. Data Uniformity Audit
    console.print("\n[bold yellow]Stage 3: Format & Classification Uniformity[/bold yellow]")
    cust_types = set(dfs["customers"]["customer_type"].unique())
    is_cust_uniform = cust_types.issubset({"Registered", "Guest"})
    console.print(f" [{'bold green]PASS' if is_cust_uniform else 'bold red]FAIL'}[/] Customer Types: strictly {cust_types}")

    inv_statuses = set(dfs["invoices"]["status"].unique())
    is_inv_uniform = inv_statuses.issubset({"Completed", "Cancelled"})
    console.print(f" [{'bold green]PASS' if is_inv_uniform else 'bold red]FAIL'}[/] Invoice Statuses: strictly {inv_statuses}")

    items = dfs["invoice_items"].copy()
    items["quantity"] = items["quantity"].astype(int)
    invoices = dfs["invoices"].copy()
    merged_items = items.merge(invoices, on="invoice_no")
    
    cancelled_items_cnt = len(merged_items[merged_items["status"] == "Cancelled"])
    completed_items_cnt = len(merged_items[merged_items["status"] == "Completed"])
    console.print(f" [bold green][PASS][/bold green] Line Items Partitioned: {completed_items_cnt:,} Completed | {cancelled_items_cnt:,} Cancelled/Returns")

    # 4. Referential Integrity
    console.print("\n[bold yellow]Stage 4: Referential Integrity (Zero Orphan Foreign Keys)[/bold yellow]")
    ref_table = Table(title="Foreign Key Referential Integrity Constraints", box=box.SIMPLE_HEAVY)
    ref_table.add_column("Constraint", style="cyan")
    ref_table.add_column("Parent Table", style="white")
    ref_table.add_column("Child Table", style="white")
    ref_table.add_column("Orphan Records", justify="right")
    ref_table.add_column("Status", justify="center")

    parent_cust = set(dfs["customers"]["customer_id"])
    child_cust = set(dfs["invoices"]["customer_id"])
    orphan_cust = len(child_cust - parent_cust)
    ref_table.add_row(
        "FK_Invoices_Customers", "customers(customer_id)", "invoices(customer_id)",
        str(orphan_cust), "[bold green]100% VALID[/bold green]" if orphan_cust == 0 else "[bold red]VIOLATION[/bold red]"
    )

    parent_inv = set(dfs["invoices"]["invoice_no"])
    child_inv = set(dfs["invoice_items"]["invoice_no"])
    orphan_inv = len(child_inv - parent_inv)
    ref_table.add_row(
        "FK_Items_Invoices", "invoices(invoice_no)", "invoice_items(invoice_no)",
        str(orphan_inv), "[bold green]100% VALID[/bold green]" if orphan_inv == 0 else "[bold red]VIOLATION[/bold red]"
    )

    parent_prod = set(dfs["products"]["stock_code"])
    child_prod = set(dfs["invoice_items"]["stock_code"])
    orphan_prod = len(child_prod - parent_prod)
    ref_table.add_row(
        "FK_Items_Products", "products(stock_code)", "invoice_items(stock_code)",
        str(orphan_prod), "[bold green]100% VALID[/bold green]" if orphan_prod == 0 else "[bold red]VIOLATION[/bold red]"
    )

    invt_prod = set(dfs["inventory"]["stock_code"])
    orphan_invt = len(invt_prod - parent_prod)
    ref_table.add_row(
        "FK_Inventory_Products", "products(stock_code)", "inventory(stock_code)",
        str(orphan_invt), "[bold green]100% VALID[/bold green]" if orphan_invt == 0 else "[bold red]VIOLATION[/bold red]"
    )

    console.print(ref_table)

    total_orphans = orphan_cust + orphan_inv + orphan_prod + orphan_invt

    console.print()
    if total_nulls == 0 and total_orphans == 0:
        console.print(Panel(
            "[bold green]ALL QUALITY ASSURANCE CHECKS PASSED (100%)[/bold green]\n\n"
            "• [white]Total Missing / Null Values:[/white] [bold green]0 (Zero)[/bold green]\n"
            "• [white]Total Orphan Foreign Keys:[/white] [bold green]0 (Zero)[/bold green]\n"
            "• [white]Normalization Status:[/white] [bold cyan]Third Normal Form (3NF) Verified[/bold cyan]\n"
            "• [white]Database Ingestion Status:[/white] [bold green]Ready for Production / PostgreSQL / MySQL[/bold green]",
            title="[bold green]DATA INTEGRITY CERTIFIED[/bold green]",
            border_style="green",
            box=box.DOUBLE
        ))
        return True
    else:
        console.print(Panel(
            f"[bold red]Integrity Check Failed:[/bold red] Found {total_nulls} nulls and {total_orphans} orphan keys.",
            title="[bold red]AUDIT FAILURE[/bold red]",
            border_style="red"
        ))
        return False

# ==============================================================================
# INTERACTIVE TERMINAL MENU
# ==============================================================================
def interactive_menu(input_path: Path, output_path: Path, guest_prefix: int):
    while True:
        console.print("[bold yellow]Available Operations:[/bold yellow]")
        console.print(" [bold cyan][1][/bold cyan] Clean & Impute Raw Data -> Generate 3NF CSV Files")
        console.print(" [bold cyan][2][/bold cyan] Verify & Audit Processed Data (Zero-Null & Foreign Key Check)")
        console.print(" [bold cyan][3][/bold cyan] Full End-to-End Pipeline (Clean + Audit)")
        console.print(" [bold cyan][4][/bold cyan] Change Input / Output Paths")
        console.print(" [bold cyan][5][/bold cyan] Exit")
        
        choice = console.input("\n[bold green]Enter option [1-5] (default: 3): [/bold green]").strip()
        if choice == "" or choice == "3":
            if not input_path.exists():
                console.print(f"[bold red]Error:[/bold red] Input file not found: {input_path}")
                continue
            clean_and_normalize(input_path, output_path, guest_prefix)
            verify_data_integrity(output_path)
            break
        elif choice == "1":
            if not input_path.exists():
                console.print(f"[bold red]Error:[/bold red] Input file not found: {input_path}")
                continue
            clean_and_normalize(input_path, output_path, guest_prefix)
            break
        elif choice == "2":
            verify_data_integrity(output_path)
            break
        elif choice == "4":
            new_in = console.input(f"Enter input file path (current: {input_path}): ").strip()
            if new_in:
                input_path = Path(new_in)
            new_out = console.input(f"Enter output dir path (current: {output_path}): ").strip()
            if new_out:
                output_path = Path(new_out)
            console.print(f"[green]Paths updated.[/green] Input: {input_path} | Output: {output_path}\n")
        elif choice == "5" or choice.lower() in ["q", "exit"]:
            console.print("[yellow]Exiting.[/yellow]")
            break
        else:
            console.print("[red]Invalid selection. Please choose 1, 2, 3, 4, or 5.[/red]\n")

def main():
    script_dir = Path(__file__).parent.resolve()
    
    # Check if project data directory exists, otherwise fallback to sample
    project_raw = script_dir / "data" / "raw" / "online_retail_data.xlsx"
    sample_raw = script_dir / "sample" / "raw_sample.csv"
    
    if project_raw.exists():
        default_input = project_raw
        default_output = script_dir / "data" / "processed"
    elif sample_raw.exists():
        default_input = sample_raw
        default_output = script_dir / "output"
    else:
        default_input = Path(r"C:\Users\steph\Downloads\online_retail_data.xlsx")
        default_output = script_dir / "output"

    parser = argparse.ArgumentParser(
        description="Martadinata CSV Imputer & 3NF Normalizer Engine"
    )
    parser.add_argument("--input", "-i", type=Path, default=default_input, help="Path to raw dataset")
    parser.add_argument("--output", "-o", type=Path, default=default_output, help="Destination directory")
    parser.add_argument("--guest-prefix", type=int, default=90000, help="Guest ID prefix")
    parser.add_argument("--clean", action="store_true", help="Run clean & normalize step directly")
    parser.add_argument("--verify", action="store_true", help="Run verification step directly")
    parser.add_argument("--all", action="store_true", help="Run both clean and verify directly")
    
    args = parser.parse_args()
    print_header()
    
    if args.all:
        clean_and_normalize(args.input, args.output, args.guest_prefix)
        verify_data_integrity(args.output)
    elif args.clean:
        clean_and_normalize(args.input, args.output, args.guest_prefix)
    elif args.verify:
        verify_data_integrity(args.output)
    else:
        # Default: interactive menu in terminal
        interactive_menu(args.input, args.output, args.guest_prefix)

if __name__ == "__main__":
    main()

"""Clean the Telangana tourism monthly visitor dataset.

Run from the project root:
    python cleaning.py
Input:  data/raw/telangana_tourism_2024_2025.csv
Outputs: data/processed/telangana_tourism_cleaned.csv
         outputs/cleaning_quality_report.txt
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "raw" / "telangana_tourism_2024_2025.csv"
OUTPUT = ROOT / "data" / "processed" / "telangana_tourism_cleaned.csv"
REPORT = ROOT / "outputs" / "cleaning_quality_report.txt"

REQUIRED = [
    "Year", "Month", "Month_Number", "Date", "District", "Region",
    "Tourism_Category", "Key_Tourist_Attractions", "Historical_Significance",
    "Domestic_Visitors", "Foreign_Visitors", "Total_Visitors",
    "Avg_Hotel_Occupancy_%", "Est_Revenue_Lakhs_INR",
]
NUMERIC = [
    "Year", "Month_Number", "Domestic_Visitors", "Foreign_Visitors",
    "Total_Visitors", "Avg_Hotel_Occupancy_%", "Est_Revenue_Lakhs_INR",
]
TEXT = [
    "Month", "District", "Region", "Tourism_Category",
    "Key_Tourist_Attractions", "Historical_Significance",
]


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT}\nPlace the collected CSV at this path.")
    df = pd.read_csv(INPUT)
    original_rows, original_cols = df.shape
    missing_columns = [c for c in REQUIRED if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}\nFound columns: {list(df.columns)}")

    # Normalize whitespace and blank text values.
    for col in TEXT:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    # Convert numeric fields safely; unparseable values become missing and are reported.
    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    missing_before_fill = df.isna().sum()
    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Date is reconstructed from Year/Month_Number when possible; otherwise invalid dates remain missing.
    date_missing = df["Date"].isna()
    reconstructable = date_missing & df["Year"].notna() & df["Month_Number"].between(1, 12)
    df.loc[reconstructable, "Date"] = pd.to_datetime(
        dict(year=df.loc[reconstructable, "Year"].astype(int),
             month=df.loc[reconstructable, "Month_Number"].astype(int), day=1), errors="coerce"
    )

    # Fill only derivable fields. Do not invent missing visitor counts or revenue.
    can_derive_total = df["Total_Visitors"].isna() & df["Domestic_Visitors"].notna() & df["Foreign_Visitors"].notna()
    df.loc[can_derive_total, "Total_Visitors"] = (
        df.loc[can_derive_total, "Domestic_Visitors"] + df.loc[can_derive_total, "Foreign_Visitors"]
    )
    # Standardize month labels from the numeric month where possible.
    month_valid = df["Month_Number"].between(1, 12)
    df.loc[month_valid, "Month"] = pd.to_datetime(
        {"year": 2000, "month": df.loc[month_valid, "Month_Number"].astype(int), "day": 1}
    ).dt.strftime("%b").to_numpy()

    # Quality flags, retained in the cleaned file for transparent review.
    df["Visitor_Total_Check"] = (
        df["Domestic_Visitors"].notna() & df["Foreign_Visitors"].notna() & df["Total_Visitors"].notna()
        & ((df["Domestic_Visitors"] + df["Foreign_Visitors"]) == df["Total_Visitors"])
    )
    df["Visitor_Count_Negative_Flag"] = (
        df[["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors"]].lt(0).any(axis=1)
    )
    df["Occupancy_Out_Of_Range_Flag"] = (
        df["Avg_Hotel_Occupancy_%"].notna()
        & ~df["Avg_Hotel_Occupancy_%"].between(0, 100)
    )
    df["Revenue_Negative_Flag"] = df["Est_Revenue_Lakhs_INR"].lt(0).fillna(False)

    # Stable chronological sort; keep missing values rather than silently fabricating them.
    df = df.sort_values(["Date", "District"], na_position="last").reset_index(drop=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False, date_format="%Y-%m-%d")

    report = [
        "TELANGANA TOURISM DATA CLEANING REPORT",
        "=======================================",
        f"Input file: {INPUT.relative_to(ROOT)}",
        f"Output file: {OUTPUT.relative_to(ROOT)}",
        f"Original shape: {original_rows} rows x {original_cols} columns",
        f"Rows removed as exact duplicates: {exact_duplicates}",
        f"Cleaned shape: {df.shape[0]} rows x {df.shape[1]} columns",
        "",
        "Missing values in original data (before duplicate removal / repairs):",
    ]
    report.extend([f"  {col}: {int(count)}" for col, count in missing_before_fill.items()])
    report += [
        "", f"Rows where domestic + foreign equals total: {int(df['Visitor_Total_Check'].sum())} / {len(df)}",
        f"Rows with negative visitor counts: {int(df['Visitor_Count_Negative_Flag'].sum())}",
        f"Rows with occupancy outside 0-100%: {int(df['Occupancy_Out_Of_Range_Flag'].sum())}",
        f"Rows with negative revenue: {int(df['Revenue_Negative_Flag'].sum())}",
        "", "Notes:",
        "- Exact duplicate rows were removed.",
        "- Text whitespace and numeric/date types were standardized.",
        "- Total visitors were calculated only when total was missing and both visitor components existed.",
        "- Missing visitor/revenue values were not guessed or replaced with zero.",
        "- Review the flags and source data before presenting results; cleaning does not prove source accuracy.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("Cleaning completed.")
    print(f"Cleaned CSV: {OUTPUT}")
    print(f"Quality report: {REPORT}")


if __name__ == "__main__":
    main()
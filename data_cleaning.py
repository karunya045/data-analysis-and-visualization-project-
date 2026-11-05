"""Clean the Telangana tourism CSV without silently replacing missing visitor counts."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "telangana_tourism_2024_2025.csv"
OUT_DIR = ROOT / "clean_dataset"
OUT_DIR.mkdir(exist_ok=True)
OUTPUT = OUT_DIR / "telangana_tourism_cleaned.csv"

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Dataset not found: {SOURCE}")
    df = pd.read_csv(SOURCE)
    df.columns = [c.strip().replace(" ", "_").replace("%", "percent").replace("(", "").replace(")", "") for c in df.columns]
    df = df.drop_duplicates().copy()

    numeric = ["Year", "Month_Number", "Domestic_Visitors", "Foreign_Visitors",
               "Total_Visitors", "Avg_Hotel_Occupancy_percent", "Est_Revenue_Lakhs_INR"]
    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["District", "Region", "Tourism_Category"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    required = [c for c in ["Year", "Month_Number", "District"] if c in df.columns]
    if required:
        df = df.dropna(subset=required)

    if {"Domestic_Visitors", "Foreign_Visitors"}.issubset(df.columns):
        calculated = df["Domestic_Visitors"] + df["Foreign_Visitors"]
        df["Visitor_Total_Check"] = calculated.eq(df["Total_Visitors"]) if "Total_Visitors" in df.columns else pd.NA

    df.to_csv(OUTPUT, index=False)
    print(f"Rows saved: {len(df)}")
    print(f"Cleaned dataset: {OUTPUT}")
    print("Missing values retained where source values were unavailable.")

if __name__ == "__main__":
    main()

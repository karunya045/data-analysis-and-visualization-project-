"""Generate summary tables from the cleaned Telangana tourism dataset."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "clean_dataset" / "telangana_tourism_cleaned.csv"
OUT = ROOT / "analysis_outputs"
OUT.mkdir(exist_ok=True)

def main():
    if not INPUT.exists():
        raise FileNotFoundError("Run data_cleaning.py first.")
    df = pd.read_csv(INPUT)
    for col in ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    metrics = []
    for col in ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"]:
        if col in df.columns:
            metrics.append({"Metric": col, "Sum": df[col].sum(min_count=1),
                            "Mean": df[col].mean(), "Maximum": df[col].max()})
    pd.DataFrame(metrics).to_csv(OUT / "key_metrics.csv", index=False)

    if "District" in df.columns:
        cols = [c for c in ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"] if c in df.columns]
        df.groupby("District", dropna=False)[cols].sum(min_count=1).sort_values(
            "Total_Visitors" if "Total_Visitors" in cols else cols[0], ascending=False
        ).to_csv(OUT / "district_summary.csv")

    if {"Year", "Month_Number"}.issubset(df.columns):
        cols = [c for c in ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"] if c in df.columns]
        df.groupby(["Year", "Month_Number"], dropna=False)[cols].sum(min_count=1).reset_index().sort_values(
            ["Year", "Month_Number"]).to_csv(OUT / "monthly_summary.csv", index=False)

    if "Tourism_Category" in df.columns:
        cols = [c for c in ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"] if c in df.columns]
        df.groupby("Tourism_Category", dropna=False)[cols].sum(min_count=1).to_csv(OUT / "category_summary.csv")
    print(f"Analysis tables saved in: {OUT}")

if __name__ == "__main__":
    main()

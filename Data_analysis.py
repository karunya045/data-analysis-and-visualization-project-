"""Analyze cleaned Telangana tourism monthly visitor data and export tables/charts.

Run after cleaning.py:
    python analysis.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "processed" / "telangana_tourism_cleaned.csv"
OUT = ROOT / "outputs" / "analysis"
FIG = ROOT / "outputs" / "figures"


def save_csv(df, name):
    df.to_csv(OUT / name, index=False)


def main():
    if not INPUT.exists():
        raise FileNotFoundError("Cleaned file not found. Run `python cleaning.py` first.")
    df = pd.read_csv(INPUT, parse_dates=["Date"])
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    # Avoid presenting sums as valid where key fields are missing; group totals are based on available rows.
    numeric = ["Domestic_Visitors", "Foreign_Visitors", "Total_Visitors", "Est_Revenue_Lakhs_INR"]
    df["International_Share_%"] = (df["Foreign_Visitors"] / df["Total_Visitors"].replace(0, pd.NA) * 100).round(2)
    df["Domestic_Share_%"] = (df["Domestic_Visitors"] / df["Total_Visitors"].replace(0, pd.NA) * 100).round(2)

    yearly = df.groupby("Year", dropna=False).agg(
        Domestic_Visitors=("Domestic_Visitors", "sum"),
        Foreign_Visitors=("Foreign_Visitors", "sum"),
        Total_Visitors=("Total_Visitors", "sum"),
        Avg_Hotel_Occupancy_Pct=("Avg_Hotel_Occupancy_%", "mean"),
        Est_Revenue_Lakhs_INR=("Est_Revenue_Lakhs_INR", "sum"),
        Records=("District", "size"),
    ).reset_index()
    yearly["Avg_Hotel_Occupancy_Pct"] = yearly["Avg_Hotel_Occupancy_Pct"].round(2)
    save_csv(yearly, "yearly_summary.csv")

    monthly = df.groupby(["Month_Number", "Month"], dropna=False).agg(
        Domestic_Visitors=("Domestic_Visitors", "sum"),
        Foreign_Visitors=("Foreign_Visitors", "sum"),
        Total_Visitors=("Total_Visitors", "sum"),
        Est_Revenue_Lakhs_INR=("Est_Revenue_Lakhs_INR", "sum"),
        Avg_Hotel_Occupancy_Pct=("Avg_Hotel_Occupancy_%", "mean"),
    ).reset_index().sort_values("Month_Number")
    monthly["Avg_Hotel_Occupancy_Pct"] = monthly["Avg_Hotel_Occupancy_Pct"].round(2)
    save_csv(monthly, "monthly_summary.csv")

    district = df.groupby(["District", "Region"], dropna=False).agg(
        Domestic_Visitors=("Domestic_Visitors", "sum"),
        Foreign_Visitors=("Foreign_Visitors", "sum"),
        Total_Visitors=("Total_Visitors", "sum"),
        Avg_Hotel_Occupancy_Pct=("Avg_Hotel_Occupancy_%", "mean"),
        Est_Revenue_Lakhs_INR=("Est_Revenue_Lakhs_INR", "sum"),
        Months_Recorded=("Date", "nunique"),
    ).reset_index().sort_values("Total_Visitors", ascending=False)
    district["Avg_Hotel_Occupancy_Pct"] = district["Avg_Hotel_Occupancy_Pct"].round(2)
    save_csv(district, "district_summary.csv")

    category = df.groupby("Tourism_Category", dropna=False).agg(
        Domestic_Visitors=("Domestic_Visitors", "sum"),
        Foreign_Visitors=("Foreign_Visitors", "sum"),
        Total_Visitors=("Total_Visitors", "sum"),
        Est_Revenue_Lakhs_INR=("Est_Revenue_Lakhs_INR", "sum"),
        Records=("District", "size"),
    ).reset_index().sort_values("Total_Visitors", ascending=False)
    save_csv(category, "category_summary.csv")

    # Compact KPI report for GitHub and presentation notes.
    total_domestic = df["Domestic_Visitors"].sum()
    total_foreign = df["Foreign_Visitors"].sum()
    total_visitors = df["Total_Visitors"].sum()
    total_revenue = df["Est_Revenue_Lakhs_INR"].sum()
    top_district = district.iloc[0] if not district.empty else None
    peak_month = monthly.loc[monthly["Total_Visitors"].idxmax()] if not monthly.empty else None
    report = [
        "TELANGANA TOURISM — EXPLORATORY ANALYSIS SUMMARY",
        "=================================================",
        f"Records analyzed: {len(df)}",
        f"Date range: {df['Date'].min().date() if df['Date'].notna().any() else 'N/A'} to {df['Date'].max().date() if df['Date'].notna().any() else 'N/A'}",
        f"Districts represented: {df['District'].nunique(dropna=True)}",
        f"Total domestic visitors (sum of monthly district records): {total_domestic:,.0f}",
        f"Total foreign visitors (sum of monthly district records): {total_foreign:,.0f}",
        f"Total visitors (sum of monthly district records): {total_visitors:,.0f}",
        f"Estimated revenue (sum of monthly district records, INR lakhs): {total_revenue:,.2f}",
        f"Foreign visitor share of total: {(total_foreign / total_visitors * 100):.2f}%" if total_visitors else "Foreign visitor share of total: N/A",
    ]
    if top_district is not None:
        report.append(f"Highest visitor total by district over the period: {top_district['District']} ({top_district['Total_Visitors']:,.0f})")
    if peak_month is not None:
        report.append(f"Highest aggregate month: {peak_month['Month']} (month number {int(peak_month['Month_Number'])}) — {peak_month['Total_Visitors']:,.0f} visitors")
    report += [
        "", "Interpretation cautions:",
        "- These totals are sums of monthly district records, not unique individual tourists.",
        "- District and category totals depend on the accuracy and definitions in the supplied dataset.",
        "- Key_Tourist_Attractions is a descriptive text field, not a per-attraction visitor count; do not rank individual places from it.",
        "- Validate figures against authoritative sources before treating them as official statistics.",
    ]
    (OUT / "kpi_summary.txt").write_text("\n".join(report) + "\n", encoding="utf-8")

    # Charts use default matplotlib styling.
    if not monthly.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly["Month"], monthly["Total_Visitors"], marker="o")
        ax.set_title("Telangana Tourism: Monthly Visitor Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Visitors (sum across district-month records)")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        fig.savefig(FIG / "monthly_visitor_trend.png", dpi=160)
        plt.close(fig)
    if not district.empty:
        top = district.head(10).sort_values("Total_Visitors")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top["District"], top["Total_Visitors"])
        ax.set_title("Top Districts by Recorded Visitor Total")
        ax.set_xlabel("Visitors (sum across monthly records)")
        ax.set_ylabel("District")
        fig.tight_layout()
        fig.savefig(FIG / "top_districts_visitors.png", dpi=160)
        plt.close(fig)

    print(f"Analysis complete. Tables and KPI report saved to: {OUT}")
    print(f"Charts saved to: {FIG}")


if __name__ == "__main__":
    main()
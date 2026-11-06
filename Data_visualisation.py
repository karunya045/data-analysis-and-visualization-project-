"""Data visualisation for the Telangana Tourism Analysis project.

Input: cleaned_telangana_tourism_with_latitude_longitude.csv
Output: PNG charts saved in a folder named 'visualizations'.

Keep this script in the same folder as the cleaned CSV, or pass a CSV path:
    python Data_visualisation.py "clean_dataset.csv"
"""
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt


def find_dataset():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1]).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        return path

    candidates = [
        Path(__file__).parent / "clean_dataset.csv",
        Path(__file__).parent / "cleaned_telangana_tourism_with_latitude_longitude.csv",
        Path(__file__).parent / "cleaned_Telangana_Tourism_with_Coordinates.csv",
        Path(__file__).parent / "Telangana_Tourism_Cleaned_Week_3.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not find the cleaned CSV. Put it beside this script as "
        "'clean_dataset.csv', or run: python Data_visualisation.py path/to/file.csv"
    )


def main():
    csv_path = find_dataset()
    df = pd.read_csv(csv_path)
    df.columns = [str(c).strip() for c in df.columns]
    output_dir = Path(__file__).parent / "visualizations"
    output_dir.mkdir(exist_ok=True)

    # Support both project dataset formats: monthly visitor analysis and place catalogue.
    visitor_required = {"district", "domestic_visitors", "foreign_visitors", "total_visitors"}
    place_required = {"District", "Place", "Place_Type", "Category"}

    if place_required.issubset(df.columns) and not visitor_required.issubset(df.columns):
        # Place catalogue visualisations (district/place/category fields; no visitor counts).
        df["District"] = df["District"].astype("string").str.strip()
        df["Place_Type"] = df["Place_Type"].astype("string").str.strip()
        df["Category"] = df["Category"].astype("string").str.strip()

        counts = df.groupby("District")["Place"].count().sort_values(ascending=False).head(10)
        plt.figure(figsize=(11, 6))
        counts.sort_values().plot(kind="barh")
        plt.title("Top 10 Districts by Listed Tourist Places")
        plt.xlabel("Number of listed places")
        plt.ylabel("District")
        plt.tight_layout()
        plt.savefig(output_dir / "01_top_districts_by_places.png", dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_dir / '01_top_districts_by_places.png'}")

        type_counts = df["Place_Type"].value_counts(dropna=True)
        plt.figure(figsize=(7, 7))
        plt.pie(type_counts, labels=type_counts.index, autopct="%1.1f%%", startangle=90)
        plt.title("Listed Places by Place Type")
        plt.axis("equal")
        plt.tight_layout()
        plt.savefig(output_dir / "02_places_by_type.png", dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_dir / '02_places_by_type.png'}")

        categories = df["Category"].value_counts(dropna=True).head(10)
        plt.figure(figsize=(10, 6))
        categories.sort_values().plot(kind="barh")
        plt.title("Top Categories of Listed Tourist Places")
        plt.xlabel("Number of places")
        plt.ylabel("Category")
        plt.tight_layout()
        plt.savefig(output_dir / "03_places_by_category.png", dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_dir / '03_places_by_category.png'}")

        print("\nPlace-catalogue visualizations completed successfully.")
        print(f"Input dataset: {csv_path}")
        print(f"Charts folder: {output_dir}")
        print("Note: these charts count listed destinations; they do not represent visitor numbers.")
        return

    if not visitor_required.issubset(df.columns):
        raise ValueError(
            "CSV format not recognized. Expected either the monthly visitor dataset "
            "(district, domestic_visitors, foreign_visitors, total_visitors) or place catalogue "
            "(District, Place, Place_Type, Category). Found columns: " + ", ".join(df.columns)
        )

    numeric_cols = [
        "year", "month_number", "domestic_visitors", "foreign_visitors",
        "total_visitors", "avg_hotel_occupancy", "est_revenue_lakhs_inr"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    def save_chart(filename):
        plt.tight_layout()
        plt.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_dir / filename}")

    # 1. District-wise visitor totals
    district = df.groupby("district", dropna=True)["total_visitors"].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(11, 6))
    district.sort_values().plot(kind="barh")
    plt.title("Top 10 District Areas by Total Visitors")
    plt.xlabel("Total visitors (sum across available records)")
    plt.ylabel("District / area")
    save_chart("01_top_districts_by_visitors.png")

    # 2. Monthly visitor trend across years
    if {"year", "month_number", "month"}.issubset(df.columns):
        trend = df.groupby(["year", "month_number", "month"], dropna=True)["total_visitors"].sum().reset_index()
        trend = trend.sort_values(["year", "month_number"])
        plt.figure(figsize=(12, 6))
        for year, part in trend.groupby("year"):
            plt.plot(part["month"], part["total_visitors"], marker="o", label=str(int(year)) if pd.notna(year) else "Unknown year")
        plt.title("Monthly Tourism Visitor Trend")
        plt.xlabel("Month")
        plt.ylabel("Total visitors")
        plt.xticks(rotation=35)
        plt.legend(title="Year")
        save_chart("02_monthly_visitor_trend.png")

    # 3. Domestic vs foreign visitors
    visitor_mix = pd.Series({
        "Domestic visitors": df["domestic_visitors"].sum(),
        "Foreign visitors": df["foreign_visitors"].sum(),
    }).dropna()
    plt.figure(figsize=(7, 7))
    plt.pie(visitor_mix, labels=visitor_mix.index, autopct="%1.1f%%", startangle=90)
    plt.title("Domestic vs Foreign Visitor Share")
    plt.axis("equal")
    save_chart("03_domestic_vs_foreign_share.png")

    # 4. Revenue by district/area, if present
    if "est_revenue_lakhs_inr" in df.columns:
        revenue = df.groupby("district", dropna=True)["est_revenue_lakhs_inr"].sum().sort_values(ascending=False).head(10)
        plt.figure(figsize=(11, 6))
        revenue.sort_values().plot(kind="barh")
        plt.title("Top 10 District Areas by Estimated Tourism Revenue")
        plt.xlabel("Estimated revenue (₹ lakh; summed records)")
        plt.ylabel("District / area")
        save_chart("04_top_districts_by_revenue.png")

    # 5. Tourism category by visitors, if present
    if "tourism_category" in df.columns:
        category = df.groupby("tourism_category", dropna=True)["total_visitors"].sum().sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        category.plot(kind="bar")
        plt.title("Visitors by Tourism Category")
        plt.xlabel("Tourism category")
        plt.ylabel("Total visitors")
        plt.xticks(rotation=30, ha="right")
        save_chart("05_visitors_by_category.png")

    # 6. Average hotel occupancy, if present
    if "avg_hotel_occupancy" in df.columns:
        occupancy = df.groupby("district", dropna=True)["avg_hotel_occupancy"].mean().sort_values(ascending=False).head(10)
        plt.figure(figsize=(11, 6))
        occupancy.sort_values().plot(kind="barh")
        plt.title("Top 10 District Areas by Average Hotel Occupancy")
        plt.xlabel("Average hotel occupancy (%)")
        plt.ylabel("District / area")
        save_chart("06_hotel_occupancy_by_district.png")

    print("\nVisualization completed successfully.")
    print(f"Input dataset: {csv_path}")
    print(f"Charts folder: {output_dir}")
    print("Note: revenue/visitor fields should be described according to the source and methodology in your report.")


if __name__ == "__main__":
    main()
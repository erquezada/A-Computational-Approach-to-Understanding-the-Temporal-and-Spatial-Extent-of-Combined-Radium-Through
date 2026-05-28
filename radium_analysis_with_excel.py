#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd


MCL_DEFAULT = 5.0

# Default paths for the Excel file uploaded in this ChatGPT session.
# Change these if you move the script or Excel file to another folder.
DEFAULT_INPUT_FILE = Path(__file__).with_name("filtered_annual_maximum_radium.xlsx")
DEFAULT_OUTPUT_DIR = Path(__file__).with_name("analysis_outputs")


def clean_column_names(data: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to easier snake_case names."""
    renamed = {
        col: (
            col.strip()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_per_")
            .replace("-", "_")
            .lower()
        )
        for col in data.columns
    }
    return data.rename(columns=renamed)


def load_data(input_path: Path, sheet_name: Union[str, int] = 0) -> pd.DataFrame:
    """Load and clean the radium Excel dataset."""
    data = pd.read_excel(input_path, sheet_name=sheet_name)
    data = clean_column_names(data)

    required_columns = [
        "wi_unique_well_no",
        "measured_amount",
        "sample_date",
        "year",
        "county",
        "region",
        "first_bedrock_ft",
        "maximum_contaminant_limit_mcl",
    ]

    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data["sample_date"] = pd.to_datetime(data["sample_date"], errors="coerce")
    data["measured_amount"] = pd.to_numeric(data["measured_amount"], errors="coerce")
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data["first_bedrock_ft"] = pd.to_numeric(data["first_bedrock_ft"], errors="coerce")
    data["maximum_contaminant_limit_mcl"] = pd.to_numeric(
        data["maximum_contaminant_limit_mcl"], errors="coerce"
    )

    data = data.dropna(subset=["sample_date", "measured_amount", "year"])
    data["year"] = data["year"].astype(int)

    data["mcl"] = data["maximum_contaminant_limit_mcl"].fillna(MCL_DEFAULT)
    data["exceeds_mcl"] = data["measured_amount"] > data["mcl"]

    return data.sort_values(["year", "sample_date"]).reset_index(drop=True)


def save_summary_tables(data: pd.DataFrame, output_dir: Path) -> None:
    """Save useful summary tables as CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    overall_summary = pd.DataFrame(
        {
            "metric": [
                "rows",
                "unique_wells",
                "start_year",
                "end_year",
                "mean_radium",
                "median_radium",
                "max_radium",
                "mcl",
                "exceedance_count",
                "exceedance_rate",
            ],
            "value": [
                len(data),
                data["wi_unique_well_no"].nunique(),
                data["year"].min(),
                data["year"].max(),
                data["measured_amount"].mean(),
                data["measured_amount"].median(),
                data["measured_amount"].max(),
                data["mcl"].median(),
                int(data["exceeds_mcl"].sum()),
                data["exceeds_mcl"].mean(),
            ],
        }
    )

    annual_summary = (
        data.groupby("year")
        .agg(
            samples=("measured_amount", "size"),
            unique_wells=("wi_unique_well_no", "nunique"),
            mean_radium=("measured_amount", "mean"),
            median_radium=("measured_amount", "median"),
            max_radium=("measured_amount", "max"),
            exceedance_count=("exceeds_mcl", "sum"),
            exceedance_rate=("exceeds_mcl", "mean"),
        )
        .reset_index()
    )

    county_summary = (
        data.groupby("county")
        .agg(
            samples=("measured_amount", "size"),
            unique_wells=("wi_unique_well_no", "nunique"),
            mean_radium=("measured_amount", "mean"),
            median_radium=("measured_amount", "median"),
            max_radium=("measured_amount", "max"),
            exceedance_count=("exceeds_mcl", "sum"),
            exceedance_rate=("exceeds_mcl", "mean"),
        )
        .sort_values(["mean_radium", "samples"], ascending=[False, False])
        .reset_index()
    )

    region_summary = (
        data.groupby("region")
        .agg(
            samples=("measured_amount", "size"),
            unique_wells=("wi_unique_well_no", "nunique"),
            mean_radium=("measured_amount", "mean"),
            median_radium=("measured_amount", "median"),
            max_radium=("measured_amount", "max"),
            exceedance_count=("exceeds_mcl", "sum"),
            exceedance_rate=("exceeds_mcl", "mean"),
        )
        .sort_values("mean_radium", ascending=False)
        .reset_index()
    )

    overall_summary.to_csv(output_dir / "overall_summary.csv", index=False)
    annual_summary.to_csv(output_dir / "annual_summary.csv", index=False)
    county_summary.to_csv(output_dir / "county_summary.csv", index=False)
    region_summary.to_csv(output_dir / "region_summary.csv", index=False)


def save_plot(fig: plt.Figure, output_path: Path) -> None:
    """Save and close a matplotlib figure."""
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_annual_trend(data: pd.DataFrame, output_dir: Path) -> None:
    annual = (
        data.groupby("year")
        .agg(
            mean_radium=("measured_amount", "mean"),
            median_radium=("measured_amount", "median"),
            max_radium=("measured_amount", "max"),
        )
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(annual["year"], annual["mean_radium"], marker="o", label="Mean")
    ax.plot(annual["year"], annual["median_radium"], marker="o", label="Median")
    ax.plot(annual["year"], annual["max_radium"], marker="o", label="Maximum")
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Annual Radium Trend")
    ax.set_xlabel("Year")
    ax.set_ylabel("Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "annual_radium_trend.png")


def plot_exceedance_rate(data: pd.DataFrame, output_dir: Path) -> None:
    annual = (
        data.groupby("year")
        .agg(exceedance_rate=("exceeds_mcl", "mean"), samples=("exceeds_mcl", "size"))
        .reset_index()
    )
    annual["exceedance_rate_percent"] = annual["exceedance_rate"] * 100

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(annual["year"], annual["exceedance_rate_percent"])
    ax.set_title("Annual MCL Exceedance Rate")
    ax.set_xlabel("Year")
    ax.set_ylabel("Samples Above MCL (%)")
    ax.grid(axis="y", alpha=0.3)
    save_plot(fig, output_dir / "annual_mcl_exceedance_rate.png")


def plot_distribution(data: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data["measured_amount"], bins=30, edgecolor="black")
    ax.axvline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Distribution of Combined Radium Measurements")
    ax.set_xlabel("Combined Radium (pCi/L)")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save_plot(fig, output_dir / "radium_distribution.png")


def plot_top_counties(data: pd.DataFrame, output_dir: Path, min_samples: int = 5) -> None:
    county = (
        data.groupby("county")
        .agg(samples=("measured_amount", "size"), mean_radium=("measured_amount", "mean"))
        .query("samples >= @min_samples")
        .sort_values("mean_radium", ascending=False)
        .head(15)
        .sort_values("mean_radium")
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(county.index, county["mean_radium"])
    ax.axvline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title(f"Top Counties by Mean Radium, Minimum {min_samples} Samples")
    ax.set_xlabel("Mean Combined Radium (pCi/L)")
    ax.set_ylabel("County")
    ax.legend()
    ax.grid(axis="x", alpha=0.3)
    save_plot(fig, output_dir / "top_counties_by_mean_radium.png")


def plot_region_comparison(data: pd.DataFrame, output_dir: Path) -> None:
    region = (
        data.groupby("region")
        .agg(mean_radium=("measured_amount", "mean"))
        .sort_values("mean_radium")
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(region.index, region["mean_radium"])
    ax.axvline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Mean Radium by Region")
    ax.set_xlabel("Mean Combined Radium (pCi/L)")
    ax.set_ylabel("Region")
    ax.legend()
    ax.grid(axis="x", alpha=0.3)
    save_plot(fig, output_dir / "mean_radium_by_region.png")


def plot_bedrock_vs_radium(data: pd.DataFrame, output_dir: Path) -> None:
    plot_data = data.dropna(subset=["first_bedrock_ft", "measured_amount"])

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(plot_data["first_bedrock_ft"], plot_data["measured_amount"], alpha=0.6)
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Bedrock Depth vs. Radium")
    ax.set_xlabel("First Bedrock Depth (ft)")
    ax.set_ylabel("Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "bedrock_depth_vs_radium.png")


def plot_boxplot_by_year(data: pd.DataFrame, output_dir: Path) -> None:
    years = sorted(data["year"].dropna().unique())
    grouped = [data.loc[data["year"] == year, "measured_amount"] for year in years]

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.boxplot(grouped, labels=years, showfliers=False)
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Radium Distribution by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Combined Radium (pCi/L)")
    ax.tick_params(axis="x", rotation=90)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save_plot(fig, output_dir / "radium_boxplot_by_year.png")


def write_text_report(data: pd.DataFrame, output_dir: Path) -> None:
    exceedance_rate = data["exceeds_mcl"].mean() * 100
    report = f"""
Radium Data Analysis Report
===========================

Rows analyzed: {len(data):,}
Unique wells: {data['wi_unique_well_no'].nunique():,}
Year range: {data['year'].min()}-{data['year'].max()}

Combined Radium Summary
-----------------------
Mean: {data['measured_amount'].mean():.3f} pCi/L
Median: {data['measured_amount'].median():.3f} pCi/L
Minimum: {data['measured_amount'].min():.3f} pCi/L
Maximum: {data['measured_amount'].max():.3f} pCi/L

MCL Analysis
------------
MCL used: {MCL_DEFAULT:.1f} pCi/L
Samples above MCL: {int(data['exceeds_mcl'].sum()):,}
Exceedance rate: {exceedance_rate:.2f}%

Top 10 Counties by Mean Radium
------------------------------
{data.groupby('county')['measured_amount'].mean().sort_values(ascending=False).head(10).to_string()}

Top 10 Years by Mean Radium
---------------------------
{data.groupby('year')['measured_amount'].mean().sort_values(ascending=False).head(10).to_string()}
""".strip()

    (output_dir / "analysis_report.txt").write_text(report, encoding="utf-8")


def run_analysis(input_path: Path, output_dir: Path, sheet_name: Union[str, int] = 0) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_data(input_path, sheet_name=sheet_name)

    cleaned_path = output_dir / "cleaned_radium_data.csv"
    data.to_csv(cleaned_path, index=False)

    save_summary_tables(data, output_dir)
    write_text_report(data, output_dir)

    plot_annual_trend(data, output_dir)
    plot_exceedance_rate(data, output_dir)
    plot_distribution(data, output_dir)
    plot_top_counties(data, output_dir)
    plot_region_comparison(data, output_dir)
    plot_bedrock_vs_radium(data, output_dir)
    plot_boxplot_by_year(data, output_dir)

    print(f"Analysis complete.")
    print(f"Input file: {input_path}")
    print(f"Output folder: {output_dir}")
    print(f"Rows analyzed: {len(data):,}")
    print(f"Unique wells: {data['wi_unique_well_no'].nunique():,}")
    print(f"Year range: {data['year'].min()}-{data['year'].max()}")
    print(f"Samples above MCL: {int(data['exceeds_mcl'].sum()):,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze radium Excel data.")
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help="Path to the Excel input file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Folder where tables, report, and plots will be saved.",
    )
    parser.add_argument(
        "--sheet",
        default=0,
        help="Excel sheet name or index. Default is the first sheet.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # argparse returns sheet values as strings. Convert numeric sheet indexes like "0" to int.
    sheet_name: Union[str, int]
    if isinstance(args.sheet, str) and args.sheet.isdigit():
        sheet_name = int(args.sheet)
    else:
        sheet_name = args.sheet

    run_analysis(
        input_path=args.input,
        output_dir=args.output,
        sheet_name=sheet_name,
    )


if __name__ == "__main__":
    main()
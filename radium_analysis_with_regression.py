#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


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



def add_regression_features(data: pd.DataFrame) -> pd.DataFrame:
    """Add numeric variables used by the regression models."""
    data = data.copy()
    data["sample_year_decimal"] = (
        data["sample_date"].dt.year
        + (data["sample_date"].dt.dayofyear - 1) / 365.25
    )
    data["year_centered"] = data["sample_year_decimal"] - data["sample_year_decimal"].mean()
    data["log_measured_amount"] = pd.NA

    positive_mask = data["measured_amount"] > 0
    data.loc[positive_mask, "log_measured_amount"] = data.loc[
        positive_mask, "measured_amount"
    ].apply(lambda value: pd.NA if pd.isna(value) else __import__("math").log(value))
    data["log_measured_amount"] = pd.to_numeric(data["log_measured_amount"], errors="coerce")
    return data


def regression_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    """Return common regression metrics."""
    residuals = actual - predicted
    ss_res = float((residuals ** 2).sum())
    ss_tot = float(((actual - actual.mean()) ** 2).sum())
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else float("nan")
    rmse = float((residuals ** 2).mean() ** 0.5)
    mae = float(residuals.abs().mean())
    return {
        "r_squared": r_squared,
        "rmse": rmse,
        "mae": mae,
    }


def save_time_regression(data: pd.DataFrame, output_dir: Path) -> None:
    """Fit and save a simple time-trend regression: radium ~ year."""
    model_data = data.dropna(subset=["measured_amount", "sample_year_decimal", "year_centered"]).copy()

    x = sm.add_constant(model_data["year_centered"])
    y = model_data["measured_amount"]
    model = sm.OLS(y, x).fit()
    model_data["predicted_radium_time_model"] = model.predict(x)

    coefficient_table = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "p_value": model.pvalues.values,
            "std_error": model.bse.values,
            "confidence_interval_low": model.conf_int()[0].values,
            "confidence_interval_high": model.conf_int()[1].values,
        }
    )
    coefficient_table.to_csv(output_dir / "time_regression_coefficients.csv", index=False)

    metrics = regression_metrics(y, model_data["predicted_radium_time_model"])
    pd.DataFrame([metrics]).to_csv(output_dir / "time_regression_metrics.csv", index=False)

    (output_dir / "time_regression_summary.txt").write_text(model.summary().as_text(), encoding="utf-8")

    # Plot individual samples plus fitted regression line.
    plot_data = model_data.sort_values("sample_year_decimal")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(plot_data["sample_year_decimal"], plot_data["measured_amount"], alpha=0.45, label="Samples")
    ax.plot(
        plot_data["sample_year_decimal"],
        plot_data["predicted_radium_time_model"],
        linewidth=2,
        label="OLS regression line",
    )
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Linear Regression: Radium Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "time_regression_radium_over_time.png")

    # Plot annual means with fitted regression line for a cleaner trend view.
    annual = (
        model_data.groupby("year")
        .agg(mean_radium=("measured_amount", "mean"), mean_year_decimal=("sample_year_decimal", "mean"))
        .reset_index()
    )
    annual["year_centered"] = annual["mean_year_decimal"] - model_data["sample_year_decimal"].mean()
    annual_x = sm.add_constant(annual["year_centered"])
    annual["predicted_radium"] = model.predict(annual_x)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(annual["year"], annual["mean_radium"], label="Annual mean")
    ax.plot(annual["year"], annual["predicted_radium"], linewidth=2, label="OLS regression line")
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Linear Regression on Annual Mean Radium")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "time_regression_annual_mean.png")

    # Residuals plot.
    residuals = model_data["measured_amount"] - model_data["predicted_radium_time_model"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(model_data["predicted_radium_time_model"], residuals, alpha=0.5)
    ax.axhline(0, linestyle="--")
    ax.set_title("Time Regression Residuals")
    ax.set_xlabel("Predicted Combined Radium (pCi/L)")
    ax.set_ylabel("Residual")
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "time_regression_residuals.png")


def save_bedrock_regression(data: pd.DataFrame, output_dir: Path) -> None:
    """Fit and save a simple regression: radium ~ first bedrock depth."""
    model_data = data.dropna(subset=["measured_amount", "first_bedrock_ft"]).copy()
    if len(model_data) < 2:
        (output_dir / "bedrock_regression_summary.txt").write_text(
            "Not enough non-missing bedrock depth data to fit a regression model.",
            encoding="utf-8",
        )
        return

    x = sm.add_constant(model_data["first_bedrock_ft"])
    y = model_data["measured_amount"]
    model = sm.OLS(y, x).fit()
    model_data["predicted_radium_bedrock_model"] = model.predict(x)

    coefficient_table = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "p_value": model.pvalues.values,
            "std_error": model.bse.values,
            "confidence_interval_low": model.conf_int()[0].values,
            "confidence_interval_high": model.conf_int()[1].values,
        }
    )
    coefficient_table.to_csv(output_dir / "bedrock_regression_coefficients.csv", index=False)

    metrics = regression_metrics(y, model_data["predicted_radium_bedrock_model"])
    pd.DataFrame([metrics]).to_csv(output_dir / "bedrock_regression_metrics.csv", index=False)

    (output_dir / "bedrock_regression_summary.txt").write_text(model.summary().as_text(), encoding="utf-8")

    plot_data = model_data.sort_values("first_bedrock_ft")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(plot_data["first_bedrock_ft"], plot_data["measured_amount"], alpha=0.5, label="Samples")
    ax.plot(
        plot_data["first_bedrock_ft"],
        plot_data["predicted_radium_bedrock_model"],
        linewidth=2,
        label="OLS regression line",
    )
    ax.axhline(MCL_DEFAULT, linestyle="--", label="MCL = 5 pCi/L")
    ax.set_title("Linear Regression: Bedrock Depth vs. Radium")
    ax.set_xlabel("First Bedrock Depth (ft)")
    ax.set_ylabel("Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "bedrock_regression.png")


def save_multiple_regression(data: pd.DataFrame, output_dir: Path) -> None:
    """Fit a multiple regression model using year, bedrock depth, and region."""
    model_data = data.dropna(
        subset=["measured_amount", "year_centered", "first_bedrock_ft", "region"]
    ).copy()

    if len(model_data) < 5 or model_data["region"].nunique() < 2:
        (output_dir / "multiple_regression_summary.txt").write_text(
            "Not enough complete rows or region variety to fit the multiple regression model.",
            encoding="utf-8",
        )
        return

    model = smf.ols(
        formula="measured_amount ~ year_centered + first_bedrock_ft + C(region)",
        data=model_data,
    ).fit()

    model_data["predicted_radium_multiple_model"] = model.predict(model_data)

    coefficient_table = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "p_value": model.pvalues.values,
            "std_error": model.bse.values,
            "confidence_interval_low": model.conf_int()[0].values,
            "confidence_interval_high": model.conf_int()[1].values,
        }
    )
    coefficient_table.to_csv(output_dir / "multiple_regression_coefficients.csv", index=False)

    metrics = regression_metrics(model_data["measured_amount"], model_data["predicted_radium_multiple_model"])
    pd.DataFrame([metrics]).to_csv(output_dir / "multiple_regression_metrics.csv", index=False)

    (output_dir / "multiple_regression_summary.txt").write_text(model.summary().as_text(), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        model_data["measured_amount"],
        model_data["predicted_radium_multiple_model"],
        alpha=0.5,
    )
    min_value = min(model_data["measured_amount"].min(), model_data["predicted_radium_multiple_model"].min())
    max_value = max(model_data["measured_amount"].max(), model_data["predicted_radium_multiple_model"].max())
    ax.plot([min_value, max_value], [min_value, max_value], linestyle="--", label="Perfect prediction")
    ax.set_title("Multiple Regression: Actual vs. Predicted Radium")
    ax.set_xlabel("Actual Combined Radium (pCi/L)")
    ax.set_ylabel("Predicted Combined Radium (pCi/L)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    save_plot(fig, output_dir / "multiple_regression_actual_vs_predicted.png")


def save_regression_models(data: pd.DataFrame, output_dir: Path) -> None:
    """Run all regression models and save their results."""
    regression_dir = output_dir / "regression"
    regression_dir.mkdir(parents=True, exist_ok=True)

    regression_data = add_regression_features(data)
    regression_data.to_csv(regression_dir / "regression_ready_data.csv", index=False)

    save_time_regression(regression_data, regression_dir)
    save_bedrock_regression(regression_data, regression_dir)
    save_multiple_regression(regression_data, regression_dir)

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

Regression Outputs
------------------
Regression models are saved in the regression folder inside the output directory.
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
    save_regression_models(data, output_dir)

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
    args, _unknown = parser.parse_known_args()
    return args


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
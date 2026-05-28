# A Computational Approach to Understanding the Temporal and Spatial Extent of Combined Radium Through Wisconsin’s Cambrian-Ordovician Aquifer System

This repository contains a computational groundwater research workflow for analyzing combined radium measurements in Wisconsin wells, with emphasis on the Cambrian-Ordovician aquifer system.

The project includes data cleaning, well filtering, table merging, annual maximum radium extraction, exploratory data analysis, visualization, and regression modeling.

## Project Overview

Combined radium is regulated in drinking water because elevated concentrations may pose long-term health risks. This project uses Python and R-based workflows to investigate patterns in measured radium concentrations across Wisconsin well data.

The workflow focuses on:

- Cleaning radium concentration records
- Removing invalid or negative measurements
- Merging well and contaminant datasets
- Filtering wells by aquifer and geologic conditions
- Extracting annual maximum radium values
- Visualizing temporal and spatial patterns
- Modeling trends using regression analysis

## Repository Contents

| File or Folder | Description |
|---|---|
| `UW.ipynb` | Main notebook used during research development and exploration |
| `Well_Information_Populator.py` | Populates missing well-related information using previous or replacement well references |
| `Negative_Radium_Concentration_and_Unique_Well_Number_Cleaner.py` | Cleans radium records and handles invalid measurements or well identifiers |
| `Table_Merger.py` | Merges well information and radium contaminant datasets |
| `Sand_and_Gravel_Well_Filter.py` | Filters out sand and gravel wells from the dataset |
| `Annual_Maximum_Radium_Contamination_Filter.py` | Extracts annual maximum radium values |
| `Theil-Sen_Regression_Analysis_Modeler.r` | R script for Theil-Sen regression analysis |
| `radium_analysis.py` | Python data analysis and visualization script |
| `radium_analysis_with_excel.py` | Python analysis script configured for Excel input |
| `radium_analysis_with_regression.py` | Python script with summary statistics, visualizations, and regression models |
| `analysis_outputs/` | Generated summary tables, plots, reports, and regression outputs |
| `radium_analysis_with_regression_outputs/` | Additional generated analysis outputs |

## Data Files

This repository includes Excel datasets used during the analysis. These files contain cleaned, filtered, or merged versions of the original well and radium records.

Important data files include:

- `filtered_annual_maximum_radium.xlsx`
- `filtered_radium_data_dnr.xlsx`
- `filtered_sand_and_gravel_wells_dnr.xlsx`
- `merged_all_wells_ra_dnr.xlsx`

Before reusing or redistributing the data, verify that the source data can be shared publicly and cite the original data provider when applicable.

## Main Analysis Script

The most complete Python script is:

```bash
radium_analysis_with_regression.py

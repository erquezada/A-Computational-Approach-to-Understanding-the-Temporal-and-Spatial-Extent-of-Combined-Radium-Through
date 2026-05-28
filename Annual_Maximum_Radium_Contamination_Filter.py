from pathlib import Path

import pandas as pd
from tqdm import tqdm

def read_excel_file(file_path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"The file does not exist: {file_path}")

    df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl", parse_dates=["Sample Date"])

    # Make datetime columns timezone-naive for consistency
    for col in df.select_dtypes(include=["datetime64[ns, tz]"]):
        df[col] = df[col].dt.tz_localize(None)

    return df

def wells_sampled(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Sample Date"] = pd.to_datetime(df["Sample Date"], errors="coerce")
    df["Year"] = df["Sample Date"].dt.year

    # Keep only the highest measured amount per well-year
    idx = df.groupby(["WI_UNIQUE_WELL_NO", "Year"])["Measured Amount"].idxmax()
    result = df.loc[idx].copy()
    result["Count"] = df.groupby(["WI_UNIQUE_WELL_NO", "Year"])['Measured Amount'].transform("count").loc[idx].astype(int)
    result.reset_index(drop=True, inplace=True)
    return result

def main():
    file_path = "filtered_sand_and_gravel_wells_dnr.xlsx"
    
    sheet_name = "Sheet1"
    

    input_path = Path(file_path)
    output_path = Path(__file__).resolve().parent / "filtered_annual_maximum_radium.xlsx"

    with tqdm(total=3, desc="Annual max radium", unit="step") as progress:
        df = read_excel_file(input_path, sheet_name=sheet_name)
        progress.update(1)

        wells_data = wells_sampled(df)
        progress.update(1)

        wells_data.to_excel(output_path, index=False)
        progress.update(1)

    print(f"Updated wells in dataset: {len(wells_data)} rows")
    print(f"Saved annual maximum radium data to '{output_path}'.")

if __name__ == "__main__":
    main()

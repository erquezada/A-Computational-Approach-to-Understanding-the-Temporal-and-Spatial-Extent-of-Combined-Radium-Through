from pathlib import Path

import pandas as pd
from tqdm import tqdm


def read_excel_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    except ValueError as exc:
        raise ValueError(f"Sheet '{sheet_name}' not found in {file_path}") from exc


def merge_excel_files(
    file1: Path,
    file2: Path,
    sheet1: str,
    sheet2: str,
    output_file: Path,
    on: str = "WI_UNIQUE_WELL_NO",
    how: str = "inner",
) -> pd.DataFrame:
    with tqdm(total=4, desc="Merging Excel files", unit="step") as progress:
        df1 = read_excel_sheet(file1, sheet1)
        progress.update(1)

        df2 = read_excel_sheet(file2, sheet2)
        progress.update(1)

        merged_df = pd.merge(df1, df2, on=on, how=how)
        progress.update(1)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_excel(output_file, index=False)
        progress.update(1)

    return merged_df


def main() -> None:
    file1 = Path(
        "/Users/ericquezada/Desktop/Projects/Internship 3 UW - Madison/University of Wisconsin Water Science Lab Docs/Savannah/Populated_All_Wisconsin_Wells.xlsx"
    )
    file2 = Path(
        "/Users/ericquezada/Desktop/Projects/Internship 3 UW - Madison/A-Computational-Approach-to-Understanding-the-Temporal-and-Spatial-Extent-of-Combined-Radium-Through/filtered_radium_data_dnr.xlsx"
    )
    sheet1 = "Sheet1"
    sheet2 = "Sheet1"
    output_file = Path(
        "/Users/ericquezada/Desktop/Projects/Internship 3 UW - Madison/A-Computational-Approach-to-Understanding-the-Temporal-and-Spatial-Extent-of-Combined-Radium-Through/merged_all_wells_ra_dnr.xlsx"
    )

    merged_df = merge_excel_files(file1, file2, sheet1, sheet2, output_file)
    print(f"Merged data saved to {output_file} ({len(merged_df)} rows)")


if __name__ == "__main__":
    main()

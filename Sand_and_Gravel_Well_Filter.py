from pathlib import Path

import pandas as pd
from tqdm import tqdm

def first_bedrock_filter(
    file_name: str,
    sheet_name: str,
    column_name: str,
    output_file_name: str,
) -> None:
    input_path = Path(file_name)
    output_path = Path(output_file_name)

    if not input_path.exists():
        raise FileNotFoundError(f"The file does not exist: {input_path}")

    df = pd.read_excel(input_path, sheet_name=sheet_name)

    if column_name not in df.columns:
        raise KeyError(f"Column not found: {column_name}")

    with tqdm(total=3, desc="Filtering wells", unit="step") as progress:
        progress.update(1)

        filtered_df = df.dropna(subset=[column_name]).reset_index(drop=True)
        progress.update(1)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        filtered_df.to_excel(output_path, index=False)
        progress.update(1)

    print(f"Filtered {len(df) - len(filtered_df)} rows with missing '{column_name}'.")
    print(f"Modified output saved to '{output_path}'.")

def main():
    # Example usage
    file_name = 'merged_all_wells_ra_dnr.xlsx'
    sheet_name = 'Sheet1'
    column_name = 'FIRST_BEDROCK_FT'
    output_file_name = 'filtered_sand_and_gravel_wells_dnr.xlsx' #file name

    first_bedrock_filter(file_name, sheet_name, column_name, output_file_name)

if __name__ == "__main__":
    main()

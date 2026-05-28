from pathlib import Path

import pandas as pd
from tqdm import tqdm


class ExcelDataCleaner:
    def __init__(self, file_path: str | Path, sheet_name: str, usecols=None):
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.usecols = usecols
        self.df = self._load_excel()

    def _load_excel(self) -> pd.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        return pd.read_excel(
            self.file_path,
            sheet_name=self.sheet_name,
            usecols=self.usecols,
            engine="openpyxl",
        )

    def _validate_columns(self, required_columns: list[str]) -> None:
        missing = [col for col in required_columns if col not in self.df.columns]
        if missing:
            raise KeyError(f"Missing required columns: {missing}")

    def describe_column(self, column_name: str) -> pd.Series:
        self._validate_columns([column_name])
        return self.df[column_name]

    def filter_negative_and_missing(self, value_column: str, well_number_column: str) -> pd.DataFrame:
        self._validate_columns([value_column, well_number_column])
        mask = self.df[value_column].ge(0) & self.df[well_number_column].notna()
        self.df = self.df.loc[mask].reset_index(drop=True)
        return self.df

    def get_unique_well_numbers(self, well_number_column: str) -> pd.Index:
        self._validate_columns([well_number_column])
        return self.df[well_number_column].dropna().unique()

    def save(self, output_path: str | Path) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_excel(output_path, index=False)


def main() -> None:
    file_path = Path("Ra Contamination in Public Water Supplies.xlsx")
    sheet_name = "All Ra Wells"
    value_column = "Measured Amount"
    well_number_column = "WI_UNIQUE_WELL_NO"
    output_file_path = Path("filtered_radium_data_dnr.xlsx")

    with tqdm(total=3, desc="Processing Excel file", unit="step") as progress:
        cleaner = ExcelDataCleaner(
            file_path=file_path,
            sheet_name=sheet_name,
            usecols=None,
        )
        progress.update(1)

        original_row_count = len(cleaner.df)
        original_unique_wells = cleaner.df[well_number_column].nunique(dropna=True)

        print(f"Loaded {original_row_count} rows from '{sheet_name}'")
        print(f"Original unique wells: {original_unique_wells}")

        cleaner.filter_negative_and_missing(value_column, well_number_column)
        progress.update(1)
        cleaned_row_count = len(cleaner.df)
        cleaned_unique_wells = len(cleaner.get_unique_well_numbers(well_number_column))

        print(f"Rows after filtering negatives and missing well numbers: {cleaned_row_count}")
        print(f"Unique wells after filtering: {cleaned_unique_wells}")

        cleaner.save(output_file_path)
        progress.update(1)
        print(f"Saved filtered data to: {output_file_path}")


if __name__ == "__main__":
    main()

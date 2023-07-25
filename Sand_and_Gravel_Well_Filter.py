import pandas as pd

def delete_empty_cells(file_name, sheet_name, column_name, output_file_name):
    try:
        # Read the Excel file
        df = pd.read_excel(file_name, sheet_name=sheet_name)

        # Delete rows with empty cells in the specified column
        df.dropna(subset=[column_name], inplace=True)

        # Save the modified dataframe to a new Excel file
        df.to_excel(output_file_name, index=False)

        print(f"Empty cells deleted in column '{column_name}' in sheet '{sheet_name}'.")
        print(f"Modified output saved to '{output_file_name}'.")
    except FileNotFoundError:
        print(f"The file {file_name} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Example usage
    file_name = 'merged_all_wells_ra_dnr.xlsx'
    sheet_name = 'Sheet1'
    column_name = 'FIRST_BEDROCK_FT'
    output_file_name = 'filtered_sand_and_gravel_wells_dnr.xlsx'

    delete_empty_cells(file_name, sheet_name, column_name, output_file_name)

if __name__ == "__main__":
    main()

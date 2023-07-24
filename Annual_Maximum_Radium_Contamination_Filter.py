import os
import numpy as np
import pandas as pd

def read_excel_file(file_path, sheet_name=None):
    try:
  
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', parse_dates=['Sample Date'])
            # Ensure all the datetime objects are timezone unaware
        for col in df.select_dtypes(include=[np.datetime64]):
            if df[col].dtype.name == 'datetime64[ns, tz]':
                df[col] = df[col].dt.tz_localize(None)
        return df
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        print(f"File not found or permission denied: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

def wells_sampled(df):
    df['Sample Date'] = pd.to_datetime(df['Sample Date'])
    df['Year'] = df['Sample Date'].dt.year
    df.sort_values(['WI_UNIQUE_', 'Year', 'Measured A'], ascending=[True, True, False], inplace=True)
    df.drop_duplicates(['WI_UNIQUE_', 'Year'], keep='first', inplace=True)
    df['Count'] = df.groupby(['WI_UNIQUE_', 'Year'])['Measured A'].transform('count')
    return df

def main():
    file_path = "/Users/erquezada/Desktop/Max_Contamination/CO_U and CO_C Wells with Ra data DNR merged -S&G in MCOAS.xlsx"
    # Get the sheet name from the user
    sheet_name = input("Enter the sheet name you want to work with: ")

    df = read_excel_file(file_path, sheet_name=sheet_name)

    if df is not None:
        wells_data = wells_sampled(df)
        print("Updated wells in dataset:")
        print(wells_data)

        # Get the directory of the script
        script_dir = os.path.dirname(os.path.realpath(__file__))

        # Write data to an Excel file
        output_file_name = os.path.join(script_dir, f"updated_wells_data_{sheet_name}.xlsx")
        wells_data.to_excel(output_file_name, index=False)
        print(f"Updated wells data has been written to '{output_file_name}'.")
    else:
        print(f"Failed to read data from {file_path}")

if __name__ == "__main__":
    main()

import pandas as pd

class ExcelDataReader:
    def read_excel_file(self, file_path, sheet_name, column_name):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        specific_column = df[column_name]
        df.index = df.index + 1
        df.reset_index(drop=True, inplace=True)
        return specific_column

def process_excel_file(file_path, sheet_name, column_name, well_number_column):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Delete rows with negative values in the specified column
    df = df[df[column_name] >= 0]

    # Delete cells with an empty well number
    df = df.dropna(subset=[well_number_column])

    # Reset the index
    df.reset_index(drop=True, inplace=True)

    return df

def process_unique_well_numbers(df, column_name):
    unique_well_numbers = df[column_name].unique()

    # Perform further processing or calculations on the unique well numbers
    # ...

    return unique_well_numbers

# Specify the file path, sheet name, and column name
file_path = 'Ra Contamination in Public Water Supplies.xlsx'
sheet_name = 'All wells Ra DNR'
column_name = 'Measured Amount'
well_number_column = 'WI_UNIQUE_WELL_NO'

# Create an instance of ExcelDataReader
data_reader = ExcelDataReader()

# Call the read_excel_file method and store the returned column in a variable
column_data = data_reader.read_excel_file(file_path, sheet_name, column_name)

# Print the column data
print(column_data)

# Process the Excel file and obtain the updated DataFrame
processed_data = process_excel_file(file_path, sheet_name, column_name, well_number_column)

# Save the updated DataFrame to a new Excel file
output_file_path = 'Updated_Data.xlsx'
processed_data.to_excel(output_file_path, index=False)

print("\nNew Excel file has been generated:", output_file_path)

# Process the unique well numbers
unique_wells = process_unique_well_numbers(processed_data, well_number_column)
print("\nUnique Well Numbers:")
print(unique_wells)

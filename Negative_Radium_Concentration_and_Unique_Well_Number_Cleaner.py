import pandas as pd

class ExcelDataReader:
    def __init__(self, file_path, sheet_name):
        self.df = pd.read_excel(file_path, sheet_name=sheet_name)

    def read_column(self, column_name):
        specific_column = self.df[column_name]
        return specific_column

    def drop_negative_values(self, column_name, well_number_column):
        # Delete rows with negative values in the specified column
        self.df = self.df[self.df[column_name] >= 0]
        # Delete cells with an empty well number
        self.df = self.df.dropna(subset=[well_number_column])
        # Reset the index
        self.df.reset_index(drop=True, inplace=True)
        return self.df

    def process_unique_well_numbers(self, column_name):
        unique_well_numbers = self.df[column_name].unique()
        return unique_well_numbers

# Specify the file path, sheet name, and column name
file_path = 'Ra Contamination in Public Water Supplies.xlsx'
sheet_name = 'All Ra Wells'
column_name = 'Measured Amount'
well_number_column = 'WI_UNIQUE_WELL_NO'

# Create an instance of ExcelDataReader
data_reader = ExcelDataReader(file_path, sheet_name)

# Call the read_column method and store the returned column in a variable
column_data = data_reader.read_column(column_name)

# Print the column data
print(column_data)

# Process the Excel file and obtain the updated DataFrame
processed_data = data_reader.drop_negative_values(column_name, well_number_column)

# Save the updated DataFrame to a new Excel file
output_file_path = 'filtered_radium_data_dnr.xlsx'
processed_data.to_excel(output_file_path, index=False)

print("\nNew Excel file has been generated:", output_file_path)

# Process the unique well numbers
unique_wells = data_reader.process_unique_well_numbers(well_number_column)
print("\nUnique Well Numbers:")
print(unique_wells)

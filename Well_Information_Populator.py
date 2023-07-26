import pandas as pd

def well_data_populator(data):
    # Iterate over each row in the DataFrame
    for index, row in data.iterrows():
        current_wi_unique = row['WI_UNIQUE_WELL_NO']
        first_bedrock_ft = row['FIRST_BEDROCK_FT']

        # Check if FIRST_BEDROCK_FT is empty
        if pd.isnull(first_bedrock_ft):
            previous_well_no = row['PREVIOUS_WELL_NO']
            replacement_well_no = row['REPLACEMENT_WELL_NO']

            # Check if previous well number is available
            if pd.notnull(previous_well_no):
                # Find the previous well's FIRST_BEDROCK_FT
                previous_row = data[data['WI_UNIQUE_WELL_NO'] == previous_well_no]

                if len(previous_row) > 0:
                    previous_bedrock_ft = previous_row['FIRST_BEDROCK_FT'].values[0]

                    # Check if previous well's FIRST_BEDROCK_FT is available
                    if pd.notnull(previous_bedrock_ft):
                        # Update the current row with the previous well's FIRST_BEDROCK_FT
                        data.at[index, 'FIRST_BEDROCK_FT'] = previous_bedrock_ft
            elif pd.notnull(replacement_well_no):
                # Find the replacement well's FIRST_BEDROCK_FT
                replacement_row = data[data['WI_UNIQUE_WELL_NO'] == replacement_well_no]

                if len(replacement_row) > 0:
                    replacement_bedrock_ft = replacement_row['FIRST_BEDROCK_FT'].values[0]

                    # Check if replacement well's FIRST_BEDROCK_FT is available
                    if pd.notnull(replacement_bedrock_ft):
                        # Update the current row with the replacement well's FIRST_BEDROCK_FT
                        data.at[index, 'FIRST_BEDROCK_FT'] = replacement_bedrock_ft

    return data

def main():
    try:
        # Load the data into a DataFrame
        data = pd.read_excel('All_Wisconsin_Wells_DNR.xlsx')

        # Sort the data by WI Unique number
        data = data.sort_values('WI_UNIQUE_WELL_NO')

        data = well_data_populator(data)

        # Save the updated data to a new file
        data.to_excel('populated_all_wisconsin_wells.xlsx', index=False)

    except FileNotFoundError:
        print("The file All_Wisconsin_Wells_DNR.xlsx does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

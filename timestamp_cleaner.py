# -*- coding: utf-8 -*-
"""Timestamp cleaner.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SNrnuqVQQ7CNhpHy3XcYsx2NCSZe_muY
"""

from google.colab import files
uploaded = files.upload()

from openpyxl import load_workbook
import pandas as pd

def clean_excel_files(file, sheet1, output_file):
    # Read the Excel file
    excel_file = pd.read_excel(file, sheet_name=sheet1, engine='openpyxl')

    # Focus on a specific column by column name
    column_name = 'Sample Date'
    specific_column = excel_file[column_name]

    # Convert "Sample Date" column to datetime format
    excel_file['Sample Date'] = pd.to_datetime(excel_file['Sample Date'])

    # Extract the date portion without the timestamp
    excel_file['Sample Date'] = excel_file['Sample Date'].dt.strftime('%m/%d/%Y')

    # Perform operations on the modified DataFrame
    # For example, display the updated "Sample Date" column
    print(excel_file['Sample Date'])

    # Save the updated DataFrame to a new Excel file
    excel_file.to_excel(output_file, index=False)

# Example usage
file = 'Merged DNR 2000 - 2018 years.xlsx'
sheet1 = 'Sheet1'
output_file = '2000 - 2018 date fixed.xlsx'

clean_excel_files(file, sheet1, output_file)
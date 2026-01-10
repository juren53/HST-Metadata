import pandas as pd

# Replace 'input_file.xls' with the path to your XLS file
xls_file = 'input_file.xls'

# Replace 'output_file.csv' with the desired name for the CSV output file
output_file = 'output_file.csv'

# Read the XLS file into a pandas DataFrame
df = pd.read_excel(xls_file)

# Save the DataFrame as a CSV file
df.to_csv(output_file, index=False) 

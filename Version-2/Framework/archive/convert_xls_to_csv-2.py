import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Convert XLS to CSV.')
    parser.add_argument('input_xls', type=str, help='Path to the input Excel file (e.g., input_file.xls)')
    parser.add_argument('output_csv', type=str, help='Path to the desired output CSV file (e.g., output_file.csv)')

    args = parser.parse_args()
    xls_file = args.input_xls
    output_file = args.output_csv

    # Read the XLS file into a pandas DataFrame
    df = pd.read_excel(xls_file) 

    # Save the DataFrame as a CSV file
    df.to_csv(output_file, index=False) 


if __name__ == "__main__":  
    main()   

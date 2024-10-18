import csv

def read_and_transpose_csv(input_file):
    tr_values = []

    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        
        # Identify the indices of the columns
        try:
            tr_index = header.index('tr')
            vlan1_index = header.index('vlan1')
            vlan2_index = header.index('vlan2')
        except ValueError as e:
            print(f"Column {e} doesn't exist in the CSV file.")
            return
        
        for row in csv_reader:
            tr_value = row[tr_index]
            tr_values.append(tr_value)  # Add the 'tr' value to the list
            
            output_file = f'{tr_value}.csv'
            with open(output_file, 'w', newline='') as outfile:
                csv_writer = csv.writer(outfile)
                csv_writer.writerow([tr_value, row[vlan1_index]])
                csv_writer.writerow([tr_value, row[vlan2_index]])
                
    # Now, append the contents from each `{tr_value}.csv` to a new CSV
    new_csv = 'combined.csv'
    with open(new_csv, 'w', newline='') as combined_csv:
        csv_writer = csv.writer(combined_csv)
        for tr_value in tr_values:
            filename = f'{tr_value}.csv'
            with open(filename, 'r') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    csv_writer.writerow(row)

if __name__ == "__main__":
    input_filename = 'transpose1.csv'
    read_and_transpose_csv(input_filename)

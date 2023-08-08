import csv

def read_and_transpose_csv(input_file):
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        
        # Read the header separately
        header = next(csv_reader)
        
        # Identify the index of 'tr', 'vlan1' and 'vlan2' columns
        try:
            tr_index = header.index('tr')
            vlan1_index = header.index('vlan1')
            vlan2_index = header.index('vlan2')
        except ValueError as e:
            print(f"Column {e} doesn't exist in the CSV file.")
            return
        
        for row in csv_reader:
            # Use the value in 'tr' column as the filename
            tr_value = row[tr_index]
            output_file = f'{tr_value}.csv'
            
            with open(output_file, 'w', newline='') as outfile:
                csv_writer = csv.writer(outfile)
                # Only write the values from 'vlan1' and 'vlan2' columns
                csv_writer.writerow([tr_value, [row[vlan1_index]]])
                csv_writer.writerow([tr_value, [row[vlan2_index]]])

if __name__ == "__main__":
    input_filename = 'transpose1.csv'
    read_and_transpose_csv(input_filename)

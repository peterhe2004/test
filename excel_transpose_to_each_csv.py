import csv

def read_and_transpose_csv(input_file):
    with open(input_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        header = next(csv_reader)
        print(f"Header: {header}")

        # Identify the index of 'tr' column
        try:
            tr_index = header.index('tr')
            print(tr_index)
        except ValueError:
            print("The 'tr' column doesn't exist in the CSV file.")
            return
        
        for row in csv_reader:
            # Use the value in 'tr' column as the filename
            tr_value = row[tr_index]
            output_file = f'{tr_value}.csv'  # Creating a new filename based on 'tr' column value


        # for idx, row in enumerate(csv_reader):
        #     output_file = f'output_{idx}.csv'  # Creating a new filename for each row

            with open(output_file, 'w', newline='') as outfile:
                csv_writer = csv.writer(outfile)
                for item in row:
                    csv_writer.writerow([item])

if __name__ == "__main__":
    input_filename = 'transpose1.csv'
    read_and_transpose_csv(input_filename)

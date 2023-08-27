import os
import csv

def rename_replacing_keyword(folder_path):
    csv_file_path = r'C:\Users\phe\Documents\tech\test\shCREv1.csv'

    csv_data = {}
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data[row['CRE']] = row['TR']

    # target_files = [f for f in files if f.endswith('.txt')]
    # folder_path = r'C:\Users\phe\Documents\tech\test\preconfig'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            # Perform the desired operations on each file
            # Check if the filename contains the value of A1
            # Append A2 value followed by "_" to the beginning
            # Rename the file

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    for a1_value, a2_value in csv_data.items():
                        if a1_value in filename:
                            new_filename = f"{a2_value}_{filename}"
                            new_file_path = os.path.join(folder_path, new_filename)
                            os.rename(file_path, new_file_path)
                            break  # Break the loop after finding the first match


directory = r'C:\Users\phe\Documents\tech\test\preconfig'
rename_replacing_keyword(directory)
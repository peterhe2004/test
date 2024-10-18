import os

def rename_files_in_directory(directory, prefix):
    # List all files in the given directory
    files = os.listdir(directory)
    
    # Filter out just the .txt files or any other condition you'd like
    txt_files = [f for f in files if f.endswith('.txt')]
    
    for filename in txt_files:
        # Create new filename with the prefix
        new_filename = prefix + filename
        
        # Form the full file paths
        original_file_path = os.path.join(directory, filename)
        new_file_path = os.path.join(directory, new_filename)
        
        # Rename the file
        os.rename(original_file_path, new_file_path)
        print(f"Renamed {filename} to {new_filename}")

# Example usage
directory_path = '/path/to/your/directory'
rename_files_in_directory(directory_path, 'prefix_')

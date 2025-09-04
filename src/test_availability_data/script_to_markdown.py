import pandas as pd
import os
from src.test_availability_data.utils.general import get_data_directory_from_command_line

def create_markdown_file_from_csv(data_dir):
    
    # Read CSV file
    file_path = os.path.join(data_dir, "downloaded_datasets.csv")
    df = pd.read_csv(file_path)

    # Convert dataframe to markdown table
    markdown_table = df.to_markdown(index=False)

    # Save into a markdown file inside docs/
    with open("docs/generated_table.md", "w") as f:
        f.write("# Auto-generated Table\n\n")
        f.write(markdown_table)

if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    create_markdown_file_from_csv(data_dir)
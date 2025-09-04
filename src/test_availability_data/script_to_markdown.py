import pandas as pd
import os
import subprocess
from dotenv import load_dotenv
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

def deploy_on_gh_pages():
    # Load .env variables
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME")
    repo = "Automation-test-Marine-Data-Store"

    if not token or not username:
        raise ValueError("❌ Missing one or more required environment variables")

    
    remote_url = f"https://{username}:{token}@github.com/{repo}.git"

    # Run mkdocs deploy
    try:
        subprocess.run([
            "mkdocs", "gh-deploy",
            "--remote-url", remote_url,
            "--force"  # optional, see discussion earlier
        ], check=True)
        print("✅ Docs deployed successfully")
    except subprocess.CalledProcessError as e:
        print("❌ Deployment failed:", e)


if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    create_markdown_file_from_csv(data_dir)
    deploy_on_gh_pages()
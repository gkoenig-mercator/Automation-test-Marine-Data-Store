import pandas as pd
import os
import subprocess
from dotenv import load_dotenv
from src.test_availability_data.utils.general import get_data_directory_from_command_line

def create_markdown_file_from_csv(data_dir):
    
    # Read CSV file
    file_path = os.path.join(data_dir, "datasets_not_downloaded.csv")
    try:
        df = pd.read_csv(file_path)

        # Convert dataframe to markdown table
        markdown_table = df.to_markdown(index=False)

        # Save into a markdown file inside docs/
        with open("docs/generated_table.md", "w") as f:
            f.write("# List of Datasets With Errors\n\n")
            f.write(markdown_table)

    except pd.errors.EmptyDataError:

        with open("docs/generated_table.md", "w") as f:
            f.write("# List of Datasets With Errors\n\n")
            f.write("No error for this run")

def deploy_on_gh_pages():
    """
    Deploy documentation to GitHub Pages using mkdocs via HTTPS + Personal Access Token.
    
    Requires:
      - GH_TOKEN environment variable to be set (your GitHub PAT)
      - mkdocs installed and configured with gh-pages
    
    Example:
      export GH_TOKEN="ghp_XXXXXXXXXXXXXXXX"
      deploy_on_gh_pages("username", "repository")
    """
    token = os.environ.get("GH_TOKEN")
    repo_name = os.environ.get("GH_REPO")
    repo_user = os.environ.get("GH_USER")

    if not token:
        print("❌ Error: GH_TOKEN environment variable is not set.")
        sys.exit(1)

    repo_url = f"https://{token}@github.com/{repo_user}/{repo_name}.git"

    try:
        # Update remote URL to use token authentication
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
        
        # Deploy documentation
        subprocess.run(["mkdocs", "gh-deploy", "--force"], check=True)
        
        print("✅ Docs deployed successfully")
    except subprocess.CalledProcessError as e:
        print("❌ Deployment failed:", e)
        sys.exit(1)

if __name__ == "__main__":

    data_dir = get_data_directory_from_command_line()
    create_markdown_file_from_csv(data_dir)
    deploy_on_gh_pages()
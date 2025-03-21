import os
from dotenv import load_dotenv
from chat_code import ChatCode
from tree_sitter_languages import get_language, get_parser
from github import Github
from github_repo import GitHubRepo

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "octoobservo/semicolons2025wiki"

repo = GitHubRepo(GITHUB_TOKEN, REPO_NAME)
repo.create_github_issue("Test Issue 2", "This is a test issue.")

def create_github_issue(title, body):
    """Create an issue on GitHub."""
    try:
        issue = repo.create_issue(title=title, body=body)
        print(f"Issue created: {issue.html_url}")
    except Exception as e:
        print(f"Failed to create issue: {e}")

# try:
#     language = get_language('python')
#     parser = get_parser('python')
#     print("Successfully retrieved language:", language)
# except Exception as e:
#     print("Error:", e)
# os.environ["LANGCHAIN_HANDLER"] = ""
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["LANGCHAIN_TRACING_V2"] = ""
# os.environ["LANGCHAIN_TRACING"] = ""

code = ChatCode()

print("Starting ingestion...")
code.ingest("C:\\code\\semicolons\\sample_code")
code.ingest("C:\\code\\semicolons\\sample_code\\monolog-loki")
code.ingest("C:\\code\\semicolons\\laravel-crm")
print("Ingestion completed.")
response = code.ask("what language was this code base written in?")
print(response)

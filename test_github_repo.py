import os
from dotenv import load_dotenv
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
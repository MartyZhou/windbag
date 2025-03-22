import os
from dotenv import load_dotenv
from github_repo import GitHubRepo

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "octoobservo/laravel-crm"

repo = GitHubRepo(GITHUB_TOKEN, REPO_NAME)

branch_name = "feature/update-file"
file_path = "C:\\code\\semicolons\\code-for-rag\\laravel-crm\\packages\\Webkul\\Activity\\src\\Repositories\\ActivityRepository.php"
commit_message = "Update file with new content"
pr_title = "Update file.php"
pr_body = "This pull request updates file.php with new content."

repo.commit_and_create_pr(branch_name, file_path, commit_message, pr_title, pr_body)

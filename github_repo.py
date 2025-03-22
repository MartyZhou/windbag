from github import Github
import os

class GitHubRepo(object):
    def __init__(self, token, repo_name):
        self.token = token
        self.repo_name = repo_name
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)
        self.base_folder_path = "C:\\code\\semicolons\\code-for-rag\\laravel-crm"

    def create_github_issue(self, title, body):
        """Create an issue on GitHub."""
        try:
            issue = self.repo.create_issue(title=title, body=body)
            print(f"Issue created: {issue.html_url}")
        except Exception as e:
            print(f"Failed to create issue: {e}")

    def commit_and_create_pr(self, branch_name, file_path, commit_message, pr_title, pr_body, base_branch="semicolon2025"):
        """
        Commit local changes to a branch, push them, and create a pull request.

        :param branch_name: Name of the branch to create or use.
        :param file_path: Path to the file to commit (local file).
        :param commit_message: Commit message.
        :param pr_title: Title of the pull request.
        :param pr_body: Body of the pull request.
        :param base_branch: The branch to merge the pull request into (default: main).
        """
        try:
            # Get the base branch reference
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")

            # Create a new branch from the base branch
            try:
                self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_ref.object.sha)
                print(f"Branch '{branch_name}' created.")
            except Exception as e:
                print(f"Branch '{branch_name}' already exists: {e}")

            # Read the local file content
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Get the file path relative to the repository root
            repo_file_path = os.path.relpath(file_path, start=self.base_folder_path).replace("\\", "/")

            # Get the file from the repository (if it exists)
            try:
                repo_file = self.repo.get_contents(repo_file_path, ref=branch_name)
                # Update the file with local changes
                self.repo.update_file(
                    path=repo_file.path,
                    message=commit_message,
                    content=content,
                    sha=repo_file.sha,
                    branch=branch_name,
                )
                print(f"File '{repo_file_path}' updated in branch '{branch_name}'.")
            except Exception:
                # Create the file if it doesn't exist
                self.repo.create_file(
                    path=repo_file_path,
                    message=commit_message,
                    content=content,
                    branch=branch_name,
                )
                print(f"File '{repo_file_path}' created in branch '{branch_name}'.")

            # Create a pull request
            pr = self.repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch,
            )
            print(f"Pull request created: {pr.html_url}")

        except Exception as e:
            print(f"Failed to commit and create pull request: {e}")
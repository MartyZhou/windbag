from github import Github

class GitHubRepo(object):
    def __init__(self, token, repo_name):
        self.token = token
        self.repo_name = repo_name
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def create_github_issue(self, title, body):
        """Create an issue on GitHub."""
        try:
            issue = self.repo.create_issue(title=title, body=body)
            print(f"Issue created: {issue.html_url}")
        except Exception as e:
            print(f"Failed to create issue: {e}")
import os
import requests
from openai import OpenAI

client = OpenAI()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# GitHub API headers
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_repo_info(github_url):
    """Extracts owner and repo name from GitHub URL."""
    parts = github_url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[-2], parts[-1]

def fetch_latest_commits(owner, repo, n=10):
    """Fetches the latest N commits from a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    commits = response.json()
    return commits[:n]

def analyze_commits_with_openai(commits):
    """Analyzes commit messages and diffs using OpenAI API from a Web3 sales perspective."""
    messages = []
    for commit in commits:
        commit_message = commit['commit']['message']
        messages.append(f"Commit: {commit_message}")

    prompt = "\n".join(messages) + "\nAs a Web3 sales professional, analyze these commits focusing on:\n" \
            "1. New blockchain technologies or protocols being implemented\n" \
            "2. Product features or improvements that could interest potential clients\n" \
            "3. Integration with new Web3 tools or platforms\n" \
            "4. Security improvements or compliance updates\n" \
            "Please highlight any potential business opportunities or competitive advantages."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Web3 sales professional analyzing GitHub commits to identify business opportunities and technological advancements."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    github_url = input("Enter GitHub repository URL: ")
    owner, repo = get_repo_info(github_url)
    commits = fetch_latest_commits(owner, repo)
    analysis = analyze_commits_with_openai(commits)
    print("\nAnalysis:\n", analysis)


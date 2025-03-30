import os
import requests
from openai import OpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with minimal configuration
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.openai.com/v1"
)

# Set up GitHub headers
HEADERS = {
    'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
    'Accept': 'application/vnd.github.v3+json'
}

def get_repo_info(github_url):
    """Extracts owner and repo name from GitHub URL."""
    github_url = github_url.replace('https://github.com/', '').replace('http://github.com/', '')
    github_url = github_url.rstrip('/')
    parts = github_url.split('/')
    if not parts[0]:
        raise ValueError("Invalid GitHub URL")
    return parts[0], parts[1] if len(parts) > 1 else None

def get_user_repos(owner):
    """Fetches all repositories for a given GitHub user/organization."""
    url = f"https://api.github.com/users/{owner}/repos"
    repos = []
    page = 1
    
    while True:
        response = requests.get(f"{url}?page={page}", headers=HEADERS)
        response.raise_for_status()
        current_repos = response.json()
        if not current_repos:
            break
        repos.extend(current_repos)
        page += 1
    
    return [repo['name'] for repo in repos]

def fetch_recent_commits(owner, repo, days):
    """Fetches commits from the last {days} days from a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    # Calculate date from 7 days ago
    since_date = (datetime.now() - timedelta(days=days)).isoformat()
    lastNDays = days
    
    response = requests.get(url, headers=HEADERS, params={'since': since_date})
    response.raise_for_status()
    return response.json()

def analyze_commits_with_openai(commits):
    """Analyzes commit messages and diffs using OpenAI API from a Web3 sales perspective."""
    messages = []
    for commit_data in commits:
        repo = commit_data['repo']
        commit_message = commit_data['commit']['commit']['message']
        messages.append(f"Repository: {repo}\nCommit: {commit_message}")

    prompt = "\n".join(messages) + "\nAs a Web3 sales professional, analyze these commits focusing on:\n" \
            "1. New blockchain technologies or protocols being implemented\n" \
            "2. Product features or improvements that could interest potential clients\n" \
            "3. Integration with new Web3 tools or platforms\n" \
            "4. Security improvements or compliance updates\n\n" \
            "Please provide your analysis in the following format:\n\n" \
            "ANALYSIS:\n" \
            "[Your detailed analysis here]\n\n" \
            "TECHNOLOGY TAGS:\n" \
            "- List all mentioned blockchain technologies (e.g., Ethereum, Solana)\n" \
            "- List all mentioned protocols (e.g., DeFi, NFT)\n" \
            "- List all mentioned tools and platforms (e.g., MetaMask, OpenSea)\n" \
            "- List all mentioned standards or frameworks (e.g., ERC20, ERC721)"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system", 
                "content": "You are a Web3 sales professional analyzing GitHub commits. " \
                          "Provide a detailed analysis followed by specific technology tags. " \
                          "Be precise and only tag technologies that are explicitly mentioned or strongly implied in the commits. " \
                          "Format tags in categories and use standard naming conventions for Web3 technologies."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    github_url = input("Enter GitHub user/organization URL: ")
    owner, _ = get_repo_info(github_url)
    
    print(f"\nAnalyzing repositories for {owner}...")
    repos = get_user_repos(owner)
    
    all_commits = []
    for repo in repos:
        print(f"\nFetching commits from {repo}...")
        try:
            commits = fetch_recent_commits(owner, repo)
            if commits:
                all_commits.extend([{
                    'repo': repo,
                    'commit': commit
                } for commit in commits])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching commits from {repo}: {e}")
    
    if all_commits:
        print(f"\nAnalyzing {len(all_commits)} commits from the last {lastNDays} days...")
        
        # Update analyze_commits_with_openai function call
        messages = []
        for commit_data in all_commits:
            repo = commit_data['repo']
            commit_message = commit_data['commit']['commit']['message']
            messages.append(f"Repository: {repo}\nCommit: {commit_message}\n")
        
        analysis = analyze_commits_with_openai(all_commits)
        print("\nAnalysis:\n", analysis)
    else:
        print("\nNo commits found in the last 7 days.")

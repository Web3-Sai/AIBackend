from flask import Flask, request, jsonify
from github_commit_analyzer import get_repo_info, get_user_repos, fetch_recent_commits, analyze_commits_with_openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_github():
    try:
        # Get GitHub URL from request
        data = request.get_json()
        if not data or 'github_url' not in data:
            return jsonify({'error': 'Missing github_url in request body'}), 400
        
        github_url = data['github_url']
        days = data.get('days', 7)  # Optional parameter, defaults to 7 days
        
        # Get owner info
        owner, _ = get_repo_info(github_url)
        
        # Get all repos
        repos = get_user_repos(owner)
        
        # Collect commits
        all_commits = []
        for repo in repos:
            try:
                commits = fetch_recent_commits(owner, repo, days)
                if commits:
                    all_commits.extend([{
                        'repo': repo,
                        'commit': commit
                    } for commit in commits])
            except Exception as e:
                print(f"Error fetching commits from {repo}: {str(e)}")
                continue
        
        if not all_commits:
            return jsonify({
                'message': 'No commits found in the specified time period',
                'data': None
            }), 200
        
        # Analyze commits
        analysis = analyze_commits_with_openai(all_commits)
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'data': {
                'owner': owner,
                'repos_analyzed': len(repos),
                'commits_analyzed': len(all_commits),
                'analysis': analysis
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 
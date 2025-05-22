#!/usr/bin/env python3
import subprocess
import os
from datetime import datetime
from jinja2 import Template

def get_git_tag():
    """Get the latest git tag"""
    try:
        tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0']).decode().strip()
        return tag.lstrip('v')  # Remove 'v' prefix if present
    except subprocess.CalledProcessError:
        return "1.0.0"  # Default version if no tags

def get_app_name():
    """Extract app name from repository or use default"""
    try:
        # Get repo name from git remote
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url']).decode().strip()
        repo_name = remote_url.split('/')[-1].replace('.git', '')
        return repo_name
    except:
        return "WebAppX"  # Default name

def get_commits_since_last_tag():
    """Get commits since the last tag"""
    try:
        # Get all tags sorted by version
        tags = subprocess.check_output(['git', 'tag', '--sort=-version:refname']).decode().strip().split('\n')
        
        if len(tags) > 1 and tags[0] and tags[1]:
            # Get commits between the last two tags
            last_tag = tags[1]
            commits = subprocess.check_output(['git', 'log', f'{last_tag}..HEAD', '--oneline']).decode().strip()
        elif len(tags) >= 1 and tags[0]:
            # If only one tag exists, get all commits
            commits = subprocess.check_output(['git', 'log', '--oneline']).decode().strip()
        else:
            # No tags exist, get all commits
            commits = subprocess.check_output(['git', 'log', '--oneline']).decode().strip()
        
        return commits.split('\n') if commits else []
    except subprocess.CalledProcessError:
        return []

def parse_commits_by_type(commits):
    """Parse commits into categories based on conventional commit format and keywords"""
    categories = {
        'new_features': [],
        'improvements': [],
        'bug_fixes': [],
        'security_updates': [],
        'infra_changes': [],
        'db_changes': [],
        'known_issues': []
    }
    
    for commit in commits:
        if not commit.strip():
            continue
            
        # Remove commit hash and clean up message
        commit_msg = ' '.join(commit.split()[1:]).lower() if commit else ''
        original_msg = ' '.join(commit.split()[1:]) if commit else ''
        
        # Skip merge commits
        if commit_msg.startswith('merge'):
            continue
            
        # Categorize based on conventional commits and keywords
        if any(keyword in commit_msg for keyword in ['feat:', 'feature:', 'add:', 'new:', 'implement:']):
            categories['new_features'].append(f"• {original_msg}")
        elif any(keyword in commit_msg for keyword in ['fix:', 'bug:', 'resolve:', 'patch:']):
            categories['bug_fixes'].append(f"• {original_msg}")
        elif any(keyword in commit_msg for keyword in ['security:', 'sec:', 'vulnerability:', 'cve:', 'auth:']):
            categories['security_updates'].append(f"• {original_msg}")
        elif any(keyword in commit_msg for keyword in ['perf:', 'optimize:', 'improve:', 'enhance:', 'refactor:', 'performance:']):
            categories['improvements'].append(f"• {original_msg}")
        elif any(keyword in commit_msg for keyword in ['ci:', 'build:', 'deploy:', 'docker:', 'workflow:', 'pipeline:', 'infra:']):
            categories['infra_changes'].append(f"• {original_msg}")
        elif any(keyword in commit_msg for keyword in ['db:', 'database:', 'migration:', 'schema:', 'sql:', 'table:']):
            categories['db_changes'].append(f"• {original_msg}")
        else:
            # Default to improvements if no specific category matches
            categories['improvements'].append(f"• {original_msg}")
    
    # Convert lists to formatted strings or default messages
    formatted_categories = {}
    for category, items in categories.items():
        if items:
            formatted_categories[category] = '\n'.join(items)
        else:
            formatted_categories[category] = "• No changes in this category"
    
    return formatted_categories

def main():
    # Get dynamic values
    version = get_git_tag()
    app_name = get_app_name()
    release_date = datetime.now().strftime('%Y-%m-%d')
    generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Get commits since last tag and categorize them
    commits = get_commits_since_last_tag()
    commit_categories = parse_commits_by_type(commits)
    
    print(f"📝 Found {len(commits)} commits since last tag")
    for category, items in commit_categories.items():
        count = len([item for item in items.split('\n') if item.strip() and not item.strip() == "• No changes in this category"])
        print(f"   {category}: {count} items")
    
    # Read template
    with open("release_note_template.md", "r") as file:
        template = Template(file.read())
    
    # Build release data from parsed commits
    release_data = {
        "app_name": app_name,
        "version": version,
        "release_date": release_date,
        "generation_date": generation_date,
        "environment": "Production",
        **commit_categories  # Unpack the categorized commits
    }
    
    # Generate release notes
    release_note = template.render(**release_data)
    
    # Write output file
    output_filename = f"{app_name}_{version}_ReleaseNotes.md"
    with open(output_filename, "w") as out:
        out.write(release_note)
    
    print(f"✅ Release notes generated: {output_filename}")

if __name__ == "__main__":
    main()

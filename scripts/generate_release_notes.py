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

def main():
    # Get dynamic values
    version = get_git_tag()
    app_name = get_app_name()
    release_date = datetime.now().strftime('%Y-%m-%d')
    generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Read template
    with open("release_note_template.md", "r") as file:
        template = Template(file.read())
    
    # TODO: Replace these with actual data from your change tracking system
    # You can integrate with GitHub API, JIRA, or parse commit messages
    release_data = {
        "app_name": app_name,
        "version": version,
        "release_date": release_date,
        "generation_date": generation_date,
        "environment": "Production",
        "new_features": "• Added analytics dashboard\n• Scheduled email notifications",
        "improvements": "• Optimized SQL queries\n• Enhanced error handling",
        "bug_fixes": "• Fixed login redirect issue\n• Resolved memory leak in data processing",
        "security_updates": "• JWT token validation improvement\n• Updated dependencies with security patches",
        "infra_changes": "• Refactored GitHub Actions workflow\n• Updated deployment scripts",
        "db_changes": "• Migrated UserPreferences table\n• Added indexes for performance",
        "known_issues": "• Search timeout under high load\n• Mobile responsiveness on older devices"
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

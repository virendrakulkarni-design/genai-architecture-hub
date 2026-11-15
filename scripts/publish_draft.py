#!/usr/bin/env python3
"""
Publish Draft Post Script for GenAI Architecture Hub
Takes a draft JSON (via file, --json string, or stdin), validates the schema,
assigns the next official post ID (post-N), strips draft flags, sets publishedAt,
appends to data/posts.json, syncs data/posts.js, and optionally commits/pushes to git.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTS_JSON = os.path.join(DATA_DIR, "posts.json")
POSTS_JS = os.path.join(DATA_DIR, "posts.js")

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def sync_posts_js(posts):
    with open(POSTS_JS, "w", encoding="utf-8") as f:
        f.write("// Auto-generated data sync for direct local file:// and offline execution\n")
        f.write(f"window.POSTS_DATA = {json.dumps(posts, indent=2, ensure_ascii=False)};\n")

def validate_post_schema(post):
    required = ["title", "lead", "stats", "mentalModel", "diagram", "diagramCaption", "codeTitle", "codeContent", "takeaway"]
    for field in required:
        if field not in post:
            raise ValueError(f"Draft is missing required field: '{field}'")
    return True

def publish_draft(draft_data, push=True):
    posts = load_json(POSTS_JSON)
    next_id = f"post-{len(posts) + 1}"

    published = dict(draft_data)
    published.pop("draft", None)
    published["id"] = next_id
    published["level"] = published.get("level", "Advanced")
    published["levelClass"] = f"level-{published['level'].lower()}"
    published["readTime"] = published.get("readTime", "8 min read")
    published["audience"] = published.get("audience", "Enterprise GenAI Systems Engineers and Architects")
    published["publishedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    validate_post_schema(published)

    posts.append(published)
    save_json(POSTS_JSON, posts)
    sync_posts_js(posts)

    print(f"Successfully published '{published['title']}' as {next_id}!")
    print(f"Total published posts: {len(posts)}")

    if push:
        try:
            print("Committing and pushing to git origin/main...")
            subprocess.run(["git", "add", "data/posts.json", "data/posts.js"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "commit", "-m", f"Publish dispatch: {published['title']} [skip ci]"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            print("Pushed to GitHub Pages main branch successfully!")
        except Exception as e:
            print(f"Note: Git commit/push failed or skipped: {e}")

    return published

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Publish a draft post to GenAI Architecture Hub.")
    parser.add_argument("--file", type=str, help="Path to draft JSON file.")
    parser.add_argument("--json", type=str, help="Draft JSON string.")
    parser.add_argument("--no-push", action="store_true", help="Do not git commit and push.")
    args = parser.parse_args()

    draft_data = None
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            draft_data = json.load(f)
    elif args.json:
        draft_data = json.loads(args.json)
    elif not sys.stdin.isatty():
        draft_data = json.load(sys.stdin)
    else:
        print("Error: Please provide draft data via --file, --json, or stdin.")
        sys.exit(1)

    publish_draft(draft_data, push=not args.no_push)

if __name__ == "__main__":
    main()

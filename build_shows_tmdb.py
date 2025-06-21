

import os
import requests
import time
import re

# === CONFIG ===
TMDB_API_KEY = "35f06166e5f6d0338bc2c57008612667"  # Replace with your actual API key
OUTPUT_DIR = "3. Bibliography/TV Shows"
WAIT_TIME = 1  # Seconds between requests to avoid rate limiting

# === INPUT: TV Show Titles ===
TV_SHOW_TITLES = [
"13 Reasons Why", "The Office", "Fallout", "Friends", "Manifest", "Phineas and Ferb", "Severance", "That '70s Show","That '90s Show", "The 100", "Mr. Robot", "The Cable Guy (1996)", "The Rookie", "Upload"
]

# === HELPERS ===

def slugify(name):
    return name.replace("/", "-").replace(":", "").strip()

def to_multiline_yaml(key, items):
    if not items:
        return f"{key}:\n  -"
    return f"{key}:\n" + "\n".join(f"  - {item.strip()}" for item in items)

def get_tmdb_show_id(title):
    url = f"https://api.themoviedb.org/3/search/tv"
    params = {"api_key": TMDB_API_KEY, "query": title}
    res = requests.get(url, params=params).json()
    if res["results"]:
        return res["results"][0]["id"]
    return None

def get_show_details(show_id):
    url = f"https://api.themoviedb.org/3/tv/{show_id}"
    params = {"api_key": TMDB_API_KEY}
    return requests.get(url, params=params).json()

def get_show_credits(show_id):
    url = f"https://api.themoviedb.org/3/tv/{show_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    return requests.get(url, params=params).json()

def get_watch_providers(show_id):
    url = f"https://api.themoviedb.org/3/tv/{show_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}
    res = requests.get(url, params=params).json()
    us = res.get("results", {}).get("US", {})
    return us.get("flatrate", [])

# === MAIN SCRIPT ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

for title in TV_SHOW_TITLES:
    print(f"🔍 Fetching: {title}")
    show_id = get_tmdb_show_id(title)
    if not show_id:
        print(f"❌ Not found: {title}")
        continue

    details = get_show_details(show_id)
    credits = get_show_credits(show_id)
    providers = get_watch_providers(show_id)

    filename = slugify(details['name']) + ".md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        print(f"⏩ Skipped (already exists): {filename}")
        continue

    # Parse data
    name = details["name"]
    year = details["first_air_date"][:4] if details.get("first_air_date") else "0"
    seasons = details.get("number_of_seasons", 0)
    episodes = details.get("number_of_episodes", 0)
    runtime = details["episode_run_time"][0] if details.get("episode_run_time") else 0
    genres = [g["name"].lower() for g in details.get("genres", [])]
    streaming = [p["provider_name"] for p in providers] if providers else []

    actors = [a["name"] for a in credits.get("cast", [])[:8]]
    directors = [c["name"] for c in credits.get("crew", []) if c["job"] == "Executive Producer"]

    frontmatter = f"""---
type: show
title: {name}
seasons: {seasons}
episodes: {episodes}
running_time: {runtime}
available_on: {", ".join(streaming) if streaming else ""}
director: {", ".join(directors) if directors else ""}
{to_multiline_yaml("actors", actors)}
watched: false
{to_multiline_yaml("genre", genres)}
favorite: false
---"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"✅ Saved: {filename}")
    time.sleep(WAIT_TIME)

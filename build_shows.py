import os
import requests
import time
import re

# === CONFIG ===
OMDB_API_KEY = ""  # Replace this with your OMDb API key
OUTPUT_DIR = "3. Bibliography/TV Shows"
WAIT_TIME = 1  # To avoid rate limits (1s between requests)

# === INPUT: Add TV shows here ===
TV_SHOW_TITLES = [
    "That 70s show",
    "That 80s show",
    "That 90s show"
]

# === Create output directory ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Helpers ===
def to_multiline_yaml(key, items):
    if not items:
        return f"{key}:\n  -"
    return f"{key}:\n" + "\n".join(f"  - {item.strip()}" for item in items)

def safe_int(value):
    try:
        return int(re.search(r"\d+", value).group()) if value else 0
    except:
        return 0

# === Main processing loop ===
for title in TV_SHOW_TITLES:
    query = re.sub(r"\s+", "+", title.strip())
    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"

    response = requests.get(url)
    data = response.json()

    if data.get("Response") != "True":
        print(f"❌ Not found: {title}")
        continue

    if data.get("Type") != "series":
        print(f"🎬 Skipped (not a TV show): {title}")
        continue

    actors = data.get("Actors", "").split(",") if data.get("Actors") else []
    genres = data.get("Genre", "").split(",") if data.get("Genre") else []
    runtime = safe_int(data.get("Runtime", "0 min"))

    frontmatter = f"""---
type: show
title: {data.get('Title')}
seasons: "0"  # update manually if needed
episodes: "0"
running_time: {runtime}
available_on: 
director: {data.get('Director')}
{to_multiline_yaml('actors', actors)}
watched: false
{to_multiline_yaml('genre', genres)}
favorite: false
---"""

    filename = f"{data.get('Title').replace('/', '-')}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"✅ Saved: {filename}")
    time.sleep(WAIT_TIME)

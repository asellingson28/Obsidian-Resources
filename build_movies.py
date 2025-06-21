import os
import requests
import time
import re
from normalize_genres import normalize_genres_in_folder

# === CONFIG ===
OMDB_API_KEY = ""  # Replace with your OMDb API key
OUTPUT_DIR = "3. Bibliography/Movies"
WAIT_TIME = 1  # seconds between requests to avoid throttling

# === INPUT MOVIE TITLES ===
# Format: "MOVIE TITLE (YYYY)"
MOVIE_TITLES = [


]

# === CREATE OUTPUT DIRECTORY ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === FUNCTION TO CLEAN AND FORMAT MULTILINE YAML ===
def to_multiline_yaml(key, items):
    if not items:
        return f"{key}:\n  -"
    return f"{key}:\n" + "\n".join(f"  - {item.strip()}" for item in items)

# === MAIN LOOP ===

for full_title in MOVIE_TITLES:
    match = re.match(r"^(.*?)(?:\s\((\d{4})\))?$", full_title.strip())
    title = match.group(1)
    year = match.group(2) or ""

    query = title.replace(" ", "+")
    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    if year:
        url += f"&y={year}"

    response = requests.get(url)
    data = response.json()

    # ... continue with validation and frontmatter generation ...

    response = requests.get(url)
    data = response.json()

    if data.get("Response") != "True":
        print(f"❌ Not found: {title}")
        continue

    if data.get("Type") != "movie":
        print(f"📺 Skipped (not a movie): {title}")
        continue

    actors = data.get("Actors", "").split(",") if data.get("Actors") else []
    genres = data.get("Genre", "").split(",") if data.get("Genre") else []
    runtime = data.get("Runtime", "0").replace(" min", "").strip()
    runtime = int(runtime) if runtime.isdigit() else 0

    frontmatter = f"""---
type: movie
title: {data.get('Title')}
year: {data.get('Year')}
running_time: {runtime}
director: {data.get('Director')}
{to_multiline_yaml('actors', actors)}
watched: false
{to_multiline_yaml('genre', genres)}
favorite: false
---"""
    filename = f"{data.get('Title').replace('/', '-')}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # === Skip if file already exists ===
    if os.path.exists(filepath):
        print(f"⏩ Skipped (already exists): {filename}")
        continue

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"✅ Saved: {filename}")
    time.sleep(WAIT_TIME)  # avoid hitting rate limit
normalize_genres_in_folder(OUTPUT_DIR)

import os
import requests
import time
import re

# === CONFIG ===
OMDB_API_KEY = ""  # Replace with your OMDb API key
OUTPUT_DIR = "3. Bibliography/Movies"
WAIT_TIME = 1  # seconds between requests to avoid throttling

# === INPUT MOVIE TITLES ===
MOVIE_TITLES = [
"No Place in This World",
"A Quiet Place Part II",
"A Quiet Place: Day One"

    # Add as many as you want here
]

# === CREATE OUTPUT DIRECTORY ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === FUNCTION TO CLEAN AND FORMAT MULTILINE YAML ===
def to_multiline_yaml(key, items):
    if not items:
        return f"{key}:\n  -"
    return f"{key}:\n" + "\n".join(f"  - {item.strip()}" for item in items)

# === MAIN LOOP ===
for title in MOVIE_TITLES:
    query = re.sub(r"\s+", "+", title.strip())
    url = f"http://www.omdbapi.com/?t={query}&apikey={OMDB_API_KEY}"
    
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

    # Save note
    filename = f"{data.get('Title').replace('/', '-')}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    print(f"✅ Saved: {filename}")
    time.sleep(WAIT_TIME)  # avoid hitting rate limit

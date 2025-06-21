# normalize_genres.py

import os
import yaml

def normalize_genre_case(genre_list):
    return [g.lower() for g in genre_list]

def normalize_genres_in_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                if not lines or lines[0].strip() != '---':
                    continue

                end_index = None
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        end_index = i
                        break

                if end_index is None:
                    print(f"⚠️ Skipped (no closing frontmatter): {file}")
                    continue

                frontmatter_lines = lines[1:end_index]
                content_lines = lines[end_index + 1:]

                data = yaml.safe_load(''.join(frontmatter_lines)) or {}
                if 'genre' not in data:
                    continue

                normalized = normalize_genre_case(data['genre'])
                if data['genre'] == normalized:
                    continue

                data['genre'] = normalized
                new_frontmatter = yaml.dump(data, allow_unicode=True, sort_keys=False)

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('---\n' + new_frontmatter + '---\n' + ''.join(content_lines))

                print(f"✅ Normalized: {file}")

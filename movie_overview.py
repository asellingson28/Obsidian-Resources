import os

# Optional: define what text file extensions to include
TEXT_EXTENSIONS = {'.txt', '.md', '.markdown', '.yaml', '.yml'}

def is_text_file(filename):
    # Skip hidden/system files and only allow certain extensions
    if filename.startswith('.'):
        return False
    if TEXT_EXTENSIONS:
        return os.path.splitext(filename)[1].lower() in TEXT_EXTENSIONS
    return True  # If no filter, assume all non-hidden are fine

def find_files_to_update(folder_path):
    files_to_update = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if not is_text_file(file):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                contains_type_movie = any('type: show' in line for line in lines)
                already_has_overview = any('overview: [[(O) TV Shows]]' in line for line in lines)

                if contains_type_movie and not already_has_overview:
                    files_to_update.append(file_path)

            except Exception as e:
                print(f"Skipped (read error) {file_path}: {e}")

    return files_to_update

def update_files(files_to_update):
    for file_path in files_to_update:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                new_lines.append(line)
                if 'type: show' in line:
                    new_lines.append('overview: "[[(O) TV Shows]]"\n')

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print(f"Updated: {file_path}")
        except Exception as e:
            print(f"Failed to update {file_path}: {e}")

if __name__ == "__main__":
    folder_to_scan = '3. Bibliography'  # Replace this

    print("Scanning for files to update...")
    files = find_files_to_update(folder_to_scan)


    if not files:
        print("No files need updating.")
    else:
        print("\nThe following files will be modified:")
        for f in files:
            print(f" - {f}")

        confirm = input("\nDo you want to apply the changes? (yes/no): ").strip().lower()
        if confirm == 'yes':
            update_files(files)
            print("All files updated.")
        else:
            print("No changes were made.")

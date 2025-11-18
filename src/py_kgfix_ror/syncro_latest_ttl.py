import re
from pathlib import Path
import shutil
from datetime import datetime

import logging

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# get date modified from ttl file
def parse_ttl_modified_date(file_path: str) -> str | None:
    patterns = [
        r"dct:modified\s+['\"]([^'\"]+)['\"]\^\^xsd:date", 
        r"dct:modified\s+['\"]([^'\"]+)['\"]\^\^xsd:dateTime",
        r"dct:modified\s+['\"]([^'\"]+)['\"]"  
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
    return None

# get & write all latest files in latest folder
def get_all_latest_files(ttl_file_name: str, release_name: str) -> None:
    latest_dir = Path("/workspace/latest")
    if not latest_dir.exists():
        latest_dir.mkdir(parents=True, exist_ok=True)

    latest_ttl_file = latest_dir / (ttl_file_name + ".ttl")
    latest_json_file = latest_dir / (ttl_file_name + ".json") 
    latest_jsonld_file = latest_dir / (ttl_file_name + ".jsonld")
    
    current_ttl_file = Path("/workspace") / release_name / (ttl_file_name + ".ttl")
    current_json_file = Path("/workspace") / release_name / (ttl_file_name + ".json")
    current_jsonld_file = Path("/workspace") / release_name / (ttl_file_name + ".jsonld")

    if not latest_ttl_file.exists():
        shutil.copy2(current_ttl_file, latest_ttl_file)
        shutil.copy2(current_json_file, latest_json_file)
        shutil.copy2(current_jsonld_file, latest_jsonld_file)
        logging.info(f"➕ Créé: {ttl_file_name} (.ttl, .json, .jsonld)")
        return

    latest_modified_str = parse_ttl_modified_date(latest_ttl_file)
    current_modified_str = parse_ttl_modified_date(current_ttl_file)

    if not latest_modified_str or not current_modified_str:
        logging.error(f"⚠️  Date manquante - copie: {ttl_file_name} (.ttl, .json, .jsonld)")
        return

    latest_modified_date = datetime.fromisoformat(latest_modified_str)
    current_modified_date = datetime.fromisoformat(current_modified_str)

    if current_modified_date > latest_modified_date:
        shutil.copy2(current_ttl_file, latest_ttl_file)
        shutil.copy2(current_json_file, latest_json_file) 
        shutil.copy2(current_jsonld_file, latest_jsonld_file)
        logging.info(f"🔄 Mis à jour: {ttl_file_name} (.ttl, .json, .jsonld)")

# if __name__ == "__main__":
#     print("Starting TTL synchronization...")

#     local_path = Path("/workspace")
#     releases = ["v14.0", "v15.0"]

#     for release_name in releases:
#         # logging.info(f"Release to process : {release_name}\n")
#         output_dir = local_path / release_name
#         releases_file = get_json_files_for_version(local_path, release_name)
        
#         # if not releases_file:
#             # logging.error(f"No JSON files found for release {release_name}\n")

#         for j, file in enumerate(releases_file):
#             print(f"Processing file: {file}")
#             ttl_file = output_dir / f"{file.stem}.ttl"
#             progress = round((j + 1) / len(releases_file) * 100)
#             verify_inside_latest(file.stem, release_name)
#             # logging.info(f"✅ - {progress}% - {file}")
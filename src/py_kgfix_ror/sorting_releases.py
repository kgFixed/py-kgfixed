import logging
import os
import re
from typing import List

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def version_key(version):
    # Remove leading 'v' if present
    version = version.lstrip('v')
    # Split by '.' and convert to integers
    parts = [int(p) for p in version.split('.')]
    # Pad with zeros to at least 3 parts (major.minor.patch)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)

# get the versions to process
def get_releases_to_process(volume_path: str = "/workspace") -> List[str]:
    releases_to_process = []
    
    try:
        version_pattern = re.compile(r"^v\d+\.\d+(\.\d+)?$")
        folders = [
            f for f in os.listdir(volume_path) 
            if os.path.isdir(os.path.join(volume_path, f)) and version_pattern.match(f)
        ]
        
        for folder in sorted(folders):
            folder_path = os.path.join(volume_path, folder)
            
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            ttl_files = [f for f in os.listdir(folder_path) if f.endswith('.ttl')]
            
            json_count = len(json_files)
            ttl_count = len(ttl_files)
                        
            if json_count != ttl_count:
                releases_to_process.append(folder)

    except Exception as e:
        logging.error(f"Error reading releases from volume: {e}")
        return []
    
    return releases_to_process

# get release to process sorted - CORRIGÉE
def get_releases_to_process_sorted() -> List[str]:
    releases = get_releases_to_process()
    # Trier avec la fonction version_key
    releases_sorted = sorted(releases, key=version_key)
    return releases_sorted

# if __name__ == "__main__":
#     releases = get_releases_to_process_sorted()
#     logging.info(f"Releases to process (sorted): {releases}")
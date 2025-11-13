import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List

from py_kgfix_ror import (
    process_ror_json_to_ttl,
    ttl_to_jsonld_local_context,
    verif_ttl_file
)

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# get the json file for one version
def get_json_files_for_version(local_path: Path, version: str) -> List[Path]:
    version_path = local_path / version
    if version_path.exists():
        return sorted([f for f in version_path.glob("*.json") if f.is_file()])
    return []

# get the versions to process
def get_versions_to_process(volume_path: str = "/workspace") -> List[str]:
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

# get date last commit git
def get_git_last_commit_date(file: Path, release_version: str) -> None:
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%ci', release_version + '/' + file.name],
            capture_output=True,
            text=True,
            cwd=Path("/workspace")
        )
        if result.returncode == 0:
            git_date = result.stdout.strip().split()[0]  
            os.environ['GIT_LAST_COMMIT_DATE'] = git_date
        else:
            os.environ['GIT_LAST_COMMIT_DATE'] = "date_unknown"
    except Exception:
        os.environ['GIT_LAST_COMMIT_DATE'] = "date_unknown"

# final processing
def final_processing(releases: List[str], volume_path: str = "/workspace") -> None:
    local_path = Path(volume_path)

    for release_name in releases:
        logging.info(f"Release to process : {release_name}\n")
        output_dir = local_path / release_name
        releases_file = get_json_files_for_version(local_path, release_name)
        
        if not releases_file:
            logging.error(f"No JSON files found for release {release_name}\n")

        for j, file in enumerate(releases_file):
            ttl_file = output_dir / f"{file.stem}.ttl"
            get_git_last_commit_date(file, release_name)
            process_ror_json_to_ttl(file, output_dir)
            ttl_to_jsonld_local_context(ttl_file)
            progress = round((j + 1) / len(releases_file) * 100)
            logging.info(f"✅ - {progress}% - {file}")

    verif_ttl_file()

# main fonction
if __name__ == "__main__":

    try:
        releases = get_versions_to_process()
        final_processing(releases)
    except Exception as e:
        logging.error("💥 Critic Error: {e}")
        import traceback
        traceback.print_exc()
        
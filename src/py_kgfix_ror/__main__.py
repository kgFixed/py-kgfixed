import logging
import os
import re
import time
import subprocess
from pathlib import Path
from typing import List

from py_kgfix_ror import (
    git_push_existing_ttl,
    process_ror_file,
)

# function to clone a Git repository
def clone_repository(repo_url: str, branch: str, clone_dir: Path) -> None:
    clone_dir.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ['git', 'clone', '-b', branch, repo_url, str(clone_dir)],
        check=True
    )

# get the json file for one version
def get_json_files_for_version(local_path: Path, version: str) -> List[Path]:
    version_path = local_path / version
    if version_path.exists():
        return sorted([f for f in version_path.glob("*.json") if f.is_file()])
    return []

# get the versions to process
def get_versions_to_process(volume_path: str = "/workspace") -> List[str]:
    
    # output_dir = os.path.join(volume_path, "output")
    # os.makedirs(output_dir, exist_ok=True)
    releases_to_process = []
    
    try:
        semver_pattern = re.compile(r"^v\d+\.\d+(\.\d+)?$")
        folders = [
            f for f in os.listdir(volume_path) 
            if os.path.isdir(os.path.join(volume_path, f)) and semver_pattern.match(f)
        ]
        releases_to_process = sorted(folders) 
    except Exception as e:
        logging.error(f"Error reading releases from volume: {e}")
        return
    
    return releases_to_process

# final processing
def final_processing(volume_path: str = "/workspace") -> None:
    
    local_path = Path(volume_path)
    releases_to_process = get_versions_to_process(volume_path)

    if not releases_to_process:
        logging.warning("No releases found to process")
        return

    logging.info(f"Processing releases: {releases_to_process}")

    for i, release in enumerate(releases_to_process):
        releases_file = get_json_files_for_version(local_path, release)
        
        if not releases_file:
            logging.warning(f"No JSON files found for release {release}")
            continue

        output_dir = local_path / release
        for j, file in enumerate(releases_file):
            process_ror_file(file, output_dir)
            progress = round((j + 1) / len(releases_file) * 100)
            print(f"✅ - {progress}% - {file}")
        
        # if len(releases_to_process) > 1 and i > 0 and release != releases_to_process[i-1]:
        #     print("\nWait for the commit and push files...")
        #     success = git_push_existing_ttl(
        #         repo_dir= Path(volume_path),
        #         target_dir= release,
        #         version_name=f"{release}",
        #         tag_version=f"{release}"
        #     )

        #     if not success:
        #         print("\n✗ Operation failed. See messages above.")
        #         exit(1)
        #     print(f"\n✓ Release {release} pushed successfully!")

# main fonction
if __name__ == "__main__":

    try:
        final_processing()
    except Exception as e:
        print(f"💥 ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        
    # local_path = Path(os.getenv('LOCAL_DATA', './default-data')).resolve()
    # print(local_path)
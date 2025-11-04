import subprocess
import os
from pathlib import Path
from typing import List

from src.py_kgfix_ror.template_to_try import process_ror_file

# get the json file for one version
def get_json_files_for_version(local_path: Path, version: str) -> List[Path]:
    version_path = local_path / version
    if version_path.exists():
        return sorted([f for f in version_path.glob("*.json") if f.is_file()])
    return []

def get_git_last_commit_date(file: Path, release_version: str) -> str:
    """Récupère la date du dernier commit git pour un fichier"""
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%ci', release_version + '/' + file.name],
            capture_output=True,
            text=True,
            cwd=local_path
        )
        git_date = result.stdout.strip() if result.returncode == 0 else "date_unknown"
        os.environ['GIT_LAST_COMMIT_DATE'] = git_date
        return git_date  
    except Exception:
        return "date_unknown"

def is_parameter_in_json_file(json_file_path: Path, target_parameter: str) -> bool:
    """
    Vérifie si le paramètre existe dans le fichier JSON
    Retourne True si trouvé, False sinon
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Cherche simplement si le mot existe dans le contenu
        return f'"{target_parameter}"' in content
        
    except Exception as e:
        print(f"❌ Erreur lecture {json_file_path}: {e}")
        return False
    
if __name__ == "__main__":
    # res = get_git_last_commit_date()
    # print(res)
    volume_path = "/workspace"
    local_path = Path(volume_path)

    releases_to_process = ["v12.0"]
    local_path = Path(volume_path)
    for release in releases_to_process:
        output_dir = local_path / release
        releases_file = get_json_files_for_version(local_path, release)
        for j, file in enumerate(releases_file):
            res = get_git_last_commit_date(file, release)
            process_ror_file(file, output_dir)
            progress = round((j + 1) / len(releases_file) * 100)
            print(f"✅ - {progress}% - {file}")

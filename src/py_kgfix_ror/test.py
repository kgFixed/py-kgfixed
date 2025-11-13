import re
import subprocess
import os
from pathlib import Path
from typing import Dict, List
import shutil

from src.py_kgfix_ror.template_to_try import process_ror_json_to_ttl

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
        os.environ['GIT_LAST_COMMIT_DATE'] = git_date.split()[0]
        return git_date.split()[0]  
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
    
def get_all_git_dates(release_version: str) -> Dict[str, str]:
    """Récupère toutes les dates git en UNE commande"""
    try:
        # Une commande git qui liste tous les fichiers avec leurs dates
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%ci', '--name-only', release_version],
            capture_output=True,
            text=True,
            cwd=local_path
        )
        
        # Parse la sortie
        dates = {}
        current_date = None
        for line in result.stdout.strip().split('\n'):
            if line and not line.isspace():
                if re.match(r'\d{4}-\d{2}-\d{2}', line):  # C'est une date
                    current_date = line.split()[0]
                elif line.endswith('.json'):  # C'est un fichier
                    if current_date:
                        dates[line] = current_date
        
        return dates
        
    except Exception as e:
        print(f"❌ Git history error: {e}")
        return {}

def get_date_release(folder_name: str, volume_path: str = "/workspace") -> str:

    
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%ci', '--', str(folder_name)],
            capture_output=True,
            text=True,
            cwd=volume_path
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split()[0]  
        else:
            return "date_inconnue"
                
    except Exception as e:
        print(f"❌ Erreur git log dossier: {e}")
        return "date_inconnue"

def copy_to_latest(release_folder: str, volume_path: str = "/workspace"):
    """Copie tous les TTL d'une release vers le dossier latest/"""
    try:
        repo_dir = Path(volume_path)
        source_dir = repo_dir / release_folder
        latest_dir = repo_dir / "latest"
        
        if not source_dir.exists():
            print(f"❌ Source release doesn't exist: {source_dir}")
            return False
        
        # Crée le dossier latest (le supprime d'abord s'il existe)
        if latest_dir.exists():
            shutil.rmtree(latest_dir)
        latest_dir.mkdir()
        
        # Copie tous les fichiers TTL
        shutil.copytree(source_dir, latest_dir, dirs_exist_ok=True)
        
        print(f"✅ Copied files to latest/ from {release_folder}")
        return True
        
    except Exception as e:
        print(f"❌ Error copying to latest: {e}")
        return False

# Utilisation
copy_to_latest("v12.0", "/workspace")

if __name__ == "__main__":

    volume_path = "/workspace"
    dates = []
    dict = {}
    releases_to_process = ["v1.0", "v1.1", "v1.2", "v12.0"]
    local_path = Path(volume_path)
    for release in releases_to_process:
        output_dir = local_path / release
        releases_file = get_json_files_for_version(local_path, release)
        # data = get_all_git_dates(release)
        # dates.append(get_date_release(release))
        dict[release] = get_date_release(release)
        # for j, file in enumerate(releases_file):
        #     # git_date = data.get(release + "/" + file.name, "date_unknown")
        #     # os.environ['GIT_LAST_COMMIT_DATE'] = git_date
        #     # process_ror_json_to_ttl(file, output_dir)
        #     progress = round((j + 1) / len(releases_file) * 100)
        #     print(f"✅ - {progress}% - {file}")
    
    latest_release = max(dict, key=dict.get)
    latest_date = dict[latest_release]
    print("Latest release:", latest_release, "with date:", latest_date)

    copy_to_latest(latest_release)

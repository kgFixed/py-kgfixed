import csv
import importlib.resources
import json
import logging
import os
from pathlib import Path
import re
from typing import List
from sema.subyt import Subyt

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# a supprimer apres
def get_json_files_for_version(local_path: Path, version: str) -> List[Path]:
    version_path = local_path / version
    if version_path.exists():
        return sorted([f for f in version_path.glob("*.json") if f.is_file()])
    return []

# create csv temp file
def create_csv_temp(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name', 'last_modified', 'isVersionOf'])
        writer.writeheader()

# write to csv
def write_to_csv(jsonld_file: Path, csv_file_path: Path) -> None:
    file_exists = os.path.exists(csv_file_path)
    fieldnames = ['name', 'last_modified', 'isVersionOf']
    try:
        with open(jsonld_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                org_data = data[0] 
                ror_id = org_data.get('@id', '')
                
                name = ''
                label_data = org_data.get('http://www.w3.org/2000/01/rdf-schema#label', [])
                if label_data and isinstance(label_data, list) and len(label_data) > 0:
                    name = label_data[0].get('@value', '')
                
                last_modified = ''
                modified_data = org_data.get('http://purl.org/dc/terms/modified', [])
                if modified_data and isinstance(modified_data, list) and len(modified_data) > 0:
                    last_modified = modified_data[0].get('@value', '')
                
            else:
                logging.error(f"Invalid format: {jsonld_file}")
                return
                
    except Exception as e:
        logging.error(f"Reading error {jsonld_file}: {e}")
        return
    
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        row_data = {
            'name': name,
            'last_modified': last_modified,
            'isVersionOf': ror_id  
        }
        
        writer.writerow(row_data)
    
# get latest minor version
def get_latest_minor_version(ldes_folder: Path) -> str:
    version_files = []
    
    for file_path in ldes_folder.glob("*.ttl"):
        match = re.search(r'v(\d+)\.(\d+)', file_path.stem)
        if match:
            major, minor = match.groups()
            version_files.append((int(major), int(minor)))
    
    if not version_files:
        return "1.00" 
    latest = sorted(version_files)[-1]
    return f"{latest[0]}.{latest[1]:02d}" 

# get current and next fragment version
def calculate_next_fragments_safe(latest_version: str):
    try:
        major, minor = latest_version.split('.')
        minor_int = int(minor)
        
        if minor_int + 1 > 99:
            current_fragment_version = f"{int(major) + 1}.00"
            next_fragment_version = f"{int(major) + 1}.01"
        else:
            current_fragment_version = f"{major}.{(minor_int + 1):02d}"
            next_fragment_version = f"{major}.{(minor_int + 2):02d}"
        
        return current_fragment_version, next_fragment_version
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return "1.01", "1.02"

# create LDES fragment
def create_ldes_fragment(csv_file_path: Path, current_version: str, next_version: str) -> None:
    organizations = []
    ldes_fragment_folder = Path("/workspace/LDES")
    ldes_fragment_folder.mkdir(parents=True, exist_ok=True)

    package_path = importlib.resources.files("py_kgfix_ror")
    template_path = package_path / "shapes" / "fragment.ttl"

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            organizations.append({
                "isVersionOf": row['isVersionOf'],
                "last_modified": row['last_modified'],
                "name": row['name']
            })

    vars = {
        "this_fragment_delta": current_version, 
        "next_fragment_delta": next_version,
        "retention_period": 1,
        "base_uri": "http://w3id.org/kgFixed/ror/ldes/",
        "data": {
            "qres" : organizations
        }
    }

    try:
        Subyt(
            template_name=template_path.name,
            template_folder=str(template_path.parent),
            source=None,
            sink=str(ldes_fragment_folder / f"v{current_version}.ttl"),
            overwrite_sink=True,
            variables=vars,
            conditional=False
        ).process()
    finally:
        if csv_file_path.exists():
            csv_file_path.unlink()

if __name__ == "__main__":

    volume_path = "/workspace"
    releases_to_process = ["v1.0", "v1.1"]
    local_path = Path(volume_path)
    
    for release in releases_to_process:
        output_dir = local_path / release
        csv_path = volume_path + f"/{release}_temp.csv"                                                             # ajout
        create_csv_temp(Path(csv_path))                                                                             # ajout
        releases_file = get_json_files_for_version(local_path, release)
        for j, file in enumerate(releases_file):
            jsonld_file = output_dir / f"{file.stem}.jsonld"
            write_to_csv(jsonld_file, Path(csv_path))                                                               # ajout
            progress = round((j + 1) / len(releases_file) * 100)
            print(f"✅ - {progress}% - {file}")
        latest_version_fragment = get_latest_minor_version(Path("/workspace/LDES"))                                 # ajout
        current_fragment_version, next_fragment_version = calculate_next_fragments_safe(latest_version_fragment)    # ajout
        create_ldes_fragment(Path(csv_path), current_fragment_version, next_fragment_version)                       # ajout
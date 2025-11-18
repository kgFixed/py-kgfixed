import csv
import importlib.resources
import json
import logging
import os
from pathlib import Path
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

# create temporary csv file
def create_csv_temp(file_path: Path) -> None:
    temp_csv_path = f"/workspace/temp.csv"
    fieldnames = ['name', 'last_modified', 'isVersionOf']
    file_exists = os.path.exists(temp_csv_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
                logging.error(f"Format invalide: {file_path}")
                return
                
    except Exception as e:
        logging.error(f"Reading error {file_path}: {e}")
        return
    
    with open(temp_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        row_data = {
            'name': name,
            'last_modified': last_modified,
            'isVersionOf': ror_id  
        }
        
        writer.writerow(row_data)
    
    logging.info(f"✅ Adding data for {Path(file_path).stem}: {name}")

# create LDES fragment
def create_ldes_fragment(csv_file_path: Path, output_dir: Path) -> None:
    organizations = []
    output_dir.mkdir(parents=True, exist_ok=True)
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
        "this_fragment_delta": "", # actual fragment
        "next_fragment_delta": "", # next fragment
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
            sink=str(output_dir / "ldes_fragment.ttl"),
            overwrite_sink=True,
            variables=vars,
            conditional=False
        ).process()
    finally:
        logging.info(f"✅ LDES fragment created at {output_dir / 'ldes_fragment.ttl'}\n")
        # if csv_file_path.exists():
        #     csv_file_path.unlink()

if __name__ == "__main__":

    volume_path = "/workspace"
    # dates = []
    # releases_to_process = ["v1.0", "v1.1"]
    # local_path = Path(volume_path)
    # for release in releases_to_process:
    #     output_dir = local_path / release
    #     releases_file = get_json_files_for_version(local_path, release)
    #     for j, file in enumerate(releases_file):
    #         jsonld_file = output_dir / f"{file.stem}.jsonld"
    #         create_csv_temp(jsonld_file)
    #         progress = round((j + 1) / len(releases_file) * 100)
    #         print(f"✅ - {progress}% - {file}")

    csv_path = volume_path + "/temp.csv"
    output_dir = volume_path + "/ldes_fragment"
    create_ldes_fragment(Path(csv_path), Path(output_dir))
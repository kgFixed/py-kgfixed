import json
import os
from pathlib import Path
import tempfile
from sema.subyt import Subyt
import logging
import requests

# Only shows errors
logging.getLogger("sema.subyt").setLevel(logging.ERROR) 

# Function to convert a JSON file to individual RDF files using a template
def json_to_individual_rdf(json_path: str | Path, template_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if isinstance(json_path, str):
        response = requests.get(json_path)
        data = response.json()
        ror_id = data['id'].split('/')[-1]    
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2) 
            tmp_path = tmp.name
    elif isinstance(json_path, Path):
        ror_id = json_path.stem
        tmp_path = str(json_path)
    else:
        raise ValueError("json_path must be a string or Path")

    vars = {
        "GIT_LAST_COMMIT_DATE": os.environ.get('GIT_LAST_COMMIT_DATE', 'date_inconnue')
    }
    
    try:
        Subyt(
            template_name=template_path.name,
            template_folder=str(template_path.parent),
            source=str(tmp_path),
            sink=str(output_dir / f"{ror_id}.ttl"),
            overwrite_sink=True,
            variables=vars,
            conditional=False
        ).process()
    finally:
        if isinstance(json_path, str):
            Path(tmp_path).unlink()
        
# if __name__ == "__main__":

#     Example of use for version 1.0
#     json_path = "https://raw.githubusercontent.com/ror-community/ror-records/main/v1.6/023rffy11.json" 
#     json_path = Path(__file__).parent.parent / "test/json/023rffy11.json"
#     template_path = Path(__file__).parent.parent / "test/template/template_1_0.ttl"
#     
#     Example of use for version 2.1
#     json_path = "https://raw.githubusercontent.com/ror-community/ror-records/main/v1.56/0003e4m70.json"
#     json_path = Path(__file__).parent.parent / "test/json/0003e4m70.json"    
#     template_path = Path(__file__).parent.parent / "test/template/template_2_1.ttl"

#     output_dir = Path(__file__).parent.parent / "test/to_push"
    
#     json_to_individual_rdf( 
#         json_path= json_path,
#         template_path= template_path,
#         output_dir= output_dir
#     )

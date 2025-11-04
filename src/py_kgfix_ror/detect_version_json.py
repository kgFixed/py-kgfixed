import json
import requests
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError
import importlib.resources

# Load JSON schema from file
def load_schema(version: str) ->  Dict[str, Any]:
    package_path = importlib.resources.files("py_kgfix_ror")
    schema_path = package_path / "json_schema" / f"ror_schema{version}.json"
    with importlib.resources.as_file(schema_path) as path:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

# Detect the version of a ROR JSON file
def detect_ror_version(json_file_path: str | Path) -> str | None:
    try:
        schema_v1 = load_schema("")
        schema_v2_0 = load_schema("_v2_0")
        schema_v2_1 = load_schema("_v2_1")
        
        if isinstance(json_file_path, str):
            response = requests.get(json_file_path)
            data = response.json()
        elif isinstance(json_file_path, Path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError("json_file_path must be a string or Path")
        
        try:
            validate(data, schema_v2_1)
            return "2_1"
        except ValidationError:
            try:
                validate(data, schema_v2_0)
                return "2_0"
            except ValidationError:
                validate(data, schema_v1)  
                return "1_0"
                
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON file")
        return None
    except ValidationError:
        print("Error: The file does not correspond to any known version")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# if __name__ == "__main__":
#     test_file_2_1 = Path("../ror_releases/v1.66/00b3mhg89.json") 
#     test_file_2_0 = Path("../ror_releases/v1.66/00b3mhg89.json") 
#     test_file_1_0 = Path("../ror_releases/v1.0/000ccd270.json") 
    
#     test_file = Path("../ror_releases/v1.66/00b3mhg89.json")

#     choice_version = 1.0

#     if choice_version == 1.0:
#         test_file = test_file_1_0
#     elif choice_version == 2.0:
#         test_file_2_0 = test_file_2_0
#     elif choice_version == 2.1:
#         test_file = test_file_2_1
#     else:
#         print("error of version")

#     if not test_file.exists():
#         print(f"Error: the file {test_file} doesn't exists")
#     else:
#         version = detect_ror_version(test_file)
#         if version:
#             print(f"Detected version : {version}")
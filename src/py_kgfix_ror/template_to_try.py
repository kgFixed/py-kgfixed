from pathlib import Path
import importlib.resources
from .detect_version_json import detect_ror_version
from .create_rdf_file import json_to_individual_rdf

# Tries to process a JSON file with different templates based on its detected version.
def process_ror_json_to_ttl(json_path: str | Path, output_dir: Path) -> None:
    version = detect_ror_version(json_path)
    
    templates_to_try = []
    
    if version is None:
        templates_to_try = [
            "template_1_0.ttl",
            "template_2_0.ttl",
            "template_2_1.ttl"
        ]
    else:
        templates_to_try = [f"template_{version}.ttl"]
    
    for template_name in templates_to_try:
        package_path = importlib.resources.files("py_kgfix_ror")
        template_path = package_path / "template" / template_name
        
        try:
            with importlib.resources.as_file(template_path) as path:
                json_to_individual_rdf(
                    json_path=json_path,
                    template_path=path,
                    output_dir=output_dir
                )
                return 
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Template failure {template_name}: {str(e)}")
            continue
    
    raise ValueError(f"No valid template found for the file: {json_path}")

# Example with a json that does not correspond to any version
# process_ror_file(Path(__file__).parent.parent / "ror_releases/v1.6/023rffy11.json", Path(__file__).parent.parent / "test")

# if __name__ == "__main__":
    # Example with a json that does not correspond to any version
    # process_ror_file(
        # Path(__file__).parent.parent / "json/004jbx603.json", #v1.0
        # Path(__file__).parent.parent / "json/000b3gw41.json", #v2.0
        # Path(__file__).parent.parent / "json/004jbx603.json", #v2.1
        # Path(__file__).parent.parent / "test"
    # )
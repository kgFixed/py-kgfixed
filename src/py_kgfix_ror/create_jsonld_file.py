from rdflib import Graph
from pathlib import Path

def ttl_to_jsonld_local_context(ttl_file: Path, output_file: Path = None) -> dict:
    g = Graph().parse(ttl_file, format='turtle')
    jsonld_file = ttl_file.with_suffix('.jsonld')
    g.serialize(format='json-ld', destination=jsonld_file)

# if __name__ == "__main__":
#     temp_dir = Path(__file__).parent.parent.parent / "000818d46.ttl"
#     jsonld_data = ttl_to_jsonld_local_context(Path(temp_dir))
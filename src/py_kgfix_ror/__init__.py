# py_kgfix_ror/__init__.py

from .create_rdf_file import json_to_individual_rdf
from .detect_version_json import load_schema, detect_ror_version
from .template_to_try import process_ror_json_to_ttl
from .create_jsonld_file import ttl_to_jsonld_local_context
from .verification_ttl_file import verif_ttl_file

__version__ = "0.1.0"
__author__ = "PROVAIN Antoine"
__all__ = [
    'json_to_individual_rdf',
    'load_schema',
    'detect_ror_version', 
    'git_push_existing_ttl',
    'process_ror_json_to_ttl',
    'ttl_to_jsonld_local_context',
    'verif_ttl_file'
]
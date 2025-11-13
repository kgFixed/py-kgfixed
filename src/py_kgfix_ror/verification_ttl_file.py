import importlib.resources
import os
import sys
import logging
import re
from rdflib import Graph
import pyshacl


def verif_ttl_file():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Get the mounted volume path from an argument or environment variable
    volume_path = os.getenv("workspace", "/workspace")

    package_path = importlib.resources.files("py_kgfix_ror")
    shapes_path = package_path / "shapes" 

    if not shapes_path.exists():
        logging.error(
            "No shapes repository path provided."
        )
        sys.exit(1)

    if not volume_path:
        logging.error(
            "No volume path provided. Please set the MOUNTED_VOLUME_PATH environment variable or pass it as an argument."
        )
        sys.exit(1)

    # Check if the volume path exists and is accessible
    if not os.path.exists(volume_path):
        logging.error(
            f"The specified volume path '{volume_path}' does not exist or is not accessible."
        )
        sys.exit(1)

    # Perform basic operations on the folder
    try:
        logging.info(f"Processing the volume at: {volume_path}")
        semver_pattern = re.compile(r"^v\d+\.\d+(\.\d+)?$")
        folders = [
            f
            for f in os.listdir(volume_path)
            if os.path.isdir(os.path.join(volume_path, f))
        ]

        for folder in folders:
            non_conform_files = []
            if semver_pattern.match(folder):
                folder_path = os.path.join(volume_path, folder)
                ttl_files = [f for f in os.listdir(folder_path) if f.endswith(".ttl")]
                logging.info(
                    f"Semver folder: {folder}, .ttl files count: {len(ttl_files)}"
                )

                logging.info(
                    f"Starting SHACL validation for TTL files in folder: {folder}"
                )
                for ttl_file in ttl_files:
                    g = Graph()
                    ttl_file_path = os.path.join(folder_path, ttl_file)
                    g.parse(ttl_file_path, format="turtle")

                    shacl_file_path = os.path.join(shapes_path, "shapes.ttl")
                    conforms, results_graph, results_text = pyshacl.validate(
                        g,
                        shacl_graph=shacl_file_path,
                        ont_graph=None,
                        inference="rdfs",
                        abort_on_first=False,
                        meta_shacl=False,
                        advanced=True,
                        debug=False,
                    )

                    if not conforms:
                        non_conform_files.append(ttl_file)
                        # Log validation errors line by line
                        for line in results_text.splitlines():
                            logging.warning(line)
                        continue
            for non_conform_file in non_conform_files:
                logging.error(
                    f"File '{non_conform_file}' in folder '{folder}' did not conform to SHACL shapes."
                )
    except Exception as e:
        logging.error(f"An error occurred while processing the volume: {e}")
        sys.exit(1)


# if __name__ == "__main__":
#     main()

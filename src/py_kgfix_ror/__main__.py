import os
import logging
import traceback
import subprocess
from typing import List
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from py_kgfix_ror import (
    process_ror_json_to_ttl,
    ttl_to_jsonld_local_context,
    verify_all_ttl_files,
    get_all_latest_files,
    get_releases_to_process_sorted,
    create_ldes_fragment,
    write_to_csv,
    create_csv_temp,
    get_latest_ldes_fragment,
)

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# get the json file for one version
def get_json_files_for_version(local_path: Path, version: str) -> List[Path]:
    version_path = local_path / version
    if version_path.exists():
        return sorted([f for f in version_path.glob("*.json") if f.is_file()])
    return []


# get date last commit git for file
def get_git_last_commit_date_for_file(file: Path, release_version: str) -> None:
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--pretty=format:%ci",
                release_version + "/" + file.name,
            ],
            capture_output=True,
            text=True,
            cwd=Path("/workspace"),
        )
        if result.returncode == 0:
            git_date = result.stdout.strip().split()[0]
            os.environ["GIT_LAST_COMMIT_DATE"] = git_date
        else:
            os.environ["GIT_LAST_COMMIT_DATE"] = "date_unknown"
    except Exception:
        os.environ["GIT_LAST_COMMIT_DATE"] = "date_unknown"


# final processing
def final_processing(releases: List[str], volume_path: str = "/workspace") -> None:
    local_path = Path(volume_path)

    if not releases:
        logging.error(f"No release to process\n")

    total_unique_files = sum(
        len(get_json_files_for_version(local_path, release)) for release in releases
    )
    logging.info(
        f"Total unique JSON files to process across all releases: {total_unique_files}\n"
    )

    for i, release_name in enumerate(releases):
        logging.info(f"Release to process : {release_name}\n")
        output_dir = local_path / release_name
        csv_path = volume_path + f"/{release_name}_temp.csv"
        create_csv_temp(Path(csv_path))
        releases_file = get_json_files_for_version(local_path, release_name)

        if not releases_file:
            logging.error(f"No JSON files found for release {release_name}\n")

        for j, file in enumerate(releases_file):
            ttl_file = output_dir / f"{file.stem}.ttl"
            jsonld_file = output_dir / f"{file.stem}.jsonld"
            # Check if both files exist, skip if so
            if ttl_file.exists() and jsonld_file.exists():
                logging.info(f"Skipping {file.stem}: .ttl and .jsonld already exist.")
                continue
            get_git_last_commit_date_for_file(file, release_name)
            process_ror_json_to_ttl(file, output_dir)
            ttl_to_jsonld_local_context(ttl_file)
            get_all_latest_files(file.stem, release_name)
            write_to_csv(jsonld_file, Path(csv_path))
            progress = round((j + 1) / len(releases_file) * 100)
            logging.info(f"✅ - {progress}% - {file}")
        create_ldes_fragment(
            Path(csv_path),
            release_name,
            releases[i + 1] if i + 1 < len(releases) else None,
        )

    get_latest_ldes_fragment(releases[-1])
    # Uncomment to verify all ttl files at the end of the process
    # verify_all_ttl_files()


def extract_organization_subjects(fragment_path: Path) -> set:
    organization_uri = URIRef("http://www.w3.org/ns/org#Organization")
    graph = Graph()
    try:
        graph.parse(fragment_path, format="turtle")
    except Exception as e:
        logging.error(f"Failed to parse fragment {fragment_path}: {e}")
        return set()

    return set(graph.subjects(RDF.type, organization_uri))


def count_unique_organizations_in_ldes(ldes_folder: Path) -> None:
    if not ldes_folder.exists():
        logging.error(f"LDES folder not found: {ldes_folder}")
        return

    fragment_files = sorted(ldes_folder.glob("*.ttl"))
    if not fragment_files:
        logging.error(f"No LDES fragments found in {ldes_folder}")
        return

    total_unique_subjects = set()
    for fragment_path in fragment_files:
        subjects = extract_organization_subjects(fragment_path)
        total_unique_subjects.update(subjects)
        logging.info(
            f"Fragment {fragment_path.name}: {len(subjects)} unique org:Organization"
        )

    logging.info(
        "Total unique org:Organization across all fragments: "
        f"{len(total_unique_subjects)}"
    )


# main function
if __name__ == "__main__":

    try:
        releases = get_releases_to_process_sorted()
        logging.info(f"Releases to process: {releases}\n")
        releases = releases[::-1]
        logging.info(f"Releases to process in reverse order: {releases}\n")
        final_processing(releases)
        count_unique_organizations_in_ldes(Path("/workspace/LDES"))
    except Exception as e:
        logging.error("💥 Critic Error: {e}")
        traceback.print_exc()

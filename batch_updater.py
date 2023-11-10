import argparse
from models import State, Event, Metadata, get_metadata, update_metadata

doi_prefix = "https://doi.org/"


def get_dataset_doi(file_doi: str):
    doi = file_doi[len(doi_prefix):] if file_doi.startswith(doi_prefix) else file_doi
    parts = doi.split("/")[0:-1]
    return "/".join(parts)


def process_doi(doi: str, credentials: list):
    metadata = get_metadata(get_dataset_doi(doi), credentials)
    print(f"Current metadata for {doi} is {metadata}")

    new_doi = doi_prefix + get_dataset_doi(doi)

    if metadata.get_current_state() == State.findable:
        metadata.set_updated_state(State.registered)
    metadata.set_updated_uri(new_doi)

    new_metadata = update_metadata(metadata, credentials)
    print(f"Updated metadata for {doi} to {new_metadata}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

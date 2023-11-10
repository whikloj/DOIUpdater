import argparse
from models import State, get_metadata, update_metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("doi", help="The DOI to update")
    parser.add_argument("--url", help="The URL to update the DOI to, or None to leave alone")
    parser.add_argument("--state", choices=[str(state) for state in State], help="The state to update the DOI to")
    parser.add_argument("--credentials", nargs=2, help="The username and password to use for authentication")

    args = parser.parse_args()

    metadata = get_metadata(args.doi, args.credentials)
    print(f"Current metadata for {args.doi} is {metadata}")

    if args.state is not None or args.url is not None:
        print("Doing update")
        metadata.set_updated_state(State.from_string(args.state))
        if args.url is not None:
            metadata.set_updated_uri(args.url)
        new_metadata = update_metadata(metadata, args.credentials)
        print(f"Updated metadata for {args.doi} to {new_metadata}")

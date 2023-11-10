import enum

import requests
from requests.auth import HTTPBasicAuth


class State(enum.Enum):
    findable = "findable"
    registered = "registered"
    draft = "draft"

    def __str__(self):
        return self.value

    @staticmethod
    def from_string(value: str):
        value = value.lower().strip()
        try:
            return State[value]
        except KeyError:
            raise Exception("Invalid state")


class Event(enum.Enum):
    publish = "publish"
    register = "register"
    hide = "hide"

    def __str__(self):
        return self.value

    @staticmethod
    def from_string(value: str):
        value = value.lower().strip()
        try:
            return Event[value]
        except KeyError:
            raise Exception("Invalid event")

    @staticmethod
    def get_event(current_state: State, desired_state: State):
        if current_state in [State.draft, State.registered] and desired_state == State.findable:
            return Event.publish
        elif current_state == State.draft and desired_state == State.registered:
            return Event.register
        elif current_state == State.findable and desired_state == State.registered:
            return Event.hide
        else:
            raise Exception("Invalid state transition")


class Metadata:
    """
    A metadata object, holds the current and updated state, the DOI and the URI
    """
    current_state: State
    updated_state: State
    doi: str
    current_url: str
    updated_url: str

    def __init__(self, state: State, doi: str, url: str):
        self.current_state = state
        self.updated_state = state
        self.doi = doi
        self.current_url = url
        self.updated_url = url

    def get_current_state(self) -> State:
        return self.current_state

    def get_updated_state(self) -> State:
        return self.updated_state

    def set_updated_state(self, state: State):
        self.updated_state = state

    def get_doi(self) -> str:
        return self.doi

    def set_updated_uri(self, uri: str):
        self.updated_url = uri

    def get_current_uri(self) -> str:
        return self.current_url

    def get_updated_uri(self) -> str:
        return self.updated_url

    def get_update_json(self) -> dict:
        data = {
                "data": {
                    "type": "dois",
                    "attributes": {
                    }
                }
            }
        if self.updated_state != self.current_state:
            data["data"]["attributes"]["event"] = str(Event.get_event(self.current_state, self.updated_state))
        if self.current_url != self.updated_url:
            data["data"]["attributes"]["url"] = self.updated_url
        if len(data["data"]["attributes"]) == 0:
            raise Exception("No update required")
        return data

    def __str__(self):
        return f"Metadata(state={self.current_state}, doi={self.doi}, uri={self.current_url})"


def get_metadata_from_json(json_data: dict) -> Metadata:
    """
    Get a metadata object from the JSON returned by the DataCite API
    :param {dict} json_data: The JSON data
    :return: A metadata object
    """
    return Metadata(
        State.from_string(json_data['data']['attributes']['state']),
        json_data['data']['id'],
        json_data['data']['attributes']['url']
    )


def get_metadata(doi: str, credentials: list) -> Metadata:
    f"""
    Gets the metadata for the specified DOI
    :param {str} doi: The DOI to get the metadata for
    :param {list} credentials: List with username and password 
    :return: The metadata object for the DOI
    """
    basic = HTTPBasicAuth(credentials[0], credentials[1])
    response = requests.get(
            f"https://api.datacite.org/dois/{doi}",
            headers={
                "Accept": "application/vnd.api+json"
            }
            , auth=basic)
    if response.status_code != 200:
        raise Exception(f"Error getting metadata: {response.json()}")

    return get_metadata_from_json(response.json())


def update_metadata(metadata: Metadata, credentials: list):
    f"""
    Updates the metadata for the specified DOI
    :param {Metadata} metadata: The updated metadata object
    :param {list} credentials: The username and password
    :return: The new metadata object
    """
    basic = HTTPBasicAuth(credentials[0], credentials[1])
    response = requests.put(
            f"https://api.datacite.org/dois/{metadata.get_doi()}",
            headers={
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json"
            },
            json=metadata.get_update_json(),
            auth=basic
        )
    if response.status_code != 200:
        raise Exception(f"Error updating metadata: {response.json()}")
    return get_metadata_from_json(response.json())




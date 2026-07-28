import json


def load_json_file(file_path) -> dict:
    """
    Load a JSON file and return its content as a Python object.

    :param file_path: Path to the JSON file.
    :return: Python object representing the JSON data.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_env_variable(key: str, environment: dict):
    """
    Retrieve an environment variable from the loaded JSON settings.

    :param key: The key of the environment variable to retrieve.
    :param environment: The environment dictionary to retrieve the variable from.
    :return: The value of the environment variable or error message if the key is not found.
    """
    if key in environment:
        return environment[key]
    else:
        raise KeyError(f"Environment variable '{key}' not found.")

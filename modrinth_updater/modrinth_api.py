import os
import requests
from http import HTTPStatus
from modrinth_updater.hash_utils import get_sha1_hash
from modrinth_updater.file_utils import get_current_fabric_version, get_current_loader


MODRINTH_API_BASE = "https://api.modrinth.com/v2"

def get_latest_mod_versions(mod_project_id):
    """
    Retrieves the latest version of a mod by sending a GET request to the Modrinth API with the provided project id.

    Args:
        mod_project_id (str): The project id of the mod to retrieve the latest version for.

    Returns:
        str or requests.Response: The latest version string of the mod, or an error message if the mod could not be found or an error occurred.
    """
    url = f'{MODRINTH_API_BASE}/project/{mod_project_id}'
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            filtered_latest_mod_versions = [v for v in data['game_versions'] if 'w' not in v]
            return filtered_latest_mod_versions[-1]
        elif response.status_code == HTTPStatus.NOT_FOUND:
            print (f'❌ Cannot find the mod witht the project id: {mod_project_id}')
        else:
            print(f'⚠️  Error: {response.status_code}')
            return response
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def get_local_version(file_path):
    """
    Retrieves the version of a mod by sending a GET request to the Modrinth API with the provided file hash.

    Args:
        hashed_file (str): The SHA1 hash of the local mod file to retrieve the version for.

    Returns:
        str or requests.Response: The version string of the mod, or an error message if the mod could not be found or an error occurred.
    """
    hashed_file = get_sha1_hash(file_path)
    mod_name = os.path.basename(file_path)
    url = f'{MODRINTH_API_BASE}/version_file/{hashed_file}'
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            return data['game_versions'], data['version_number'], response.status_code
        elif response.status_code == HTTPStatus.NOT_FOUND:
            print (f'⚠️  Cannot find the mod with the hash: {hashed_file}. Your mod file "{mod_name}" can be corrupted, donwload it again.')
            return [], [], response.status_code
        else:
            print(response.text)
            print(f'⚠️ Error: {response.status_code}')
            return [], [], response.status_code
    except requests.exceptions.Timeout:
        print('⚠️ The request timed out!')
        return [], [], None
    except requests.exceptions.RequestException as e:
        print(f'⚠️ An error occurred: {e}')
        return [], [], None

def check_update(path, game_versions=None, loaders=None):
    """
    Checks if there is an update for a local mod file by sending a POST request to the Modrinth API with the file hash and current game version and loader.

    Args:
        path (str): The path to the local mod file to check for updates.
        game_versions (str, optional): The current game version, or None to use the latest version.
        loaders (str, optional): The current loader, or None to use the latest version.

    Returns:
        tuple or None: A tuple containing the response from Modrinth, the current game version, the current loader, and the SHA1 hash of the file, or None if an error occurred.
    """

    sha1_hash = get_sha1_hash(path)
    url = f'{MODRINTH_API_BASE}/version_file/{sha1_hash}/update'
    headers = {
        'Content-Type': 'application/json'
    }

    body = {}
    if game_versions:
        body['game_versions'] = [game_versions]
        loader_version = game_versions
    else:
        loader_version = get_current_fabric_version()
    if loaders:
        body['loaders'] = [loaders]
    else:
        loaders = get_current_loader()
    try:
        response = requests.post(url, json=body, headers=headers, timeout=15)
        response.raise_for_status()
        return response, loader_version, loaders
    except requests.exceptions.Timeout:
        print('The request timed out!')
        return response, loader_version, loaders
    except requests.exceptions.RequestException:
        print (f'❌ There is no update for {os.path.basename(path)} your loader is {loaders}-{game_versions}.')
        return response, loader_version, loaders
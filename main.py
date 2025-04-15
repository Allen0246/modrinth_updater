import hashlib
import requests
import json
import os
import shutil
import urllib.parse
from packaging.version import Version
from dotenv import load_dotenv

load_dotenv()
env_mc_path = os.getenv('DEFAULT_MC_FOLDER')
if not env_mc_path:
    default_minecraft_path = env_mc_path
else:
    appdata_path = os.getenv('APPDATA')
    default_minecraft_path = os.path.join(appdata_path, '.minecraft')

def get_sha1_hash(file_path):

    """
    Calculates and returns the SHA1 hash of a local file.

    Args:
        file_path (str): The path to the file to calculate the hash for.

    Returns:
        str: The SHA1 hash of the file, or an error message if the file could not be read.
    """
    sha1_hash = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha1_hash.update(chunk)
        return sha1_hash.hexdigest()
    except Exception as e:
        error = (f'Error calculating SHA1 for {file_path}: {e}')
        return error

def get_sha256_hash(file_path):
    """
    Calculates and returns the SHA256 hash of a local file.
    
    Args:
        file_path (str): The path to the file to calculate the hash for.
    
    Returns:
        str: The SHA256 hash of the file, or an error message if the file could not be read.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        error = (f'Error calculating SHA256 for {file_path}: {e}')
        return error

def get_current_fabric_version(path = default_minecraft_path):
    """
    Retrieves the current version of the Fabric loader by reading the launcher_profiles.json file.

    Args:
        path (str, optional): The path to the directory containing the 'launcher_profiles.json' file. Defaults to the global variable `default_minecraft_path`.

    Returns:
        str: The version of the Fabric loader, or an error message if the file could not be read.
    """
    json_path = os.path.join(path, 'launcher_profiles.json')
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            loader_name=[]
            for loaders in data['profiles']:
                if 'fabric' in loaders:
                    loader_name.append(loaders)
                    fabric_version = loader_name[0].split('-')[-1]
                    return fabric_version
            if not loader_name:
                print('No fabric version found.')
            return loader_name
    except Exception as e:
        error = (f'Error reading launcher_profiles.json: {e}')
        return error

def get_current_loaders(path = default_minecraft_path):
    """
    Retrieves the current Minecraft loader (fabric, forge, or quilt) by reading the launcher_profiles.json file.
    
    Args:
        path (str, optional): The path to the directory containing the 'launcher_profiles.json' file. Defaults to the global variable `default_minecraft_path`.
    
    Returns:
        str: The name of the current Minecraft loader, or an error message if the file could not be read.
    """
    json_path = os.path.join(path, 'launcher_profiles.json')
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            for loaders in data['profiles']:
                try:
                    if 'fabric' in loaders:
                        return 'fabric'
                    elif 'forge' in loaders:
                        return 'forge'
                    elif 'neoforge' in loaders:
                        return 'neoforge'
                    elif 'quilt' in loaders:
                        return 'quilt'
                except Exception as e:
                    error = (f'Error reading launcher_profiles.json: {e}')
                    return error
    except Exception as e:
        error = (f'Error reading launcher_profiles.json: {e}')
        return error

def get_wait_for_update_mods(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of mods that are waiting for an update in the specified directory.

    This function scans the 'wait_for_update' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the mods found.

    Args:
        only_name (bool, optional): If True, returns only the mod file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'wait_for_update' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of mod file names or full paths depending on the `only_name` parameter.
    """

    wait_for_update_folder = os.path.join(path, 'mods', 'wait_for_update')
    list_mods = []
    for mods in os.listdir(wait_for_update_folder):
        mods_with_path = os.path.join(wait_for_update_folder, mods)
        if os.path.isfile(mods_with_path):
            if only_name:
                list_mods.append(os.path.basename(mods_with_path))
            else:
                list_mods.append(mods_with_path)
    return list_mods

def get_all_local_mods(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all local mods in the specified directory.

    This function scans the 'mods' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the mods found.

    Args:
        only_name (bool, optional): If True, returns only the mod file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'mods' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of mod file names or full paths depending on the `only_name` parameter.
    """

    mods_folder = os.path.join(path, 'mods')
    list_mods = []
    for mods in os.listdir(mods_folder):
        mods_with_path = os.path.join(mods_folder, mods)
        if os.path.isfile(mods_with_path):
            if only_name:
                list_mods.append(os.path.basename(mods_with_path))
            else:
                list_mods.append(mods_with_path)
    return list_mods

def get_latest_mod_versions(project_id):
    """
    Retrieves the latest mod version for a given project ID from Modrinth.

    This function sends a GET request to the Modrinth API using the specified project ID
    and filters out versions containing the character 'w' from the list of game versions.
    It then returns the latest of these filtered versions.

    Args:
        project_id (str): The ID of the project to retrieve the latest mod version for.

    Returns:
        str: The latest mod version without 'w' in the version string. If the project
        is not found or an error occurs, an error message is printed and the response
        object is returned.
    """

    url = f'https://api.modrinth.com/v2/project/{project_id}'
    response = requests.get(url, timeout=15)
    try:
        if response.status_code == 200:
            data = response.json()
            filtered_latest_mod_versions = [v for v in data['game_versions'] if 'w' not in v]
            return filtered_latest_mod_versions[-1]
        elif response.status_code == 404:
            print (f'❌ Cannot find the mod witht the project id: {project_id}')
        else:
            print(f'⚠️ Error: {response.status_code}')
            print(response.text)
            return response
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def get_local_mod_version(hash):
    """
    Retrieves the version number of a local mod from Modrinth.

    Args:
        hash (str): The SHA1 hash of the mod to retrieve the version number for.

    Returns:
        str: The version number of the mod, or an error message if the mod is not found or the request fails.
    """
    url = f'https://api.modrinth.com/v2/version_file/{hash}'
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data['game_versions']
        elif response.status_code == 404:
            print (f'❌ Cannot find the mod with the hash: {hash}')
        else:
            print(f'⚠️ Error: {response.status_code}')
            print(response.text)
            return response
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def download_mod(url, save_folder, mod_name=None):
    """
    Downloads a mod from a given URL and saves it to a given folder.
    
    Args:
        url (str): The URL of the mod to download.
        save_folder (str): The folder to save the downloaded mod in.
        mod_name (str, optional): The name to save the mod as. If None, the name from the URL is used. Defaults to None.
    
    Returns:
        str: The path of the saved mod, or an error message if the download failed.
    """
    if mod_name is None:
        mod_name = os.path.basename(url)
        mod_name = urllib.parse.unquote(mod_name)
    save_path = os.path.join(save_folder, mod_name)
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()  # Raise error if download failed

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return save_path
    except requests.exceptions.Timeout:
        print("The request timed out!")
    except Exception as e:
        error = (f'Error downloading file: {e}')
        return error

def fix_version_number(game_versions):
    """
    Filters out snapshot versions from a list of game versions and returns the latest stable version.

    Args:
        game_versions (list): A list of game version strings to filter and evaluate.

    Returns:
        str: The latest stable game version string without snapshots, determined by comparing version numbers.
    """

    with_out_snapshot = [v for v in game_versions if 'w' not in v.lower()]
    return max(with_out_snapshot, key=Version)

def check_updateable_mods(mod_path, game_versions=None, loaders=None):
    """
    Checks if a mod is updatable and updates it to the latest version if possible.

    Args:
        mod_path (str): The path to the mod file.
        game_versions (str, optional): The game version to check for updates. Defaults to None.
        loaders (str, optional): The loader to check for updates. Defaults to None.

    Returns:
        str: An error message if the mod could not be updated. Otherwise, the function returns None.
    """
    sha1_hash = get_sha1_hash(mod_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'

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
    try:
        response = requests.post(url, json=body, headers=headers)
        mod_name = os.path.basename(mod_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_mod_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your mod is on the latest release: {mod_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this mod!')
                print(f'Name: {mod_name}')
                backup_folder = os.path.join(default_minecraft_path, 'mods', 'backup' )
                backup_path = os.path.join(default_minecraft_path, 'mods', 'backup', os.path.basename(mod_path))
                mods_folder = os.path.join(default_minecraft_path, 'mods')
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],mods_folder)
                    print('✅ Latest version of the mod has been downloaded!')
                    try:
                        shutil.move(mod_path, backup_path)
                        print('✅ Old mod file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error

        elif response.status_code == 404:
            wait_for_update_folder = os.path.join(default_minecraft_path, 'mods', 'wait_for_update' )
            wait_for_update_path = os.path.join(default_minecraft_path, 'mods', 'wait_for_update', os.path.basename(mod_path) )
            if not os.path.exists(wait_for_update_folder):
                    os.makedirs(wait_for_update_folder)
            try:
                shutil.move(mod_path, wait_for_update_path)
                print('✅ Mod moved to wait_for_update folder because of incompatibility!')
            except Exception as e:
                error = (f'Error moving file: {e}')
                return error
            print (f'❌ There is no update for {mod_name} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️ Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_update(mod_path, game_versions=None, loaders=None):
    """
    Checks if a mod is up to date by sending a POST request to the Modrinth API.

    Args:
        mod_path (str): The path to the mod file to check.
        game_versions (str, optional): The game version to check against. If None, the current
            Fabric version is used. Defaults to None.
        loaders (str, optional): The loader to check against. If None, the current loader is
            used. Defaults to None.

    Returns:
        str: An error message if an error occurred, otherwise None.
    """
    sha1_hash = get_sha1_hash(mod_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'

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
    try:
        response = requests.post(url, json=body, headers=headers, timeout=15)
        mod_name = os.path.basename(mod_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['version_number'])
            curret_mod_version = fix_version_number(get_local_mod_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your mod is on the latest release: {mod_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this mod!')
                print(f'Name: {mod_name}')
                backup_folder = os.path.join(default_minecraft_path, 'mods', 'backup' )
                backup_path = os.path.join(default_minecraft_path, 'mods', 'backup', os.path.basename(mod_path))
                mods_folder = os.path.join(default_minecraft_path, 'mods')
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],mods_folder)
                    print('✅ Latest version of the mod has been downloaded!')
                    try:
                        shutil.move(mod_path, backup_path)
                        print('✅ Old mod file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            print (f'❌ There is no update for {mod_name} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️ Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def update_mods():

    """
    Checks for updates of all mods in the 'mods' folder of the default Minecraft path.

    This function will loop through all mods in the 'mods' folder and check for updates using the
    check_updateable_mods function. If a mod is updateable, it will be updated using the check_update
    function. Additionally, it will check for any mods in the 'wait_for_update' folder that have been
    previously moved there and check for updates on them as well.

    Args:
        None

    Returns:
        None
    """
    all_mods = get_all_local_mods()
    loader = get_current_loaders()
    loader_version = get_current_fabric_version()
        
    update_in_progress = False

    for mod_file in all_mods:
        updatable_mod = check_updateable_mods(mod_file, loader_version, loader)
        if updatable_mod:
            update_in_progress = True

    wait_for_update_mods = get_wait_for_update_mods()
    wait_for_update_folder = os.path.join(default_minecraft_path, 'mods', 'wait_for_update' )

    if os.path.exists(wait_for_update_folder) and os.listdir(wait_for_update_folder):
        print('❗️ Checking updateable mods in the wait_for_update folder...')
        for mod_file in wait_for_update_mods:
            wait_for_update_mod = check_update(mod_file, loader_version, loader)
            if wait_for_update_mod:
                update_in_progress = True
    if not update_in_progress:
        print('✅ All mods are up to date!')

if __name__ == "__main__":
    update_mods()
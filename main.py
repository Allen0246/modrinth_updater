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

env_run_mods_update = os.getenv('RUN_MODS_UPDATER')
env_run_resourepacks_update = os.getenv('RUN_RESOUREPACKS_UPDATER')
env_run_shaderpacks_update = os.getenv('RUN_SHADERPACKS_UPDATER')

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

def download_mod(url, save_folder, mod_name=None):
    """
    Downloads a file from the given URL and saves it to the given folder.
    
    Args:
        url (str): The URL of the file to download.
        save_folder (str): The folder to save the file in.
        mod_name (str, optional): The name to give the downloaded file. If None, the filename
            will be determined from the URL. Defaults to None.
    
    Returns:
        str: The path to the saved file, or an error message if the file could not be downloaded.
    """
    if mod_name is None:
        mod_name = os.path.basename(url)
        mod_name = urllib.parse.unquote(mod_name)
    save_path = os.path.join(save_folder, mod_name)
    try:
        response = requests.get(url, stream=True, timeout=5)
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
    Removes any snapshot versions from a list of game versions and returns the highest version number.

    Args:
        game_versions (list): A list of game versions to filter.

    Returns:
        str: The highest version number without any snapshot versions, or an error message if an error occurred.
    """
    try:
        with_out_snapshot = [v for v in game_versions if 'w' not in v.lower()]
        return max(with_out_snapshot, key=Version)
    except Exception as e:
        print(f'An error occurred with versioning: {e}')

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

def get_latest_mod_versions(project_id):
    """
    Retrieves the latest stable version of a mod by sending a GET request to the Modrinth API with the specified project ID.

    Args:
        project_id (str): The project ID of the mod to retrieve the latest version for.

    Returns:
        str: The latest stable version string of the mod, or an error message if the mod could not be found or an error occurred.
    """
    url = f'https://api.modrinth.com/v2/project/{project_id}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            filtered_latest_mod_versions = [v for v in data['game_versions'] if 'w' not in v]
            return filtered_latest_mod_versions[-1]
        elif response.status_code == 404:
            print (f'❌ Cannot find the mod witht the project id: {project_id}')
        else:
            print(f'⚠️  Error: {response.status_code}')
            return response
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def get_current_loader(path = default_minecraft_path):
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

def get_local_version(hash):
    """
    Retrieves the local version of a mod by sending a GET request to the Modrinth API with the specified hash.

    Args:
        hash (str): The hash of the mod to retrieve the local version for.

    Returns:
        str: The local version of the mod, or an error message if the mod could not be found or an error occurred.
    """
    url = f'https://api.modrinth.com/v2/version_file/{hash}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['game_versions']
        elif response.status_code == 404:
            print (f'❌ Cannot find the mod with the hash: {hash}')
        else:
            print(f'  Error: {response.status_code}')
            print(response.text)
            return response
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

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

def get_wait_for_update_mods(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all local mods in the 'wait_for_update' folder of the specified directory.

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
    wait_for_update_folder = os.path.join(path, 'modrinth_updater', 'mods', 'wait_for_update')
    list_mods = []
    for mods in os.listdir(wait_for_update_folder):
        mods_with_path = os.path.join(wait_for_update_folder, mods)
        if os.path.isfile(mods_with_path):
            if only_name:
                list_mods.append(os.path.basename(mods_with_path))
            else:
                list_mods.append(mods_with_path)
    return list_mods

def get_all_resource_packs(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of resourcepacks in the specified directory.

    This function scans the 'resourcepacks' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the resourcepacks found.

    Args:
        only_name (bool, optional): If True, returns only the resourcepack file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'resourcepacks' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of resourcepack file names or full paths depending on the `only_name` parameter.
    """
    resurce_packs_folder = os.path.join(path, 'resourcepacks')
    list_resource_packs = []
    for resource_pack in os.listdir(resurce_packs_folder):
        resource_pack_with_path = os.path.join(resurce_packs_folder, resource_pack)
        if os.path.isfile(resource_pack_with_path):
            if only_name:
                list_resource_packs.append(os.path.basename(resource_pack_with_path))
            else:
                list_resource_packs.append(resource_pack_with_path)
    return list_resource_packs

def get_wait_for_update_resource_packs(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of resourcepacks that are waiting for an update in the specified directory.

    This function scans the 'wait_for_update' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the resourcepacks found.

    Args:
        only_name (bool, optional): If True, returns only the resourcepack file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'wait_for_update' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of resourcepack file names or full paths depending on the `only_name` parameter.
    """
    resurce_packs_folder = os.path.join(path, 'modrinth_updater', 'resourcepacks', 'wait_for_update')
    if not os.path.exists(resurce_packs_folder):
                    os.makedirs(resurce_packs_folder)
    list_resource_packs = []
    for resource_pack in os.listdir(resurce_packs_folder):
        resource_pack_with_path = os.path.join(resurce_packs_folder, resource_pack)
        if os.path.isfile(resource_pack_with_path):
            if only_name:
                list_resource_packs.append(os.path.basename(resource_pack_with_path))
            else:
                list_resource_packs.append(resource_pack_with_path)
    return list_resource_packs

def get_all_shaderpacks(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all local shaderpacks in the specified directory.

    This function scans the 'shaderpacks' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the shaderpacks found.

    Args:
        only_name (bool, optional): If True, returns only the shaderpack file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'shaderpacks' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of shaderpack file names or full paths depending on the `only_name` parameter.
    """
    shaderpacks_folder = os.path.join(path, 'shaderpacks')
    list_shaderpacks = []
    for shaderpack in os.listdir(shaderpacks_folder):
        shaderpacks_with_path = os.path.join(shaderpacks_folder, shaderpack)
        if os.path.isfile(shaderpacks_with_path):
            if only_name:
                list_shaderpacks.append(os.path.basename(shaderpacks_with_path))
            else:
                list_shaderpacks.append(shaderpacks_with_path)
    return list_shaderpacks

def get_wait_for_update_shaderpacks(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all local shaderpacks in the specified directory.

    This function scans the 'wait_for_update' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the shaderpacks found.

    Args:
        only_name (bool, optional): If True, returns only the shaderpack file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'wait_for_update' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of shaderpack file names or full paths depending on the `only_name` parameter.
    """
    shaderpacks_folder = os.path.join(path, 'modrinth_updater', 'shaderpacks', 'wait_for_update')
    if not os.path.exists(shaderpacks_folder):
                    os.makedirs(shaderpacks_folder)
    list_shaderpacks = []
    for shaderpack in os.listdir(shaderpacks_folder):
        shaderpacks_with_path = os.path.join(shaderpacks_folder, shaderpack)
        if os.path.isfile(shaderpacks_with_path):
            if only_name:
                list_shaderpacks.append(os.path.basename(shaderpacks_with_path))
            else:
                list_shaderpacks.append(shaderpacks_with_path)
    return list_shaderpacks

def check_updateable_mods(mod_path, game_versions=None, loaders=None):
    """
    Checks if a mod is updatable and updates it to the latest version if possible.

    Args:
        mod_path (str): The path to the mod file.
        game_versions (str, optional): The game version to check for updates. Defaults to None.
        loaders (str, optional): The loader to check for updates. Defaults to None.

    Returns:
        str: An error message if the mod could not be updated, otherwise None.
    """
    sha1_hash = get_sha1_hash(mod_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods' ,'backup', os.path.basename(mod_path))
    mods_folder = os.path.join(default_minecraft_path, 'mods')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        mod_name = os.path.basename(mod_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your mod is on the latest release: {mod_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this mod!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],mods_folder)
                    print('⬇️ Latest version of the mod has been downloaded!')
                    try:
                        shutil.move(mod_path, backup_path)
                        print('📦 Old mod file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error

        elif response.status_code == 404:
            wait_for_update_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'wait_for_update' )
            wait_for_update_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'wait_for_update', os.path.basename(mod_path) )
            if not os.path.exists(wait_for_update_folder):
                    os.makedirs(wait_for_update_folder)
            try:
                shutil.move(mod_path, wait_for_update_path)
                print ("⚠️  The mod moved to the 'modrinth_updater/mods/wait_for_update' folder because of incompatibility!")
            except Exception as e:
                error = (f'Error moving file: {e}')
                return error
            print (f'❌ There is no update for {mod_path} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_wait_for_update_mods(mod_path, game_versions=None, loaders=None):
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
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup', os.path.basename(mod_path))
    mods_folder = os.path.join(default_minecraft_path, 'mods')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        mod_name = os.path.basename(mod_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your mod is on the latest release: {mod_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this mod!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],mods_folder)
                    print('⬇️ Latest version of the mod has been downloaded!')
                    try:
                        shutil.move(mod_path, backup_path)
                        print('📦 Old mod file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            print (f'❌ There is no update for {mod_name} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_updateable_resourcepacks(resourcepacks_path, game_versions=None, loaders=None):
    """
    Checks if a resource pack is updatable and updates it to the latest version if possible.

    Args:
        resourcepacks_path (str): The path to the resource pack file.
        game_versions (str, optional): The game version to check for updates. Defaults to None.
        loaders (str, optional): The loader to check for updates. Defaults to None.

    Returns:
        str: An error message if the resource pack could not be updated, otherwise None.
    """
    sha1_hash = get_sha1_hash(resourcepacks_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup', os.path.basename(resourcepacks_path))
    resourcepacks_folder = os.path.join(default_minecraft_path, 'resourcepacks')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        resourcepack_name = os.path.basename(resourcepacks_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            print(latest_mod_version)
            print(type(latest_mod_version))
            print(curret_mod_version)
            print(type(curret_mod_version))
            print(loader_version)
            print(type(loader_version))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your resource pack is on the latest release: {resourcepack_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this resource pack!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],resourcepacks_folder)
                    print('⬇️ Latest version of the resource pack has been downloaded!')
                    try:
                        shutil.move(resourcepacks_path, backup_path)
                        print('📦 Old resource pack file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            wait_for_update_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update' )
            wait_for_update_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update', os.path.basename(resourcepacks_path) )
            if not os.path.exists(wait_for_update_folder):
                    os.makedirs(wait_for_update_folder)
            try:
                shutil.move(resourcepacks_path, wait_for_update_path)
                print ("⚠️  The resource pack moved to the 'modrinth_updater/resourcepacks/wait_for_update' folder because of incompatibility!")
            except Exception as e:
                error = (f'Error moving file: {e}')
                return error
            print (f'❌ There is no update for {resourcepacks_path} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')


def check_wait_for_update_resourcepacks(resourcepacks_path, game_versions=None, loaders=None):
    """
    Checks if a resource pack is up to date by sending a POST request to the Modrinth API.

    Args:
        resourcepacks_path (str): The path to the resource pack file to check.
        game_versions (str, optional): The game version to check against. If None, the current
            Fabric version is used. Defaults to None.
        loaders (str, optional): The loader to check against. If None, the current loader is
            used. Defaults to None.

    Returns:
        str: An error message if an error occurred, otherwise None.
    """
    sha1_hash = get_sha1_hash(resourcepacks_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup', os.path.basename(resourcepacks_path))
    resourcepacks_folder = os.path.join(default_minecraft_path, 'resourcepacks')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        resourcepack_name = os.path.basename(resourcepacks_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your resource pack is on the latest release: {resourcepack_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this resource pack!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],resourcepacks_folder)
                    print('⬇️ Latest version of the resource pack has been downloaded!')
                    try:
                        shutil.move(resourcepacks_path, backup_path)
                        print('📦 Old resource pack file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            print (f'❌ There is no update for {resourcepack_name} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_updateable_shaderpacks(shaderpacks_path, game_versions=None, loaders=None):
    """
    Checks if a shaderpack is updatable and updates it to the latest version if possible.

    Args:
        shaderpacks_path (str): The path to the shaderpack file.
        game_versions (str, optional): The game version to check for updates. Defaults to None.
        loaders (str, optional): The loader to check for updates. Defaults to None.

    Returns:
        str: An error message if the shaderpack could not be updated, otherwise None.
    """
    sha1_hash = get_sha1_hash(shaderpacks_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup', os.path.basename(shaderpacks_path))
    shaderpacks_folder = os.path.join(default_minecraft_path, 'shaderpacks')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        shaderpacks_name = os.path.basename(shaderpacks_path)
        if response.status_code == 200:
            data = response.json()
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your shaderpack is on the latest release: {shaderpacks_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this shaderpack!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],shaderpacks_folder)
                    print('⬇️ Latest version of the shaderpack has been downloaded!')
                    try:
                        shutil.move(shaderpacks_path, backup_path)
                        print('📦 Old shaderpack file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            wait_for_update_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update' )
            wait_for_update_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update', os.path.basename(shaderpacks_path) )
            if not os.path.exists(wait_for_update_folder):
                    os.makedirs(wait_for_update_folder)
            try:
                shutil.move(shaderpacks_path, wait_for_update_path)
                print ("⚠️  The shaderpack moved to the 'modrinth_updater/shaderpacks/wait_for_update' folder because of incompatibility!")
            except Exception as e:
                error = (f'Error moving file: {e}')
                return error
            print (f'❌ There is no update for {shaderpacks_path} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_wait_for_update_shaderpacks(shaderpacks_path, game_versions=None, loaders=None):
    """
    Checks if a shaderpack is up to date by sending a POST request to the Modrinth API.

    Args:
        shaderpacks_path (str): The path to the shaderpack file to check.
        game_versions (str, optional): The game version to check against. If None, the current
            Fabric version is used. Defaults to None.
        loaders (str, optional): The loader to check against. If None, the current loader is
            used. Defaults to None.

    Returns:
        str: An error message if an error occurred, otherwise None.
    """
    sha1_hash = get_sha1_hash(shaderpacks_path)
    url = f'https://api.modrinth.com/v2/version_file/{sha1_hash}/update'
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup', os.path.basename(shaderpacks_path))
    shaderpacks_folder = os.path.join(default_minecraft_path, 'shaderpacks')

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
        response = requests.post(url, json=body, headers=headers, timeout=5)
        shaderpacks_name = os.path.basename(shaderpacks_path)
        if response.status_code == 200:
            data = response.json()
            print(data)
            latest_mod_version = fix_version_number(data['game_versions'])
            curret_mod_version = fix_version_number(get_local_version(sha1_hash))
            if latest_mod_version == curret_mod_version:
                print (f'✅ Your shaderpack is on the latest release: {shaderpacks_name}! Your loader is {loaders}-{loader_version}.')
            elif latest_mod_version > curret_mod_version:
                print('🚀 A newer version is available of this shaderpack!')
                print(f"Name: {data['name']}")
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)
                try:
                    download_mod(data['files'][0]['url'],shaderpacks_folder)
                    print('⬇️ Latest version of the shaderpack has been downloaded!')
                    try:
                        shutil.move(shaderpacks_path, backup_path)
                        print('📦 Old shaderpack file moved to the backup folder!')
                    except Exception as e:
                        error = (f'Error moving file: {e}')
                        return error
                except Exception as e:
                    error = (f'Error downloading file: {e}')
                    return error
        elif response.status_code == 404:
            print (f'❌ There is no update for {shaderpacks_name} your loader is {loaders}-{game_versions}.')
        else:
            print(f'⚠️  Error: {response.status_code}')
            print(response.text)
    except requests.exceptions.Timeout:
        print('The request timed out!')
    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

def check_update():
    """
    Checks for updates for mods, resource packs and shader packs in the Minecraft directory.

    The function checks the `env_run_mods_update`, `env_run_resourepacks_update` and `env_run_shaderpacks_update` variables from the .env file to determine if the respective updaters should be run.

    If the updaters are enabled, the function gets the list of all local mods, resource packs and shader packs, and checks each of them for updates by calling the respective functions.

    If a mod, resource pack or shader pack is found to be updatable, the function moves the old version to the backup folder and downloads the new version.

    If the updaters are disabled, the function prints a message indicating that the updaters are disabled in the .env file.

    Finally, the function prints a message indicating whether everything is up to date or not.
    """
    all_mods = get_all_local_mods()
    loader = get_current_loader()
    loader_version = get_current_fabric_version()
    all_resource_packs = get_all_resource_packs()
    all_shaderpacks = get_all_shaderpacks()
        
    update_in_progres = False

    if env_run_mods_update == "true":
        # get wait for update mods
        wait_for_update_mods = get_wait_for_update_mods()
        wait_for_update_mods_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'wait_for_update' )
        #updating mods
        for mod_file in all_mods:
            updatable_mod = check_updateable_mods(mod_file, loader_version, loader)
            if updatable_mod:
                update_in_progres = True
        if os.path.exists(wait_for_update_mods_folder) and os.listdir(wait_for_update_mods_folder):
            print('❗️ Checking updateable mods in the wait_for_update folder...')
            for mod_file in wait_for_update_mods:
                wait_for_update_mod = check_wait_for_update_mods(mod_file, loader_version, loader)
                if wait_for_update_mod:
                    update_in_progres = True
            print('✅ Every mods are up to date')
    elif env_run_mods_update == "false":
        print('⚠️  Mods updater is disabled in the .env file!')

    if env_run_resourepacks_update == "true":
        #get wait for update resource packs
        wait_for_update_resource_packs = get_wait_for_update_resource_packs()
        wait_for_update_resourcepacks_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update' )
        #updating resource packs
        for resource_pack_file in all_resource_packs:
            updatable_resource_packs = check_updateable_resourcepacks(resource_pack_file, loader_version, None)
            if updatable_resource_packs:
                update_in_progres = True
        if os.path.exists(wait_for_update_resourcepacks_folder) and os.listdir(wait_for_update_resourcepacks_folder):
            print('❗️ Checking updateable resource packs in the wait_for_update folder...')
            for resource_pack_file in wait_for_update_resource_packs:
                wait_for_update_resource_pack = check_wait_for_update_resourcepacks(resource_pack_file, loader_version, None)
                if wait_for_update_resource_pack:
                    update_in_progres = True
            print('✅ Every resoucepacks are up to date')
    elif env_run_resourepacks_update == "false":
        print('⚠️  Resourcepacks updater is disabled in the .env file!')

    if env_run_shaderpacks_update == "true":
        #get wait for update shader packs
        wait_for_update_shaderpacks = get_wait_for_update_shaderpacks()
        wait_for_update_shaderpacks_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update' )
        #updating shader packs
        for shaderpack_file in all_shaderpacks:
            updatable_shaderpacks = check_updateable_shaderpacks(shaderpack_file, loader_version, None)
            if updatable_shaderpacks:
                update_in_progres = True
        if os.path.exists(wait_for_update_shaderpacks_folder) and os.listdir(wait_for_update_shaderpacks_folder):
            print('❗️ Checking updateable resource packs in the wait_for_update folder...')
            for shaderpack_file in wait_for_update_shaderpacks:
                wait_for_update_shaderpacks = check_wait_for_update_shaderpacks(shaderpack_file, loader_version, None)
                if wait_for_update_shaderpacks:
                    update_in_progres = True
        print('✅ Every shaderpacks are up to date')
    elif env_run_shaderpacks_update == "false":
        print('⚠️  Shaderpacks updater is disabled in the .env file!')

    if not update_in_progres:
        print('✅ Everything is up to date!')

if __name__ == "__main__":
    check_update()
import os
import urllib.parse
import json
from packaging.version import Version
import requests
from modrinth_updater.config import default_minecraft_path

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
        response = requests.get(url, stream=True, timeout=15)
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
        if isinstance(game_versions, str):
            game_versions = [game_versions]
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
            versions =[]
            for loaders in data['profiles']:
                if 'fabric' in loaders:
                    loader_name.append(loaders)
            if len(loader_name) < 2:
                fabric_version = loader_name[0].split('-')[-1]
                return fabric_version
            elif len(loader_name) >= 2:
                for vers in loader_name:
                    versions.append(vers.split('-')[-1])
                fabric_version = [v for v in versions if 'w' not in v.lower()]
                fabric_version = (max(fabric_version, key=Version))
                return fabric_version
            else:
                if not loader_name:
                    print('No fabric version found.')
                    return loader_name
    except Exception as e:
        error = (f'Error reading launcher_profiles.json: {e}')
        return error

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

def get_all_save_folder(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all local saves in the specified directory.

    This function scans the 'saves' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the saves found.

    Args:
        only_name (bool, optional): If True, returns only the save file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'saves' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of save file names or full paths depending on the `only_name` parameter.
    """
    saves_folder = os.path.join(path, 'saves')
    list_save_folders = []
    for save in os.listdir(saves_folder):
        save_with_path = os.path.join(saves_folder, save)
        if os.path.isfile(save_with_path):
            if only_name:
                list_save_folders.append(os.path.basename(save_with_path))
            else:
                list_save_folders.append(save_with_path)
    return list_save_folders

def get_all_datapacks(save_folder , only_name = False):
    """
    Retrieves a list of all datapacks in the specified save folder.

    This function scans the 'datapacks' folder within the specified save folder path 
    and returns a list of either the full paths or just the file names of the datapacks found.

    Args:
        save_folder (str): The path to the save folder.
        only_name (bool, optional): If True, returns only the datapack file names. 
                                    If False, returns the full paths. Defaults to False.

    Returns:
        list: A list of datapack file names or full paths depending on the `only_name` parameter.
    """
    datapacks_folder_path = os.path.join(save_folder, 'datapacks')
    datapacks = []
    for datapack in os.listdir(datapacks_folder_path):
        datapacks_with_path = os.path.join(save_folder, datapack)
        if os.path.isfile(datapacks_with_path):
            if only_name:
                datapacks.append(os.path.basename(datapacks_with_path))
            else:
                datapacks.append(datapacks_with_path)
    return datapacks

def get_wait_for_update_save_folder(only_name = False, path = default_minecraft_path):
    """
    Retrieves a list of all saves in the 'wait_for_update' folder of the specified directory.

    This function scans the 'wait_for_update' folder within the specified directory path 
    and returns a list of either the full paths or just the file names of the saves found.

    Args:
        only_name (bool, optional): If True, returns only the save file names. 
                                    If False, returns the full paths. Defaults to False.
        path (str, optional): The path to the directory containing the 'wait_for_update' folder. 
                              Defaults to the global variable `default_minecraft_path`.

    Returns:
        list: A list of save file names or full paths depending on the `only_name` parameter.
    """
    datapacks_folder = os.path.join(path, 'modrinth_updater', 'datapacks', 'wait_for_update')
    if not os.path.exists(datapacks_folder):
                    os.makedirs(datapacks_folder)
    list_save_folders = []
    for save in os.listdir(datapacks_folder):
        save_with_path = os.path.join(datapacks_folder, save)
        if os.path.isfile(save_with_path):
            if only_name:
                list_save_folders.append(os.path.basename(save_with_path))
            else:
                list_save_folders.append(save_with_path)
    return list_save_folders

def get_wait_for_update_datapacks(save_folder , only_name = False):
    """
    Retrieves a list of all datapacks in the 'wait_for_update' folder of the specified save folder.

    This function scans the 'wait_for_update' folder within the specified save folder path 
    and returns a list of either the full paths or just the file names of the datapacks found.

    Args:
        save_folder (str): The path to the save folder.
        only_name (bool, optional): If True, returns only the datapack file names. 
                                    If False, returns the full paths. Defaults to False.

    Returns:
        list: A list of datapack file names or full paths depending on the `only_name` parameter.
    """
    datapacks_folder_path = os.path.join(save_folder, 'datapacks')
    datapacks = []
    for datapack in os.listdir(datapacks_folder_path):
        datapacks_with_path = os.path.join(save_folder, datapack)
        if os.path.isfile(datapacks_with_path):
            if only_name:
                datapacks.append(os.path.basename(datapacks_with_path))
            else:
                datapacks.append(datapacks_with_path)
    return datapacks
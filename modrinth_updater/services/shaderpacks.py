import os
import shutil
from modrinth_updater.config import default_minecraft_path
from modrinth_updater.modrinth_api import check_update, get_local_version
from modrinth_updater.file_utils import fix_version_number, download_mod

def check_updateable_shaderpacks(shaderpacks_path, game_versions=None, loaders=None):
    """
    Checks if the given shaderpack is updatable, and if so, downloads and backs up the old file.
    If the shaderpack is not supported or incompatible, it is moved to the 'wait_for_update' folder.

    Args:
        shaderpacks_path (str): The path to the shaderpack to check for updates.
        game_versions (str, optional): The game version. Defaults to None.
        loaders (str, optional): The loader version. Defaults to None.

    Returns:
        str: An error message if something went wrong, otherwise None.
    """
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup', os.path.basename(shaderpacks_path))
    shaderpacks_folder = os.path.join(default_minecraft_path, 'shaderpacks')
    wait_for_update_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update' )
    wait_for_update_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update', os.path.basename(shaderpacks_path) )
    if not os.path.exists(wait_for_update_folder):
        os.makedirs(wait_for_update_folder)

    response, loader_version, loaders, sha1_hash = check_update(shaderpacks_path, game_versions, loaders)
    shaderpacks_name = os.path.basename(shaderpacks_path)
    if response is None:
        print(f'⚠️ Cannot update this shaderpack: {shaderpacks_name} because the update check failed.')
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
        try:
            shutil.move(shaderpacks_path, wait_for_update_path)
            print ("⚠️  The shaderpack moved to the 'modrinth_updater/shaderpacks/wait_for_update' folder because of incompatibility!")
        except Exception as e:
            error = (f'Error moving file: {e}')
            return error
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

def check_wait_for_update_shaderpacks(shaderpacks_path, game_versions=None, loaders=None):
    """
    Checks if a shaderpack in the 'wait_for_update' folder is now compatible with
    the current Minecraft version and loader. If compatible, it downloads the 
    latest version and backs up the old file. If not compatible, it prints a 
    message indicating the incompatibility.

    Args:
        shaderpacks_path (str): The path to the shaderpack file.
        game_versions (list, optional): A list of compatible game versions. Defaults to None.
        loaders (list, optional): A list of compatible loaders. Defaults to None.

    Returns:
        str: An error message if there is an issue during the download or move process, otherwise None.
    """

    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'backup', os.path.basename(shaderpacks_path))
    shaderpacks_folder = os.path.join(default_minecraft_path, 'shaderpacks')
    response, loader_version, loaders, sha1_hash = check_update(shaderpacks_path, game_versions, loaders)
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
        return
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

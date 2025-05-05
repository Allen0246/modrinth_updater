import os
import shutil
from modrinth_updater.config import default_minecraft_path
from modrinth_updater.modrinth_api import check_update, get_local_version
from modrinth_updater.file_utils import fix_version_number, download_mod

def check_updateable_resourcepacks(resourcepacks_path, game_versions=None, loaders=None):
    """
    Checks if the given resource pack is updatable, and if so, downloads and backs up the old file.
    If the resource pack is not supported or incompatible, it is moved to the 'wait_for_update' folder.

    Args:
        resourcepacks_path (str): The path to the resource pack to check for updates.
        game_versions (str, optional): The game version. Defaults to None.
        loaders (str, optional): The loader version. Defaults to None.

    Returns:
        str: An error message if something went wrong, otherwise None.
    """
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup', os.path.basename(resourcepacks_path))
    resourcepacks_folder = os.path.join(default_minecraft_path, 'resourcepacks')
    response, loader_version, loaders, sha1_hash = check_update(resourcepacks_path, game_versions, loaders)
    resourcepack_name = os.path.basename(resourcepacks_path)
    if response is None:
        print(f'⚠️ Cannot update this resource pack: {resourcepack_name} because the update check failed.')
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
        try:
            wait_for_update_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update' )
            wait_for_update_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update', os.path.basename(resourcepacks_path) )
            if not os.path.exists(wait_for_update_folder):
                os.makedirs(wait_for_update_folder)
            shutil.move(resourcepacks_path, wait_for_update_path)
            print ("⚠️  The resource pack moved to the 'modrinth_updater/resourcepacks/wait_for_update' folder because of incompatibility!")
        except Exception as e:
            error = (f'Error moving file: {e}')
            return error
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

def check_wait_for_update_resourcepacks(resourcepacks_path, game_versions=None, loaders=None):
    """
    Checks if a resource pack in the 'wait_for_update' folder is now compatible with the current 
    Minecraft version and loader. If compatible, it downloads the latest version and backs up the 
    old file. If not compatible, it prints a message indicating the incompatibility.

    Args:
        resourcepacks_path (str): The path to the resource pack file.
        game_versions (list, optional): A list of compatible game versions. Defaults to None.
        loaders (list, optional): A list of compatible loaders. Defaults to None.

    Returns:
        str: An error message if there is an issue during the download or move process, otherwise None.
    """

    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'backup', os.path.basename(resourcepacks_path))
    resourcepacks_folder = os.path.join(default_minecraft_path, 'resourcepacks')
    response, loader_version, loaders, sha1_hash = check_update(resourcepacks_path, game_versions, loaders)
    resourcepack_name = os.path.basename(resourcepacks_path)
    if response is None:
        print("⚠️ Cannot update this resurce pack because the update check failed.")
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
        return
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

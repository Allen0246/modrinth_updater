import os
import shutil
from modrinth_updater.config import default_minecraft_path
from modrinth_updater.modrinth_api import check_update, get_local_version
from modrinth_updater.file_utils import fix_version_number, download_mod

def check_updateable_mods(mod_path, game_versions=None, loaders=None):
    """
    Checks if a mod is updateable and updates it if there is a newer version.

    Parameters
    ----------
    mod_path : str
        The path to the mod file.
    game_versions : list, optional
        A list of game versions to support, by default None.
    loaders : list, optional
        A list of loaders to support, by default None.

    Returns
    -------
    str
        An error message if there was an error.
    """
    
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods' ,'backup', os.path.basename(mod_path))
    mods_folder = os.path.join(default_minecraft_path, 'mods')

    response, loader_version, loaders, sha1_hash = check_update(mod_path, game_versions, loaders)
    mod_name = os.path.basename(mod_path)
    if response is None:
        print(f'⚠️ Cannot update this mod: {mod_name} because the update check failed.')
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
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

def check_wait_for_update_mods(mod_path, game_versions=None, loaders=None):
    """
    This function will check if the mods in the 'modrinth_updater/mods/wait_for_update' folder are now compatible with the current Minecraft version and loader.

    If the mod is compatible, it will download the latest version, move the old file to the 'modrinth_updater/mods/backup' folder and the new file to the mods folder.

    If the mod is not compatible, it will print a message with the loader and Minecraft version that is incompatible.

    :param mod_path: The path to the mod file
    :param game_versions: A list of Minecraft versions to check for compatibility
    :param loaders: A list of loaders to check for compatibility
    :return: An error message if there is an issue downloading or moving the file
    """
    backup_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup' )
    backup_path = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'backup', os.path.basename(mod_path))
    mods_folder = os.path.join(default_minecraft_path, 'mods')
    response, loader_version, loaders, sha1_hash = check_update(mod_path, game_versions, loaders)
    mod_name = os.path.basename(mod_path)
    if response is None:
        print("⚠️ Cannot update this mod because the update check failed.")
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
        return
    else:
        print(f'⚠️  Error: {response.status_code}')
        print(response.text)

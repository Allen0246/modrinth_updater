import os
from modrinth_updater.config import default_minecraft_path, env_run_mods_update, env_run_resourepacks_update, env_run_shaderpacks_update
from modrinth_updater.file_utils import get_all_local_mods, get_all_resource_packs, get_all_shaderpacks, get_wait_for_update_mods, get_wait_for_update_resource_packs, get_wait_for_update_shaderpacks, get_current_fabric_version, get_current_loader
from modrinth_updater.services.mods import check_updateable_mods, check_wait_for_update_mods
from modrinth_updater.services.resourcepacks import check_updateable_resourcepacks,check_wait_for_update_resourcepacks
from modrinth_updater.services.shaderpacks import check_updateable_shaderpacks, check_wait_for_update_shaderpacks
def update():
    """
    Main function to update mods, resourcepacks and shaderpacks based on
    the Modrinth API.

    This function will check if the mods, resourcepacks and shaderpacks in the
    Minecraft folder are up to date. If they are not, it will download the latest
    version and move the old file to the 'wait_for_update' folder. If the file
    is in the 'wait_for_update' folder, it will check if the file is now
    compatible with the current Minecraft version and loader, and if it is,
    it will move the file back to the mods folder.

    The function will also print some information about what it is doing and
    if everything is up to date or not.

    """
    
    all_mods = get_all_local_mods()
    loader = get_current_loader()
    loader_version = get_current_fabric_version()
    all_resource_packs = get_all_resource_packs()
    all_shaderpacks = get_all_shaderpacks()
        
    update_in_progres = False

    if env_run_mods_update == "true":
        # get wait for update mods
        print('❗️ Checking updateable mods in the mods folder...')
        #updating mods
        for mod_file in all_mods:
            updatable_mod = check_updateable_mods(mod_file, loader_version, loader)
            if updatable_mod:
                update_in_progres = True
        wait_for_update_mods = get_wait_for_update_mods()
        wait_for_update_mods_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'mods', 'wait_for_update' )
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
        print('❗️ Checking updateable resource packs in the resourcepacks folder...')
        #updating resource packs
        for resource_pack_file in all_resource_packs:
            updatable_resource_packs = check_updateable_resourcepacks(resource_pack_file, loader_version, None)
            if updatable_resource_packs:
                update_in_progres = True
        wait_for_update_resource_packs = get_wait_for_update_resource_packs()
        wait_for_update_resourcepacks_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'resourcepacks', 'wait_for_update' )
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
        print('❗️ Checking updateable shaderpacks in the shaderpacks folder...')
        #updating shader packs
        for shaderpack_file in all_shaderpacks:
            updatable_shaderpacks = check_updateable_shaderpacks(shaderpack_file, loader_version, None)
            if updatable_shaderpacks:
                update_in_progres = True
        wait_for_update_shaderpacks = get_wait_for_update_shaderpacks()
        wait_for_update_shaderpacks_folder = os.path.join(default_minecraft_path, 'modrinth_updater', 'shaderpacks', 'wait_for_update' )
        if os.path.exists(wait_for_update_shaderpacks_folder) and os.listdir(wait_for_update_shaderpacks_folder):
            print('❗️ Checking updateable shaderpacks in the wait_for_update folder...')
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
    update()
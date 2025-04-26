from dotenv import load_dotenv
import os

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
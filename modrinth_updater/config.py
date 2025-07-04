import os
import platform
from dotenv import load_dotenv

load_dotenv(override=True)
system = platform.system()

# If your system is Windows, then the default path is C:\Users\%USERNAME%\AppData\Roaming\.minecraft
if system == 'Windows':
    env_mc_path = os.getenv('DEFAULT_WINDOWS_MC_FOLDER')
    if env_mc_path:
        default_minecraft_path = env_mc_path
    else:
        appdata_path = os.getenv('APPDATA')
        default_minecraft_path = os.path.join(appdata_path, '.minecraft')
# If your system is macOS, then the default path is ~/Library/Application Support/minecraft
elif system == 'Darwin':
    env_mc_path = os.getenv('DEFAULT_MACOS_MC_FOLDER')
    if env_mc_path:
        default_minecraft_path = env_mc_path
    else:
        default_minecraft_path = os.path.expanduser('~/Library/Application Support/minecraft')
# If your system is Linux, then the default path is ~/.minecraft
elif system == 'Linux':
    env_mc_path = os.getenv('DEFAULT_LINUX_MC_FOLDER')
    if env_mc_path:
        default_minecraft_path = env_mc_path
    else:
        default_minecraft_path = os.path.expanduser('~/.minecraft')

env_run_mods_update = os.getenv('RUN_MODS_UPDATER')
env_run_resourepacks_update = os.getenv('RUN_RESOUREPACKS_UPDATER')
env_run_shaderpacks_update = os.getenv('RUN_SHADERPACKS_UPDATER')

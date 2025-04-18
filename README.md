# 🧩 Modrinth Auto Updater for Mods, Resource Packs & Shader Packs

A Python-based automation tool that checks, updates, and manages your **Minecraft mods, resourcepacks, and shaderpacks** using the [Modrinth API](https://docs.modrinth.com/). Perfect for keeping your Minecraft installation clean, compatible, and up-to-date — with automatic backups and version detection.

---

## 📦 Features

- ✅ **Auto-update mods, resourcepacks, and shaderpacks**
- 💾 **Backup old versions** before replacing
- 🔍 **Match files using SHA1 hash** with Modrinth’s version API
- 📂 **Detect current Minecraft loader and version**
- 🧠 **Smart snapshot filtering** — ignores snapshot/pre-release versions
- 🕵️ **Separate folders** for incompatible mods: `wait_for_update`
- ⚙️ Supports `Fabric`, with basic detection for `Forge`, `NeoForge`, and `Quilt` (update logic applies to Fabric)

---

## 📋 Requirements

- Python 3.7+
- Minecraft installed (preferably with Fabric)
- Mods/Resourcepacks/Shaderpacks placed in their respective Minecraft folders
- Internet connection for API calls
- Mod files must exist on [Modrinth](https://modrinth.com)

---

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/modrinth-multi-updater.git
cd modrinth-multi-updater
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
requests
packaging
python-dotenv
```

---

### 3. Configure `.env` File

Create a `.env` file in the project root:

```env
# Path to Minecraft folder
DEFAULT_MC_FOLDER=C:/Users/YourName/AppData/Roaming/.minecraft

# Enable or disable different updaters
RUN_MODS_UPDATER=true
RUN_RESOUREPACKS_UPDATER=true
RUN_SHADERPACKS_UPDATER=true
```

---

## 🚀 Usage

Just run the script:

```bash
python tets.py
```

---

## 📁 Folder Structure

```
.minecraft/
├── mods/
│   └── *.jar                      # Installed mods
├── resourcepacks/
│   └── *.zip                      # Installed resource packs
├── shaderpacks/
│   └── *.zip                      # Installed shader packs
├── modrinth_updater/
│   ├── mods/
│   │   ├── backup/                # Old mod backups
│   │   ├── wait_for_update/       # Mods not supported by Modrinth or game version
│   ├── resourcepacks/
│   │   ├── backup/                # Resource pack backups
│   │   ├── wait_for_update/       # Unsupported resource packs
│   ├── shaderpacks/
│   │   ├── backup/                # Shader pack backups
│   │   ├── wait_for_update/       # Unsupported shader packs
├── launcher_profiles.json         # Used to detect Minecraft version and loader
```

---

## 🛠 How it Works

1. SHA1 hash is calculated for each file.
2. Hash is checked against Modrinth's database to identify the file.
3. Current version is compared with the latest Modrinth version.
4. If newer: downloads and backs up old file.
5. If unsupported or incompatible: moves file to `wait_for_update`.

---

## 🧪 Sample Output

```bash
🔍 Checking mod: Lithium-0.10.0.jar
✅ Lithium is up-to-date.

🔍 Checking resourcepack: BetterGrass-2.4.7.zip
🚀 A newer version is available!
⬇️ Downloaded: BetterGrass-2.5.0.zip
📦 Old version backed up

⚠️ The shaderpack moved to wait_for_update due to incompatibility.
```

---

## 🧩 Notes

- Only mods **hosted on Modrinth** are supported.
- Snapshot versions like `"25w14a"` are ignored automatically.
- File operations (moving, deleting, downloading) are safe and logged.
- The tool will **recheck waitlisted files** on every run.

---

## 🧾 License

This project is licensed under the MIT License. See `LICENSE`.

---

## 🤝 Contributing

Pull requests, improvements, or new loader support (Forge, NeoForge, Quilt) are welcome!

1. Fork it
2. Make your changes
3. Submit a PR 🚀

---

🎉 Enjoy your fully automated Minecraft mod and pack management!

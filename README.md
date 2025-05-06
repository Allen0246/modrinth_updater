# 🧩 Modrinth Auto Updater — Mods, Resource Packs & Shader Packs

A Python-based automation tool that checks, updates, and manages your Minecraft mods, resourcepacks, shaderpacks, and more using the [Modrinth API](https://docs.modrinth.com/). It performs hash-based version checks and handles file backups and replacements. Currently, only **Fabric** is fully supported.

---

## ✅ Features

- Auto-update mods, resourcepacks, shaderpacks
- Support for datapacks and modpacks (structure in place)
- File SHA1 hash matching with Modrinth's version API
- Minecraft loader and version detection (Fabric only)
- Moves unsupported/incompatible files to a separate folder
- Backup of replaced files

---

## 🛠 Requirements

- Python 3.7+
- Internet connection
- Minecraft installation (with Fabric loader recommended)
- Mods/files must be hosted on [Modrinth](https://modrinth.com)

---

## 🔧 Setup

1. **Clone the repository**:

```bash
git clone https://github.com/Allen0246/modrinth_updater.git
cd modrinth_updater
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

3. **Create a `.env` file** to configure options:

```env
DEFAULT_MC_FOLDER=C:/Users/YourName/AppData/Roaming/.minecraft
RUN_MODS_UPDATER=true
RUN_RESOURCEPACKS_UPDATER=true
RUN_SHADERPACKS_UPDATER=true
```

---

## 🚀 Usage

Run the tool with:

```bash
python main.py
```

---

## 📁 Project Structure

```
modrinth_updater/
├── LICENSE
├── main.py
├── .env
├── README.md
├── requirements.txt
└── modrinth_updater/
    ├── __init__.py
    ├── config.py
    ├── file_utils.py
    ├── hash_utils.py
    ├── modrinth_api.py
    └── services/
        ├── __init__.py
        ├── datapacks.py
        ├── modpacks.py
        ├── mods.py
        ├── resourcepacks.py
        └── shaderpacks.py
```

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

This project is licensed under the MIT License.

---

## 🤝 Contributing

Pull requests and issues are welcome!

---

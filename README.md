# 🧩 Modrinth Mods Updater

A Python-based tool for **automatically checking and updating Minecraft mods** using the [Modrinth API](https://docs.modrinth.com/). Keep your mods folder clean, updated, and compatible — with backup and fallback support built-in.

---

## 📋 Features

- ✅ **Auto-updates mods** based on SHA1 matching via Modrinth.
- 🚧 **Moves unsupported or incompatible mods** to a `wait_for_update` folder.
- 📁 **Backs up old mod versions** to a `backup` folder before replacing them.
- 🔒 Computes and verifies **SHA1/SHA256 hashes** to identify exact files.
- 🔄 **Re-checks mods in waitlist** for updates on future runs.
- 🔧 Currently supports the **Fabric** mod loader (others coming soon).
- 📂 Works with mods stored in the standard `mods` folder of Minecraft.
- ⚡ Detects active Minecraft version and loader from `launcher_profiles.json`.

---

## 🛠️ Prerequisites

Before using this tool, make sure you have:

- 🐍 Python 3.7 or higher
- 📡 Internet access (required for Modrinth API calls)
- 🎮 Minecraft installed with the **Fabric** loader
- 📁 Mods placed in your Minecraft `mods/` directory

---

## 📥 Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/modrinth-mods-updater.git
cd modrinth-mods-updater
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**

```
requests
python-dotenv
packaging
```

### 3. Configure your Minecraft path

By default, the script auto-detects your Minecraft folder based on your OS. To override this:

#### Option A: Edit `main.py` directly

```python
default_minecraft_path = 'C:/Path/To/Your/.minecraft'
```

#### Option B: Use a `.env` file

Create a `.env` file in the project root:

```env
DEFAULT_MC_FOLDER=C:/Path/To/Your/.minecraft
```

---

## 🚀 Usage

Run the script from the terminal:

```bash
python main.py
```

### What It Does

1. Scans your `mods/` folder.
2. Identifies mods with known SHA1 hashes via the Modrinth API.
3. Checks compatibility with your current Minecraft + loader version.
4. Downloads newer versions, if available.
5. Moves old versions to `mods/backup/`.
6. Moves incompatible mods to `mods/wait_for_update/`.
7. Attempts to re-update mods from `wait_for_update/` if now supported.

---

## 🖥️ Example Output

```bash
🔍 Checking mod: Lithium-0.10.0.jar
✅ Lithium is up-to-date.

🔍 Checking mod: SomeOldMod-1.0.0.jar
⚠️ Found newer compatible version!
⬇️ Downloaded: SomeOldMod-1.1.2.jar
📦 Old version moved to: backup/
```

---

## ⚙️ Folder Structure

```plaintext
.minecraft/
├── mods/
│   ├── backup/            # Backups of updated mods
│   ├── wait_for_update/   # Incompatible or unknown mods
│   └── *.jar              # Actual mod files
├── launcher_profiles.json # Used to detect loader & version
```

---

## 🧩 How It Works (Under the Hood)

- Uses SHA1 to identify mods in the Modrinth database.
- Uses your active `launcher_profiles.json` to determine game version and loader.
- Makes Modrinth API calls to:
  - Match hash to a project/version
  - Fetch the latest compatible version
  - Download updated `.jar` files
- Makes smart folder moves to back up or defer incompatible mods.

---

## 📌 Notes

- 🧪 This tool works only with mods hosted on **Modrinth**.
- 💾 Always **back up** your `.minecraft` folder before running if you're unsure.
- 🖇 You can place "pending" mods in `wait_for_update/` — the script will retry them later.
- ⛔ Snapshot Minecraft versions (like `1.20w`) are excluded by default.

---

## 🔒 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.

---

## 🤝 Contributing

Found a bug? Want to add support for Forge, Quilt, or NeoForge? Feel free to:

1. Fork the repo
2. Make changes
3. Submit a pull request

Help is always welcome!

---

## 🙋 FAQ

**Q: Will this work with Forge or Quilt?**  
🧪 Not yet. Right now only Fabric is supported, but multi-loader support is planned.

**Q: Will it delete my mods?**  
❌ No. It only backs up and moves files — nothing is permanently deleted.

**Q: Can I use this on a modpack?**  
✅ Yes, as long as it's using Fabric and Modrinth-hosted mods.

---

🎉 Happy modding!
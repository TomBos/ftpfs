# 📁 FTPFS – Minimal FTP Client

FTPFS is a no-bloat FTP client from scratch. Designed for just sending files. Nothing else.

# 🚀 Motivation
### Most FTP extensions suck:

- ❌ Can’t send timestamps correctly  
- ❌ Come bundled with features nobody asked for  
- ❌ Bloated GUIs or heavy dependencies  

### ✅ All I need is:

- 🧠 A background process that can connect to FTP servers when needed
- 🔄 Sync files automatically to remote
- 🧾 A config file to control behavior
- 📦 Installation that doesn’t make me cry
- 📥 (If I ever want to download files? I’ll use FileZilla.)

✅ **Features** (as of 09.06.2025)

- 📡 Supports multiple remote servers  
- 🛠️ Configurable via YAML:  
  &nbsp;&nbsp;&nbsp;&nbsp;File: `$HOME/.config/FTPFS/config.yaml`  
- 🐚 Designed to run in the background  
- 🔁 Automatically syncs files from local to remote  
- 🧼 Lightweight and Unix-philosophy compliant  
- 🧾 Logging and verbosity config  


# 📦 **Installation**

You can install FTPFS using the following script:

```bash
bash <(curl -sL "https://raw.githubusercontent.com/TomBos/FTPFS/master/install.sh")
```

### 📦 **Dependencies:**

- **Installation:**
  - `git`
  - `bash`

- **Runtime:**
  - `python`
  - `python-pyinotify`
  - `python-yaml`

> 💡 Make sure these are installed — the script assumes you have them!  
> Don’t hesitate to open an issue if you’re not sure how to install them on your system.


```bash
# Arch installation
sudo pacman -S git bash python python-pyinotify python-yaml
```




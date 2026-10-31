# ⚡ FileConverterPro

<p align="center">
  <strong>Universal Offline File Converter & Resizer for Windows</strong><br>
  Convert PDF, JPG, PNG, WEBP, BMP, TIFF, GIF, and ICO seamlessly — 100% offline, zero internet needed.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/Status-Standalone%20EXE-success" alt="Status" />
  <img src="https://img.shields.io/badge/Network-100%25%20Offline-blueviolet" alt="Offline" />
</p>

---

## 🌟 Highlights

- 🔒 **100% Offline & Private:** Your documents and photos never leave your machine. No telemetry, no cloud APIs.
- 📦 **Single Standalone EXE:** Portable executable bundled with all dependencies (~38.5 MB). No Python or installation required.
- 🔄 **Bidirectional Conversions:** Convert PDF ↔ JPG ↔ PNG ↔ BMP ↔ TIFF ↔ WEBP ↔ GIF ↔ ICO in any direction.
- 📐 **Smart Resizer:** 20+ presets (HD, 4K, Instagram, Passport, A4 print), custom dimensions, or percentage scaling.
- 📄 **PDF Power Tools:** Merge multiple PDFs, compress large PDF files, and extract custom page ranges.
- 🗂️ **Batch Processing:** Convert entire folders of files in a single click.
- 🪟 **Deep Windows Integration:**
  - **Right-Click Context Menu:** Convert directly from Windows Explorer.
  - **Drag & Drop:** Drop files onto the application to process them immediately.
  - **Headless CLI:** Scriptable from PowerShell, CMD, or third-party Windows software.

---

## 🚀 Quick Start

### Option 1: Run the Standalone EXE (No Python Needed)
1. Download `FileConverterPro.exe` from the [Releases](https://github.com/your-username/FileConverterPro/releases) page or locate it in `dist/FileConverterPro.exe`.
2. Double-click to launch!

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/your-username/FileConverterPro.git
cd FileConverterPro

# Install dependencies
pip install -r requirements.txt

# Launch the app
python converter.py
```

---

## 🖼️ Supported Formats & Capabilities

| Source \ Target | JPG | PNG | WEBP | BMP | TIFF | GIF | ICO | PDF |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PDF** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | *(Compress / Extract)* |
| **JPG** | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PNG** | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **WEBP**| ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ |
| **BMP** | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| **TIFF**| ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ |
| **GIF** | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| **ICO** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ |

---

## 🪟 Windows Explorer Right-Click Menu

Right-click any image or PDF in Windows Explorer and select **"Convert / Resize with FileConverterPro"**:

- **From the GUI:** Click the **`📌 Add Right-Click Menu`** button in the header.
- **Via Batch File:** Double-click [`Install_ContextMenu.bat`](Install_ContextMenu.bat).
- **Via Command Line:**
  ```powershell
  FileConverterPro.exe --register-menu
  ```
- **To Remove:** Run `Uninstall_ContextMenu.bat` or `FileConverterPro.exe --unregister-menu`.

*(Note: Registers under `HKEY_CURRENT_USER` — **No Administrator privileges required!**)*

---

## 💻 Command Line (CLI) Usage

Use `FileConverterPro.exe` inside PowerShell, CMD, or automation scripts:

```powershell
# Convert PDF pages to JPGs
FileConverterPro.exe "document.pdf" -f jpg

# Convert images into a single combined PDF
FileConverterPro.exe "receipt1.jpg" "receipt2.png" -f pdf -o "receipts.pdf"

# Convert PNG to WebP with 90% quality
FileConverterPro.exe "hero.png" -f webp -q 90

# Resize image to 1920x1080 (preserves aspect ratio)
FileConverterPro.exe "photo.jpg" --resize 1920x1080

# Scale image by 50%
FileConverterPro.exe "photo.jpg" --scale 50

# Merge multiple PDFs
FileConverterPro.exe --merge "ch1.pdf" "ch2.pdf" -o "full_book.pdf"

# Compress large PDF
FileConverterPro.exe --compress "scanned.pdf" -o "compressed.pdf"

# Extract pages 1 to 5 and page 8 from a PDF
FileConverterPro.exe --extract "document.pdf" --pages 1-5,8 -o "extracted.pdf"
```

For the complete options list, see [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) or run:
```powershell
FileConverterPro.exe --help
```

---

## 🏗️ Building the Standalone EXE

You can recompile the single standalone `.exe` using the included build script:

```bash
# One-click Windows build script
build.bat
```

Or manually with PyInstaller:
```bash
pip install -r requirements.txt
python create_icon.py
pyinstaller --clean FileConverterPro.spec
```
The compiled executable will be placed in `dist/FileConverterPro.exe`.

---

## 📂 Project Structure

```
FileConverterPro/
├── .github/
│   └── workflows/
│       └── build-exe.yml          # GitHub Actions CI for automated builds
├── docs/
│   ├── ARCHITECTURE.md            # Internal architecture and engine design
│   ├── CLI_REFERENCE.md           # Full CLI parameter reference & examples
│   └── WINDOWS_INTEGRATION.md     # Explorer context menu integration guide
├── converter.py                   # Main GUI and CLI application engine
├── create_icon.py                 # Custom ICO generator script
├── FileConverterPro.spec          # PyInstaller packaging configuration
├── icon.ico                       # Bundled multi-resolution application icon
├── Install_ContextMenu.bat        # 1-click context menu installer
├── Uninstall_ContextMenu.bat      # 1-click context menu uninstaller
├── build.bat                      # 1-click EXE compilation script
├── run.bat                        # Quick Python launch script
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules for build artifacts
├── LICENSE                        # MIT Open Source License
└── README.md                      # Project documentation
```

---



## 📄 License

This project is open source and available under the [MIT License](LICENSE).

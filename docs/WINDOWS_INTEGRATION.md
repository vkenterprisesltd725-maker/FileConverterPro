# 🪟 Windows Explorer Integration Guide

FileConverterPro is built to seamlessly blend into the Windows operating system environment.

---

## 📌 Context Menu Integration

When registered, right-clicking on **any file** in Windows Explorer will display:

```
[⚡ Icon] Convert / Resize with FileConverterPro
```

Clicking this item automatically launches FileConverterPro with your selected file pre-loaded into the conversion and resizing tabs.

---

## 🚀 How to Install Context Menu

### Method 1: Directly from the GUI (Recommended)
1. Launch `FileConverterPro.exe`.
2. In the top-right header, click **`📌 Add Right-Click Menu`**.
3. A confirmation dialog will appear. Done!

### Method 2: One-Click Batch Script
Double-click `Install_ContextMenu.bat` located inside the application folder.

### Method 3: Command Line
Open PowerShell or Command Prompt in the application folder and run:
```powershell
FileConverterPro.exe --register-menu
```

---

## 🗑️ How to Remove Context Menu

### Method 1: From the GUI
1. Launch `FileConverterPro.exe`.
2. Click **`🗑️ Remove Explorer Menu`** in the top-right header.

### Method 2: One-Click Batch Script
Double-click `Uninstall_ContextMenu.bat` located inside the application folder.

### Method 3: Command Line
```powershell
FileConverterPro.exe --unregister-menu
```

---

## 🔒 Security & Permissions

- **No Administrator Rights Required:** The context menu entries are written to:
  ```
  HKEY_CURRENT_USER\Software\Classes\*\shell\FileConverterPro
  ```
- Because it is placed in `HKEY_CURRENT_USER` (HKCU), standard non-admin user accounts can install and remove it cleanly without triggering Windows UAC prompts.
- When uninstalled, all registry keys under `FileConverterPro` are deleted without leaving orphaned entries.

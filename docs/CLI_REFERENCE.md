# 💻 FileConverterPro — CLI Reference Manual

FileConverterPro includes a headless command-line interface that can be called from CMD, PowerShell, Windows Terminal, batch scripts, Python scripts, and third-party software.

---

## 📌 Syntax Overview

```bash
FileConverterPro.exe [FILES...] [OPTIONS]
```

Or when running from source:

```bash
python converter.py [FILES...] [OPTIONS]
```

---

## ⚙️ Options & Flags

| Flag | Long Flag | Description | Default |
|---|---|---|---|
| `-h` | `--help` | Show help message and exit | — |
| `-f` | `--format` | Target format (`jpg`, `png`, `pdf`, `webp`, `bmp`, `tiff`, `gif`, `ico`) | — |
| `-o` | `--output` | Output directory or output filename | Same as input |
| `-q` | `--quality` | Compression quality for JPG / WebP (10–100) | `95` |
| | `--dpi` | DPI resolution when rendering PDF pages to images (72–600) | `200` |
| | `--resize` | Target size formatted as `WIDTHxHEIGHT` (e.g. `1920x1080`) | — |
| | `--preset` | Resize preset name (e.g. `'Full HD'`, `'4K'`, `'Instagram Post'`) | — |
| | `--scale` | Percentage scale (e.g. `50` for 50%, `200` for 200%) | — |
| | `--no-aspect` | Disable aspect ratio preservation when resizing | Maintain aspect |
| | `--merge` | Merge multiple PDF input files into one output PDF | — |
| | `--compress` | Compress a PDF file | — |
| | `--extract` | Extract pages from a PDF file | — |
| | `--pages` | Page range to extract (e.g. `1-5`, `1,3,7-10`) | — |
| | `--register-menu` | Register right-click menu in Windows Explorer | — |
| | `--unregister-menu`| Remove right-click menu from Windows Explorer | — |
| | `--gui` | Force launch interactive GUI | — |

---

## 📖 Practical Examples

### 1. Document & Image Conversions

#### Convert PDF to JPG images (one per page):
```powershell
FileConverterPro.exe "report.pdf" -f jpg
```

#### High-resolution PDF rendering (300 DPI):
```powershell
FileConverterPro.exe "blueprint.pdf" -f png --dpi 300
```

#### Combine multiple photos into a single PDF:
```powershell
FileConverterPro.exe "receipt1.jpg" "receipt2.jpg" "receipt3.png" -f pdf -o "receipts_combined.pdf"
```

#### Convert PNG to WebP with 85% quality:
```powershell
FileConverterPro.exe "banner.png" -f webp -q 85
```

#### Convert Image to Windows Icon (.ico):
```powershell
FileConverterPro.exe "logo.png" -f ico -o "favicon.ico"
```

---

### 2. Image Resizing

#### Resize to exact dimensions (maintaining aspect ratio):
```powershell
FileConverterPro.exe "wallpaper.jpg" --resize 1920x1080
```

#### Stretch to exact dimensions (without maintaining aspect ratio):
```powershell
FileConverterPro.exe "avatar.png" --resize 500x500 --no-aspect
```

#### Scale by percentage:
```powershell
# Halve the resolution (50%)
FileConverterPro.exe "large_photo.jpg" --scale 50

# Double resolution (200%)
FileConverterPro.exe "pixel_art.png" --scale 200
```

#### Use a named preset:
```powershell
FileConverterPro.exe "cover.png" --preset "Facebook Cover"
FileConverterPro.exe "post.jpg" --preset "Instagram Post"
FileConverterPro.exe "thumb.jpg" --preset "YouTube Thumbnail"
```

---

### 3. PDF Manipulation

#### Merge multiple PDF files:
```powershell
FileConverterPro.exe --merge "ch1.pdf" "ch2.pdf" "ch3.pdf" -o "full_book.pdf"
```

#### Compress large PDF:
```powershell
FileConverterPro.exe --compress "raw_scans.pdf" -o "compressed_scans.pdf"
```

#### Extract specific pages:
```powershell
# Extract pages 1 through 4 and page 8
FileConverterPro.exe --extract "contract.pdf" --pages 1-4,8 -o "signed_pages.pdf"
```

---

### 4. Integration & Shell Scripts

#### Batch convert all JPGs in a folder using PowerShell:
```powershell
Get-ChildItem -Filter *.jpg | ForEach-Object {
    & "FileConverterPro.exe" $_.FullName -f webp -q 80
}
```

#### Use from a Python script:
```python
import subprocess

subprocess.run([
    "FileConverterPro.exe",
    "sample.pdf",
    "-f", "png",
    "-o", "output_folder"
], check=True)
```

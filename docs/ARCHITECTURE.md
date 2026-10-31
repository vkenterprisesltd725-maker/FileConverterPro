# 🏛️ Architecture & Internal Design

FileConverterPro is built with an offline-first, modular design that separates the GUI presentation layer, CLI controller, Windows shell integration, and the underlying conversion engine.

---

## 🧩 Architectural Diagram

```
+-------------------------------------------------------------------+
|                           Entry Point                             |
|                   (converter.py / sys.argv)                       |
+---------------------------------+---------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
    [No Flags / Files Only]                     [Action Flags]
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
|  FileConverterApp     |                   |       run_cli()       |
|    (Tkinter GUI)      |                   |    (Headless CLI)     |
+-----------+-----------+                   +-----------+-----------+
            |                                           |
            +---------------------+---------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        ConversionEngine                           |
|                                                                   |
|   +-----------------------+           +-----------------------+   |
|   |    Pillow (PIL)       |           |   PyMuPDF (fitz)      |   |
|   |  - Raster formatting  |           |  - PDF rendering      |   |
|   |  - Resizing/Scaling   |           |  - PDF merge/compress |   |
|   |  - Color modes/Alpha  |           |  - Page extraction    |   |
|   +-----------------------+           +-----------------------+   |
+-------------------------------------------------------------------+
```

---

## 📂 Core Components

### 1. `ConversionEngine`
The static core conversion and manipulation class:
- **`pdf_to_images(pdf_path, ...)`**: Uses PyMuPDF's `fitz.Matrix` zooming algorithm to render vector PDF pages into raster pixmaps at arbitrary DPI, converted to PIL Image objects and saved in the user's selected format.
- **`images_to_pdf(image_paths, ...)`**: Standardizes image color spaces (converts palette/RGBA to RGB with white backgrounds where needed), and serializes them into a multi-page PDF document.
- **`convert_image(input_path, output_format, ...)`**: Handles format transcodings (JPG, PNG, BMP, TIFF, WEBP, GIF, ICO) with automated alpha flattening for formats that lack native transparency support.
- **`resize_image(input_path, output_dir, size, maintain_aspect, ...)`**: Uses high-quality Lanczos antialiasing resampling (`Image.LANCZOS`).
- **`merge_pdfs(pdf_paths, output_path, ...)`**: Combines PDF documents efficiently via PyMuPDF object copying.
- **`compress_pdf(pdf_path, output_path, ...)`**: Rewrites PDF xrefs, deflates streams, and removes orphan unreferenced objects with `garbage=4`.

### 2. `FileConverterApp`
- Modern dark-themed Tkinter/ttk interface with tabbed layout.
- Non-blocking background worker threads for responsive progress updating without UI freezing.
- Real-time progress bars and status indicators.

### 3. Windows Shell Integration
- Uses standard library `winreg` to register context menu handlers under `HKEY_CURRENT_USER\Software\Classes\*\shell`.
- Connects Windows file associations and drag-and-drop file paths directly into the application window.

### 4. Dynamic Console Attachment (`AttachConsole`)
- Compiled with `--noconsole` (`console=False`) to prevent flashing a black command prompt window when launched as a desktop app.
- For CLI usage, dynamically calls the Win32 API `kernel32.AttachConsole(-1)` and rebinds standard streams to `CONOUT$` to print formatted console text when executed inside terminal environments.

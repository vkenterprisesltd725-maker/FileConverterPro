"""
FileConverterPro - Universal Offline File Converter & Resizer
A standalone Windows application for converting between PDF, JPG, PNG, BMP, TIFF, WEBP, GIF, ICO, SVG
and resizing images. Fully offline - no internet required.
"""

import os
import sys
import threading
import argparse
import winreg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from io import BytesIO

# Third-party imports
from PIL import Image, ImageDraw, ImageFont
try:
    import pymupdf as fitz  # PyMuPDF >= 1.24
except ImportError:
    import fitz  # PyMuPDF legacy


# ─────────────────────── Windows Shell Integration ───────────────────────

def is_context_menu_registered():
    """Check if the context menu entry already exists in Windows Registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\*\shell\FileConverterPro"):
            return True
    except Exception:
        return False

def register_context_menu():
    """Add FileConverterPro to Windows Explorer right-click context menu (no admin rights needed)."""
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        key_path = r"Software\Classes\*\shell\FileConverterPro"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "Convert / Resize with FileConverterPro")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f'"{exe_path}",0')
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path + r"\command") as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%1"')
        return True, "FileConverterPro added to Windows Explorer right-click menu!"
    except Exception as e:
        return False, str(e)

def unregister_context_menu():
    """Remove FileConverterPro from Windows Explorer right-click context menu."""
    key_path = r"Software\Classes\*\shell\FileConverterPro"
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path + r"\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
        return True, "FileConverterPro removed from Windows Explorer right-click menu!"
    except Exception as e:
        return False, str(e)


# ─────────────────────── Constants ───────────────────────
APP_TITLE = "FileConverterPro"
APP_VERSION = "1.0.0"

IMAGE_EXTENSIONS = {
    "JPG": [".jpg", ".jpeg"],
    "PNG": [".png"],
    "BMP": [".bmp"],
    "TIFF": [".tiff", ".tif"],
    "WEBP": [".webp"],
    "GIF": [".gif"],
    "ICO": [".ico"],
}

ALL_IMAGE_EXTS = []
for exts in IMAGE_EXTENSIONS.values():
    ALL_IMAGE_EXTS.extend(exts)

SUPPORTED_INPUT = ALL_IMAGE_EXTS + [".pdf"]
OUTPUT_FORMATS = ["JPG", "PNG", "BMP", "TIFF", "WEBP", "GIF", "ICO", "PDF"]

# Preset sizes for quick resize
PRESET_SIZES = {
    "Original": None,
    "HD (1280×720)": (1280, 720),
    "Full HD (1920×1080)": (1920, 1080),
    "2K (2560×1440)": (2560, 1440),
    "4K (3840×2160)": (3840, 2160),
    "Instagram Post (1080×1080)": (1080, 1080),
    "Instagram Story (1080×1920)": (1080, 1920),
    "Facebook Cover (820×312)": (820, 312),
    "Twitter Header (1500×500)": (1500, 500),
    "YouTube Thumbnail (1280×720)": (1280, 720),
    "Icon 16×16": (16, 16),
    "Icon 32×32": (32, 32),
    "Icon 48×48": (48, 48),
    "Icon 64×64": (64, 64),
    "Icon 128×128": (128, 128),
    "Icon 256×256": (256, 256),
    "Passport Photo (600×600)": (600, 600),
    "A4 @ 300dpi (2480×3508)": (2480, 3508),
    "Letter @ 300dpi (2550×3300)": (2550, 3300),
    "Custom": "custom",
}

# Color palette — dark modern theme
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_mid": "#16213e",
    "bg_card": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b81",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0b0",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "border": "#2a2a4a",
    "input_bg": "#1e1e3a",
    "button_bg": "#e94560",
}


# ─────────────────────── Conversion Engine ───────────────────────

class ConversionEngine:
    """Core engine that handles all file conversions and resizing."""

    @staticmethod
    def pdf_to_images(pdf_path: str, output_format: str, output_dir: str,
                      dpi: int = 200, resize: tuple = None,
                      progress_callback=None) -> list:
        """Convert each page of a PDF to an image file."""
        results = []
        doc = fitz.open(pdf_path)
        total = len(doc)
        base_name = Path(pdf_path).stem

        for i, page in enumerate(doc):
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if resize:
                img = img.resize(resize, Image.LANCZOS)

            ext = output_format.lower()
            if ext == "jpg":
                ext = "jpeg"

            out_name = f"{base_name}_page_{i + 1}.{output_format.lower()}"
            out_path = os.path.join(output_dir, out_name)

            save_kwargs = {}
            fmt = "JPEG" if output_format.upper() in ("JPG", "JPEG") else output_format.upper()
            if fmt == "JPEG":
                save_kwargs["quality"] = 95
            elif fmt == "WEBP":
                save_kwargs["quality"] = 90

            if fmt == "ICO":
                size = resize or (256, 256)
                img = img.resize(size, Image.LANCZOS)
                img.save(out_path, format="ICO", sizes=[(img.width, img.height)])
            else:
                img.save(out_path, format=fmt, **save_kwargs)

            results.append(out_path)
            if progress_callback:
                progress_callback(i + 1, total)

        doc.close()
        return results

    @staticmethod
    def images_to_pdf(image_paths: list, output_path: str,
                      resize: tuple = None, progress_callback=None) -> str:
        """Combine one or more images into a single PDF."""
        images = []
        total = len(image_paths)

        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path).convert("RGB")
            if resize:
                img = img.resize(resize, Image.LANCZOS)
            images.append(img)
            if progress_callback:
                progress_callback(i + 1, total)

        if images:
            first = images[0]
            rest = images[1:] if len(images) > 1 else []
            first.save(output_path, format="PDF", save_all=True,
                       append_images=rest, resolution=200)

        return output_path

    @staticmethod
    def convert_image(input_path: str, output_format: str, output_dir: str,
                      resize: tuple = None, quality: int = 95,
                      progress_callback=None) -> str:
        """Convert a single image to another format, optionally resizing."""
        img = Image.open(input_path)

        # Handle transparency for formats that don't support it
        if output_format.upper() in ("JPG", "BMP", "ICO") and img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            img = background
        elif img.mode == "P" and output_format.upper() not in ("GIF",):
            img = img.convert("RGBA")

        if output_format.upper() == "JPG" and img.mode != "RGB":
            img = img.convert("RGB")

        if resize:
            img = img.resize(resize, Image.LANCZOS)

        base_name = Path(input_path).stem
        ext = output_format.lower()
        out_name = f"{base_name}.{ext}"
        out_path = os.path.join(output_dir, out_name)

        save_kwargs = {}
        if output_format.upper() == "JPG":
            save_kwargs = {"format": "JPEG", "quality": quality}
        elif output_format.upper() == "WEBP":
            save_kwargs = {"quality": quality}
        elif output_format.upper() == "PNG":
            save_kwargs = {"format": "PNG"}
        elif output_format.upper() == "TIFF":
            save_kwargs = {"format": "TIFF"}
        elif output_format.upper() == "BMP":
            save_kwargs = {"format": "BMP"}
        elif output_format.upper() == "GIF":
            # Preserve animation if present
            if hasattr(img, "n_frames") and img.n_frames > 1:
                img.save(out_path, format="GIF", save_all=True)
                if progress_callback:
                    progress_callback(1, 1)
                return out_path
            save_kwargs = {"format": "GIF"}
        elif output_format.upper() == "ICO":
            size = resize or (256, 256)
            img = img.resize(size, Image.LANCZOS)
            img.save(out_path, format="ICO", sizes=[(img.width, img.height)])
            if progress_callback:
                progress_callback(1, 1)
            return out_path

        fmt = save_kwargs.pop("format", output_format.upper())
        img.save(out_path, format=fmt, **save_kwargs)

        if progress_callback:
            progress_callback(1, 1)

        return out_path

    @staticmethod
    def resize_image(input_path: str, output_dir: str, size: tuple,
                     maintain_aspect: bool = True, progress_callback=None) -> str:
        """Resize an image to the given dimensions."""
        img = Image.open(input_path)

        if maintain_aspect:
            img.thumbnail(size, Image.LANCZOS)
        else:
            img = img.resize(size, Image.LANCZOS)

        ext = Path(input_path).suffix
        base_name = Path(input_path).stem
        out_name = f"{base_name}_resized{ext}"
        out_path = os.path.join(output_dir, out_name)

        fmt = ext.lstrip(".").upper()
        if fmt in ("JPG", "JPEG"):
            fmt = "JPEG"

        save_kwargs = {}
        if fmt == "JPEG":
            if img.mode != "RGB":
                img = img.convert("RGB")
            save_kwargs["quality"] = 95

        img.save(out_path, format=fmt, **save_kwargs)

        if progress_callback:
            progress_callback(1, 1)
        return out_path

    @staticmethod
    def merge_pdfs(pdf_paths: list, output_path: str, progress_callback=None) -> str:
        """Merge multiple PDFs into one."""
        merged = fitz.open()
        total = len(pdf_paths)

        for i, pdf_path in enumerate(pdf_paths):
            doc = fitz.open(pdf_path)
            merged.insert_pdf(doc)
            doc.close()
            if progress_callback:
                progress_callback(i + 1, total)

        merged.save(output_path)
        merged.close()
        return output_path

    @staticmethod
    def compress_pdf(pdf_path: str, output_path: str, progress_callback=None) -> str:
        """Compress a PDF by re-saving with garbage collection."""
        doc = fitz.open(pdf_path)
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        if progress_callback:
            progress_callback(1, 1)
        return output_path


# ─────────────────────── GUI Application ───────────────────────

class FileConverterApp:
    """Main application with a modern tabbed GUI."""

    def __init__(self, initial_files=None):
        self.root = tk.Tk()
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("960x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=COLORS["bg_dark"])

        # Try to set icon (will work when bundled)
        try:
            if getattr(sys, 'frozen', False):
                base = sys._MEIPASS
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.engine = ConversionEngine()
        self.selected_files = []
        self.output_dir = ""

        self._setup_styles()
        self._build_ui()

        # Handle any files passed via CLI, Drag-and-Drop, or Windows Explorer "Open with"
        if initial_files:
            valid_files = [str(Path(f).resolve()) for f in initial_files if os.path.exists(f)]
            if valid_files:
                self.selected_files = valid_files
                names = [Path(f).name for f in valid_files]
                text_label = f"{len(valid_files)} file(s): {', '.join(names[:5])}" + (f" +{len(names) - 5} more" if len(names) > 5 else "")
                self.convert_file_label.config(text=text_label)
                self.resize_file_label.config(text=text_label)
                self._set_status(f"Loaded {len(valid_files)} file(s) from Windows Explorer", COLORS["success"])

        # Center the window
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        """Configure ttk styles for the dark theme."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # General
        self.style.configure(".", background=COLORS["bg_dark"],
                             foreground=COLORS["text_primary"],
                             fieldbackground=COLORS["input_bg"],
                             bordercolor=COLORS["border"],
                             troughcolor=COLORS["bg_mid"])

        # Notebook (tabs)
        self.style.configure("TNotebook", background=COLORS["bg_dark"],
                             borderwidth=0)
        self.style.configure("TNotebook.Tab",
                             background=COLORS["bg_mid"],
                             foreground=COLORS["text_secondary"],
                             padding=[20, 10],
                             font=("Segoe UI", 11, "bold"))
        self.style.map("TNotebook.Tab",
                       background=[("selected", COLORS["accent"])],
                       foreground=[("selected", COLORS["text_primary"])])

        # Frames
        self.style.configure("Card.TFrame", background=COLORS["bg_card"],
                             relief="flat")
        self.style.configure("Dark.TFrame", background=COLORS["bg_dark"])

        # Labels
        self.style.configure("Title.TLabel",
                             background=COLORS["bg_dark"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 24, "bold"))
        self.style.configure("Subtitle.TLabel",
                             background=COLORS["bg_dark"],
                             foreground=COLORS["text_secondary"],
                             font=("Segoe UI", 11))
        self.style.configure("Card.TLabel",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 10))
        self.style.configure("CardTitle.TLabel",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 12, "bold"))
        self.style.configure("Status.TLabel",
                             background=COLORS["bg_dark"],
                             foreground=COLORS["success"],
                             font=("Segoe UI", 10))

        # Buttons
        self.style.configure("Accent.TButton",
                             background=COLORS["accent"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 11, "bold"),
                             padding=[20, 10],
                             borderwidth=0)
        self.style.map("Accent.TButton",
                       background=[("active", COLORS["accent_hover"]),
                                   ("pressed", COLORS["accent"])])

        self.style.configure("Secondary.TButton",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 10),
                             padding=[15, 8],
                             borderwidth=0)
        self.style.map("Secondary.TButton",
                       background=[("active", COLORS["border"])])

        # Combobox
        self.style.configure("TCombobox",
                             fieldbackground=COLORS["input_bg"],
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             arrowcolor=COLORS["accent"],
                             padding=8)

        # Progress bar
        self.style.configure("Accent.Horizontal.TProgressbar",
                             troughcolor=COLORS["bg_mid"],
                             background=COLORS["accent"],
                             borderwidth=0,
                             thickness=8)

        # Entry
        self.style.configure("TEntry",
                             fieldbackground=COLORS["input_bg"],
                             foreground=COLORS["text_primary"],
                             padding=8)

        # Checkbutton
        self.style.configure("TCheckbutton",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             font=("Segoe UI", 10))

        # Spinbox
        self.style.configure("TSpinbox",
                             fieldbackground=COLORS["input_bg"],
                             foreground=COLORS["text_primary"],
                             arrowcolor=COLORS["accent"],
                             padding=5)

        # LabelFrame
        self.style.configure("Card.TLabelframe",
                             background=COLORS["bg_card"],
                             foreground=COLORS["text_primary"],
                             bordercolor=COLORS["border"])
        self.style.configure("Card.TLabelframe.Label",
                             background=COLORS["bg_card"],
                             foreground=COLORS["accent"],
                             font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        """Build the main UI."""
        # Header
        header = ttk.Frame(self.root, style="Dark.TFrame")
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_frame = ttk.Frame(header, style="Dark.TFrame")
        title_frame.pack(side=tk.LEFT)

        ttk.Label(title_frame, text="⚡ FileConverterPro",
                  style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f"v{APP_VERSION}  •  Offline Universal Converter",
                  style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))

        # Windows Explorer Context Menu button
        self.menu_btn_text = tk.StringVar()
        self._update_menu_btn_text()
        ttk.Button(header, textvariable=self.menu_btn_text,
                   style="Secondary.TButton",
                   command=self._toggle_context_menu).pack(side=tk.RIGHT, pady=(5, 0))

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self._build_converter_tab()
        self._build_resize_tab()
        self._build_pdf_tools_tab()
        self._build_batch_tab()

    def _update_menu_btn_text(self):
        if is_context_menu_registered():
            self.menu_btn_text.set("🗑️ Remove Explorer Menu")
        else:
            self.menu_btn_text.set("📌 Add Right-Click Menu")

    def _toggle_context_menu(self):
        if is_context_menu_registered():
            ok, msg = unregister_context_menu()
            if ok:
                messagebox.showinfo("Windows Explorer Integration", msg)
            else:
                messagebox.showerror("Error", f"Failed to remove context menu: {msg}")
        else:
            ok, msg = register_context_menu()
            if ok:
                messagebox.showinfo("Windows Explorer Integration", msg)
            else:
                messagebox.showerror("Error", f"Failed to add context menu: {msg}")
        self._update_menu_btn_text()

        # Status bar
        status_frame = ttk.Frame(self.root, style="Dark.TFrame")
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready — Select files to get started")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                      style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(status_frame, length=250, mode="determinate",
                                        style="Accent.Horizontal.TProgressbar")
        self.progress.pack(side=tk.RIGHT)

    # ──────── Tab 1: Format Converter ────────

    def _build_converter_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  🔄 Convert Format  ")

        # File selection card
        card1 = ttk.LabelFrame(tab, text="  Input Files  ", style="Card.TLabelframe",
                                padding=15)
        card1.pack(fill=tk.X, padx=15, pady=(15, 8))

        btn_row = ttk.Frame(card1, style="Card.TFrame")
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="📂 Select Files",
                   style="Secondary.TButton",
                   command=self._select_files_convert).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row, text="📁 Select Folder",
                   style="Secondary.TButton",
                   command=self._select_folder_convert).pack(side=tk.LEFT)

        self.convert_file_label = ttk.Label(card1, text="No files selected",
                                            style="Card.TLabel", wraplength=700)
        self.convert_file_label.pack(fill=tk.X, pady=(10, 0))

        # Settings card
        card2 = ttk.LabelFrame(tab, text="  Conversion Settings  ",
                                style="Card.TLabelframe", padding=15)
        card2.pack(fill=tk.X, padx=15, pady=8)

        settings_row = ttk.Frame(card2, style="Card.TFrame")
        settings_row.pack(fill=tk.X)

        ttk.Label(settings_row, text="Output Format:",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.convert_format_var = tk.StringVar(value="PNG")
        fmt_combo = ttk.Combobox(settings_row, textvariable=self.convert_format_var,
                                 values=OUTPUT_FORMATS, state="readonly", width=12)
        fmt_combo.pack(side=tk.LEFT, padx=(0, 30))

        ttk.Label(settings_row, text="Quality:",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.convert_quality_var = tk.IntVar(value=95)
        quality_spin = ttk.Spinbox(settings_row, from_=10, to=100,
                                   textvariable=self.convert_quality_var, width=6)
        quality_spin.pack(side=tk.LEFT, padx=(0, 30))

        ttk.Label(settings_row, text="DPI (PDF):",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.convert_dpi_var = tk.IntVar(value=200)
        dpi_spin = ttk.Spinbox(settings_row, from_=72, to=600,
                                textvariable=self.convert_dpi_var, width=6)
        dpi_spin.pack(side=tk.LEFT)

        # Output directory
        card3 = ttk.LabelFrame(tab, text="  Output Location  ",
                                style="Card.TLabelframe", padding=15)
        card3.pack(fill=tk.X, padx=15, pady=8)

        out_row = ttk.Frame(card3, style="Card.TFrame")
        out_row.pack(fill=tk.X)

        ttk.Button(out_row, text="📁 Choose Output Folder",
                   style="Secondary.TButton",
                   command=self._select_output_dir).pack(side=tk.LEFT, padx=(0, 10))
        self.output_dir_label = ttk.Label(out_row, text="Same as source",
                                          style="Card.TLabel", wraplength=600)
        self.output_dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Convert button
        ttk.Button(tab, text="⚡  CONVERT NOW  ⚡",
                   style="Accent.TButton",
                   command=self._run_conversion).pack(pady=20)

    # ──────── Tab 2: Resize ────────

    def _build_resize_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  📐 Resize  ")

        # File selection
        card1 = ttk.LabelFrame(tab, text="  Input Images  ", style="Card.TLabelframe",
                                padding=15)
        card1.pack(fill=tk.X, padx=15, pady=(15, 8))

        btn_row = ttk.Frame(card1, style="Card.TFrame")
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="📂 Select Images",
                   style="Secondary.TButton",
                   command=self._select_files_resize).pack(side=tk.LEFT)

        self.resize_file_label = ttk.Label(card1, text="No files selected",
                                           style="Card.TLabel", wraplength=700)
        self.resize_file_label.pack(fill=tk.X, pady=(10, 0))

        # Size settings
        card2 = ttk.LabelFrame(tab, text="  Size Settings  ", style="Card.TLabelframe",
                                padding=15)
        card2.pack(fill=tk.X, padx=15, pady=8)

        row1 = ttk.Frame(card2, style="Card.TFrame")
        row1.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row1, text="Preset:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.resize_preset_var = tk.StringVar(value="Original")
        preset_combo = ttk.Combobox(row1, textvariable=self.resize_preset_var,
                                    values=list(PRESET_SIZES.keys()),
                                    state="readonly", width=30)
        preset_combo.pack(side=tk.LEFT)
        preset_combo.bind("<<ComboboxSelected>>", self._on_preset_change)

        row2 = ttk.Frame(card2, style="Card.TFrame")
        row2.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row2, text="Width:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.resize_width_var = tk.StringVar(value="")
        self.width_entry = ttk.Entry(row2, textvariable=self.resize_width_var, width=8)
        self.width_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(row2, text="Height:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.resize_height_var = tk.StringVar(value="")
        self.height_entry = ttk.Entry(row2, textvariable=self.resize_height_var, width=8)
        self.height_entry.pack(side=tk.LEFT, padx=(0, 20))

        self.maintain_aspect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Maintain Aspect Ratio",
                        variable=self.maintain_aspect_var).pack(side=tk.LEFT)

        # Percentage resize
        row3 = ttk.Frame(card2, style="Card.TFrame")
        row3.pack(fill=tk.X)

        ttk.Label(row3, text="Or scale by %:", style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.resize_percent_var = tk.StringVar(value="")
        ttk.Entry(row3, textvariable=self.resize_percent_var, width=8).pack(side=tk.LEFT)
        ttk.Label(row3, text="%", style="Card.TLabel").pack(side=tk.LEFT, padx=(5, 0))

        # Output
        card3 = ttk.LabelFrame(tab, text="  Output Location  ",
                                style="Card.TLabelframe", padding=15)
        card3.pack(fill=tk.X, padx=15, pady=8)

        out_row = ttk.Frame(card3, style="Card.TFrame")
        out_row.pack(fill=tk.X)

        ttk.Button(out_row, text="📁 Choose Output Folder",
                   style="Secondary.TButton",
                   command=self._select_output_dir).pack(side=tk.LEFT, padx=(0, 10))
        self.resize_output_label = ttk.Label(out_row, text="Same as source",
                                             style="Card.TLabel")
        self.resize_output_label.pack(side=tk.LEFT)

        # Resize button
        ttk.Button(tab, text="📐  RESIZE NOW  📐",
                   style="Accent.TButton",
                   command=self._run_resize).pack(pady=20)

    # ──────── Tab 3: PDF Tools ────────

    def _build_pdf_tools_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  📄 PDF Tools  ")

        # Merge PDFs
        card1 = ttk.LabelFrame(tab, text="  Merge PDFs  ", style="Card.TLabelframe",
                                padding=15)
        card1.pack(fill=tk.X, padx=15, pady=(15, 8))

        merge_row = ttk.Frame(card1, style="Card.TFrame")
        merge_row.pack(fill=tk.X)

        ttk.Button(merge_row, text="📂 Select PDFs to Merge",
                   style="Secondary.TButton",
                   command=self._select_pdfs_merge).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(merge_row, text="🔗 Merge",
                   style="Accent.TButton",
                   command=self._run_merge).pack(side=tk.LEFT)

        self.merge_label = ttk.Label(card1, text="No PDFs selected",
                                     style="Card.TLabel", wraplength=700)
        self.merge_label.pack(fill=tk.X, pady=(10, 0))

        # Compress PDF
        card2 = ttk.LabelFrame(tab, text="  Compress PDF  ", style="Card.TLabelframe",
                                padding=15)
        card2.pack(fill=tk.X, padx=15, pady=8)

        compress_row = ttk.Frame(card2, style="Card.TFrame")
        compress_row.pack(fill=tk.X)

        ttk.Button(compress_row, text="📂 Select PDF",
                   style="Secondary.TButton",
                   command=self._select_pdf_compress).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(compress_row, text="🗜️ Compress",
                   style="Accent.TButton",
                   command=self._run_compress).pack(side=tk.LEFT)

        self.compress_label = ttk.Label(card2, text="No PDF selected",
                                        style="Card.TLabel", wraplength=700)
        self.compress_label.pack(fill=tk.X, pady=(10, 0))

        # Extract pages
        card3 = ttk.LabelFrame(tab, text="  Extract Pages  ", style="Card.TLabelframe",
                                padding=15)
        card3.pack(fill=tk.X, padx=15, pady=8)

        extract_row = ttk.Frame(card3, style="Card.TFrame")
        extract_row.pack(fill=tk.X)

        ttk.Button(extract_row, text="📂 Select PDF",
                   style="Secondary.TButton",
                   command=self._select_pdf_extract).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(extract_row, text="Pages (e.g. 1,3,5-8):",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(10, 5))
        self.extract_pages_var = tk.StringVar(value="")
        ttk.Entry(extract_row, textvariable=self.extract_pages_var,
                  width=20).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(extract_row, text="✂️ Extract",
                   style="Accent.TButton",
                   command=self._run_extract).pack(side=tk.LEFT)

        self.extract_label = ttk.Label(card3, text="No PDF selected",
                                       style="Card.TLabel", wraplength=700)
        self.extract_label.pack(fill=tk.X, pady=(10, 0))

    # ──────── Tab 4: Batch Convert ────────

    def _build_batch_tab(self):
        tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(tab, text="  ⚡ Batch Convert  ")

        # Info
        info_card = ttk.LabelFrame(tab, text="  Batch Conversion  ",
                                    style="Card.TLabelframe", padding=15)
        info_card.pack(fill=tk.X, padx=15, pady=(15, 8))

        ttk.Label(info_card,
                  text="Convert all files in a folder to a target format at once.\n"
                       "Supports: JPG, PNG, BMP, TIFF, WEBP, GIF, ICO, PDF",
                  style="Card.TLabel", wraplength=700).pack(fill=tk.X)

        # Source folder
        card1 = ttk.LabelFrame(tab, text="  Source Folder  ", style="Card.TLabelframe",
                                padding=15)
        card1.pack(fill=tk.X, padx=15, pady=8)

        src_row = ttk.Frame(card1, style="Card.TFrame")
        src_row.pack(fill=tk.X)

        ttk.Button(src_row, text="📁 Select Source Folder",
                   style="Secondary.TButton",
                   command=self._select_batch_source).pack(side=tk.LEFT, padx=(0, 10))
        self.batch_source_label = ttk.Label(src_row, text="No folder selected",
                                            style="Card.TLabel")
        self.batch_source_label.pack(side=tk.LEFT)

        # Settings
        card2 = ttk.LabelFrame(tab, text="  Settings  ", style="Card.TLabelframe",
                                padding=15)
        card2.pack(fill=tk.X, padx=15, pady=8)

        sett_row = ttk.Frame(card2, style="Card.TFrame")
        sett_row.pack(fill=tk.X)

        ttk.Label(sett_row, text="Convert to:",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.batch_format_var = tk.StringVar(value="PNG")
        ttk.Combobox(sett_row, textvariable=self.batch_format_var,
                     values=OUTPUT_FORMATS, state="readonly",
                     width=12).pack(side=tk.LEFT, padx=(0, 30))

        ttk.Label(sett_row, text="Quality:",
                  style="Card.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        self.batch_quality_var = tk.IntVar(value=95)
        ttk.Spinbox(sett_row, from_=10, to=100,
                    textvariable=self.batch_quality_var, width=6).pack(side=tk.LEFT)

        # Output
        card3 = ttk.LabelFrame(tab, text="  Output Location  ",
                                style="Card.TLabelframe", padding=15)
        card3.pack(fill=tk.X, padx=15, pady=8)

        out_row = ttk.Frame(card3, style="Card.TFrame")
        out_row.pack(fill=tk.X)

        ttk.Button(out_row, text="📁 Choose Output Folder",
                   style="Secondary.TButton",
                   command=self._select_batch_output).pack(side=tk.LEFT, padx=(0, 10))
        self.batch_output_label = ttk.Label(out_row, text="Same as source",
                                            style="Card.TLabel")
        self.batch_output_label.pack(side=tk.LEFT)

        # Batch button
        ttk.Button(tab, text="⚡  BATCH CONVERT  ⚡",
                   style="Accent.TButton",
                   command=self._run_batch).pack(pady=20)

    # ──────── File Selection Handlers ────────

    def _select_files_convert(self):
        filetypes = [
            ("All Supported", " ".join(f"*{e}" for e in SUPPORTED_INPUT)),
            ("PDF Files", "*.pdf"),
            ("Image Files", " ".join(f"*{e}" for e in ALL_IMAGE_EXTS)),
            ("All Files", "*.*"),
        ]
        files = filedialog.askopenfilenames(title="Select Files to Convert",
                                            filetypes=filetypes)
        if files:
            self.selected_files = list(files)
            names = [Path(f).name for f in files]
            self.convert_file_label.config(
                text=f"{len(files)} file(s): {', '.join(names[:5])}"
                     + (f" +{len(names) - 5} more" if len(names) > 5 else ""))

    def _select_folder_convert(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            files = []
            for f in Path(folder).iterdir():
                if f.suffix.lower() in SUPPORTED_INPUT:
                    files.append(str(f))
            if files:
                self.selected_files = files
                self.convert_file_label.config(
                    text=f"{len(files)} file(s) found in {Path(folder).name}")
            else:
                messagebox.showwarning("No Files", "No supported files found in folder.")

    def _select_files_resize(self):
        filetypes = [
            ("Image Files", " ".join(f"*{e}" for e in ALL_IMAGE_EXTS)),
            ("All Files", "*.*"),
        ]
        files = filedialog.askopenfilenames(title="Select Images to Resize",
                                            filetypes=filetypes)
        if files:
            self.selected_files = list(files)
            names = [Path(f).name for f in files]
            self.resize_file_label.config(
                text=f"{len(files)} file(s): {', '.join(names[:5])}"
                     + (f" +{len(names) - 5} more" if len(names) > 5 else ""))

    def _select_output_dir(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_dir_label.config(text=folder)
            try:
                self.resize_output_label.config(text=folder)
            except Exception:
                pass

    def _select_pdfs_merge(self):
        files = filedialog.askopenfilenames(title="Select PDFs to Merge",
                                            filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.merge_files = list(files)
            names = [Path(f).name for f in files]
            self.merge_label.config(text=f"{len(files)} PDF(s): {', '.join(names[:5])}")

    def _select_pdf_compress(self):
        f = filedialog.askopenfilename(title="Select PDF to Compress",
                                       filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.compress_file = f
            self.compress_label.config(text=Path(f).name)

    def _select_pdf_extract(self):
        f = filedialog.askopenfilename(title="Select PDF",
                                       filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.extract_file = f
            doc = fitz.open(f)
            pages = len(doc)
            doc.close()
            self.extract_label.config(text=f"{Path(f).name} ({pages} pages)")

    def _select_batch_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.batch_source = folder
            self.batch_source_label.config(text=folder)

    def _select_batch_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.batch_output = folder
            self.batch_output_label.config(text=folder)

    # ──────── Preset Handler ────────

    def _on_preset_change(self, event=None):
        preset = self.resize_preset_var.get()
        size = PRESET_SIZES.get(preset)
        if size is None:
            self.resize_width_var.set("")
            self.resize_height_var.set("")
        elif size == "custom":
            pass  # user fills in manually
        else:
            self.resize_width_var.set(str(size[0]))
            self.resize_height_var.set(str(size[1]))

    # ──────── Progress Helper ────────

    def _update_progress(self, current, total):
        pct = int((current / total) * 100)
        self.progress["value"] = pct
        self.status_var.set(f"Processing... {current}/{total} ({pct}%)")
        self.root.update_idletasks()

    def _set_status(self, msg, color=None):
        self.status_var.set(msg)
        if color:
            self.status_label.configure(foreground=color)
        self.root.update_idletasks()

    # ──────── Conversion Runner ────────

    def _run_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files first.")
            return

        out_fmt = self.convert_format_var.get()
        quality = self.convert_quality_var.get()
        dpi = self.convert_dpi_var.get()

        def do_work():
            try:
                self._set_status("Converting...", COLORS["warning"])
                self.progress["value"] = 0
                results = []
                total = len(self.selected_files)

                for idx, fpath in enumerate(self.selected_files):
                    ext = Path(fpath).suffix.lower()
                    out_dir = self.output_dir or str(Path(fpath).parent)

                    if ext == ".pdf" and out_fmt != "PDF":
                        # PDF to image
                        res = self.engine.pdf_to_images(
                            fpath, out_fmt, out_dir, dpi=dpi,
                            progress_callback=lambda c, t: self._update_progress(
                                idx + (c / t), total))
                        results.extend(res)
                    elif ext != ".pdf" and out_fmt == "PDF":
                        # Image to PDF
                        base = Path(fpath).stem
                        out_path = os.path.join(out_dir, f"{base}.pdf")
                        res = self.engine.images_to_pdf([fpath], out_path)
                        results.append(res)
                    elif ext == ".pdf" and out_fmt == "PDF":
                        # PDF to PDF (just copy/compress)
                        base = Path(fpath).stem
                        out_path = os.path.join(out_dir, f"{base}_converted.pdf")
                        res = self.engine.compress_pdf(fpath, out_path)
                        results.append(res)
                    else:
                        # Image to image
                        res = self.engine.convert_image(
                            fpath, out_fmt, out_dir, quality=quality)
                        results.append(res)

                    self._update_progress(idx + 1, total)

                self.progress["value"] = 100
                self._set_status(f"✅ Done! {len(results)} file(s) converted successfully.",
                                 COLORS["success"])
                messagebox.showinfo("Success",
                                    f"Converted {len(results)} file(s) successfully!\n\n"
                                    f"Output: {self.output_dir or 'Source folder'}")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    # ──────── Resize Runner ────────

    def _run_resize(self):
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select images first.")
            return

        # Determine target size
        w_str = self.resize_width_var.get().strip()
        h_str = self.resize_height_var.get().strip()
        pct_str = self.resize_percent_var.get().strip()

        if pct_str:
            use_percent = True
            try:
                pct = float(pct_str) / 100.0
            except ValueError:
                messagebox.showerror("Error", "Invalid percentage value.")
                return
        elif w_str and h_str:
            use_percent = False
            try:
                target_size = (int(w_str), int(h_str))
            except ValueError:
                messagebox.showerror("Error", "Width and Height must be numbers.")
                return
        else:
            messagebox.showwarning("No Size",
                                   "Please select a preset, enter dimensions, or a percentage.")
            return

        maintain = self.maintain_aspect_var.get()

        def do_work():
            try:
                self._set_status("Resizing...", COLORS["warning"])
                self.progress["value"] = 0
                results = []
                total = len(self.selected_files)

                for idx, fpath in enumerate(self.selected_files):
                    out_dir = self.output_dir or str(Path(fpath).parent)

                    if use_percent:
                        img = Image.open(fpath)
                        size = (int(img.width * pct), int(img.height * pct))
                        img.close()
                    else:
                        size = target_size

                    res = self.engine.resize_image(fpath, out_dir, size, maintain)
                    results.append(res)
                    self._update_progress(idx + 1, total)

                self.progress["value"] = 100
                self._set_status(f"✅ Done! {len(results)} image(s) resized.", COLORS["success"])
                messagebox.showinfo("Success",
                                    f"Resized {len(results)} image(s)!\n\n"
                                    f"Output: {self.output_dir or 'Source folder'}")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    # ──────── PDF Tools Runners ────────

    def _run_merge(self):
        if not hasattr(self, 'merge_files') or not self.merge_files:
            messagebox.showwarning("No Files", "Please select PDFs to merge.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Merged PDF", defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")])
        if not out_path:
            return

        def do_work():
            try:
                self._set_status("Merging PDFs...", COLORS["warning"])
                self.engine.merge_pdfs(self.merge_files, out_path,
                                       progress_callback=self._update_progress)
                self.progress["value"] = 100
                self._set_status("✅ PDFs merged successfully!", COLORS["success"])
                messagebox.showinfo("Success", f"Merged PDF saved to:\n{out_path}")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    def _run_compress(self):
        if not hasattr(self, 'compress_file') or not self.compress_file:
            messagebox.showwarning("No File", "Please select a PDF to compress.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Compressed PDF", defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=Path(self.compress_file).stem + "_compressed.pdf")
        if not out_path:
            return

        def do_work():
            try:
                self._set_status("Compressing PDF...", COLORS["warning"])
                self.engine.compress_pdf(self.compress_file, out_path,
                                         progress_callback=self._update_progress)
                # Show size comparison
                orig = os.path.getsize(self.compress_file)
                comp = os.path.getsize(out_path)
                saved = ((orig - comp) / orig) * 100 if orig > 0 else 0

                self.progress["value"] = 100
                self._set_status("✅ PDF compressed successfully!", COLORS["success"])
                messagebox.showinfo("Success",
                                    f"Original: {orig / 1024:.1f} KB\n"
                                    f"Compressed: {comp / 1024:.1f} KB\n"
                                    f"Saved: {saved:.1f}%")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    def _run_extract(self):
        if not hasattr(self, 'extract_file') or not self.extract_file:
            messagebox.showwarning("No File", "Please select a PDF.")
            return

        pages_str = self.extract_pages_var.get().strip()
        if not pages_str:
            messagebox.showwarning("No Pages", "Please enter page numbers to extract.")
            return

        # Parse page ranges
        pages = set()
        try:
            for part in pages_str.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = part.split("-")
                    pages.update(range(int(start), int(end) + 1))
                else:
                    pages.add(int(part))
        except ValueError:
            messagebox.showerror("Error", "Invalid page format. Use: 1,3,5-8")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Extracted Pages", defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=Path(self.extract_file).stem + "_extracted.pdf")
        if not out_path:
            return

        def do_work():
            try:
                self._set_status("Extracting pages...", COLORS["warning"])
                doc = fitz.open(self.extract_file)
                new_doc = fitz.open()

                sorted_pages = sorted(pages)
                for i, page_num in enumerate(sorted_pages):
                    if 1 <= page_num <= len(doc):
                        new_doc.insert_pdf(doc, from_page=page_num - 1,
                                           to_page=page_num - 1)
                    self._update_progress(i + 1, len(sorted_pages))

                new_doc.save(out_path)
                new_doc.close()
                doc.close()

                self.progress["value"] = 100
                self._set_status("✅ Pages extracted!", COLORS["success"])
                messagebox.showinfo("Success",
                                    f"Extracted {len(sorted_pages)} page(s) to:\n{out_path}")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    # ──────── Batch Runner ────────

    def _run_batch(self):
        if not hasattr(self, 'batch_source') or not self.batch_source:
            messagebox.showwarning("No Folder", "Please select a source folder.")
            return

        out_fmt = self.batch_format_var.get()
        quality = self.batch_quality_var.get()
        out_dir = getattr(self, 'batch_output', None) or self.batch_source

        # Gather all supported files
        files = []
        for f in Path(self.batch_source).iterdir():
            if f.suffix.lower() in SUPPORTED_INPUT:
                files.append(str(f))

        if not files:
            messagebox.showwarning("No Files", "No supported files found in folder.")
            return

        def do_work():
            try:
                self._set_status(f"Batch converting {len(files)} files...", COLORS["warning"])
                self.progress["value"] = 0
                results = []

                for idx, fpath in enumerate(files):
                    ext = Path(fpath).suffix.lower()

                    if ext == ".pdf" and out_fmt != "PDF":
                        res = self.engine.pdf_to_images(fpath, out_fmt, out_dir, dpi=200)
                        results.extend(res)
                    elif ext != ".pdf" and out_fmt == "PDF":
                        base = Path(fpath).stem
                        out_path = os.path.join(out_dir, f"{base}.pdf")
                        res = self.engine.images_to_pdf([fpath], out_path)
                        results.append(res)
                    elif ext == ".pdf" and out_fmt == "PDF":
                        base = Path(fpath).stem
                        out_path = os.path.join(out_dir, f"{base}_converted.pdf")
                        res = self.engine.compress_pdf(fpath, out_path)
                        results.append(res)
                    else:
                        res = self.engine.convert_image(fpath, out_fmt, out_dir,
                                                        quality=quality)
                        results.append(res)

                    self._update_progress(idx + 1, len(files))

                self.progress["value"] = 100
                self._set_status(f"✅ Batch complete! {len(results)} file(s) converted.",
                                 COLORS["success"])
                messagebox.showinfo("Success",
                                    f"Batch converted {len(results)} file(s)!\n\n"
                                    f"Output: {out_dir}")
            except Exception as e:
                self._set_status(f"❌ Error: {str(e)}", COLORS["error"])
                messagebox.showerror("Error", str(e))

        threading.Thread(target=do_work, daemon=True).start()

    # ──────── Run ────────

    def run(self):
        self.root.mainloop()


# ─────────────────────── CLI & Headless Runner ───────────────────────

def run_cli(args):
    """Run FileConverterPro in headless/command-line mode."""
    # Attach to parent console if running from terminal on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            if ctypes.windll.kernel32.AttachConsole(-1):
                sys.stdout = open("CONOUT$", "w", encoding="utf-8")
                sys.stderr = open("CONOUT$", "w", encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="FileConverterPro",
        description="FileConverterPro - Universal Offline Converter & Resizer for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  FileConverterPro document.pdf -f jpg
  FileConverterPro photo.png -f webp -q 85
  FileConverterPro page1.jpg page2.png -f pdf -o combined.pdf
  FileConverterPro photo.jpg --resize 1920x1080
  FileConverterPro photo.jpg --scale 50
  FileConverterPro --merge doc1.pdf doc2.pdf -o merged.pdf
  FileConverterPro --compress large.pdf -o small.pdf
  FileConverterPro --extract doc.pdf --pages 1-3,5 -o pages.pdf
  FileConverterPro --register-menu
  FileConverterPro --unregister-menu
"""
    )

    parser.add_argument("files", nargs="*", help="Input file(s) or folder(s)")
    parser.add_argument("-f", "--format", choices=[f.lower() for f in OUTPUT_FORMATS] + OUTPUT_FORMATS,
                        help="Target format to convert to (JPG, PNG, PDF, WEBP, BMP, TIFF, GIF, ICO)")
    parser.add_argument("-o", "--output", help="Output directory or output file path")
    parser.add_argument("-q", "--quality", type=int, default=95, help="Image quality (10-100, default 95)")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for PDF rendering (72-600, default 200)")
    parser.add_argument("--resize", help="Resize to WIDTHxHEIGHT (e.g. 1920x1080, 800x600)")
    parser.add_argument("--preset", help="Resize preset (e.g. 'Full HD', 'HD', '4K', 'Instagram Post')")
    parser.add_argument("--scale", type=float, help="Scale by percentage (e.g. 50 for 50%%)")
    parser.add_argument("--no-aspect", action="store_true", help="Don't preserve aspect ratio when resizing")
    parser.add_argument("--merge", action="store_true", help="Merge multiple PDF files into one output PDF")
    parser.add_argument("--compress", action="store_true", help="Compress PDF file")
    parser.add_argument("--extract", action="store_true", help="Extract pages from PDF")
    parser.add_argument("--pages", help="Pages to extract (e.g. 1,3,5-8)")
    parser.add_argument("--register-menu", action="store_true", help="Add to Windows Explorer right-click menu")
    parser.add_argument("--unregister-menu", action="store_true", help="Remove from Windows Explorer right-click menu")
    parser.add_argument("--gui", action="store_true", help="Open GUI with specified files")

    parsed = parser.parse_args(args)

    if parsed.register_menu:
        ok, msg = register_context_menu()
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
        return 0 if ok else 1

    if parsed.unregister_menu:
        ok, msg = unregister_context_menu()
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
        return 0 if ok else 1

    if parsed.gui or (not parsed.format and not parsed.resize and not parsed.preset and not parsed.scale and not parsed.merge and not parsed.compress and not parsed.extract):
        # Open GUI with initial files
        app = FileConverterApp(initial_files=parsed.files)
        app.run()
        return 0

    if not parsed.files:
        print("[ERROR] No input files specified. Run with -h for help.")
        return 1

    engine = ConversionEngine()

    # Handle Merge
    if parsed.merge:
        if not parsed.output:
            print("[ERROR] Please specify output path with -o or --output (e.g. -o merged.pdf)")
            return 1
        print(f"Merging {len(parsed.files)} PDF(s) into '{parsed.output}'...")
        res = engine.merge_pdfs(parsed.files, parsed.output)
        print(f"[OK] Merged PDF saved: {res}")
        return 0

    # Handle Compress
    if parsed.compress:
        inp = parsed.files[0]
        outp = parsed.output or str(Path(inp).with_stem(Path(inp).stem + "_compressed"))
        print(f"Compressing PDF '{inp}'...")
        res = engine.compress_pdf(inp, outp)
        orig_sz = os.path.getsize(inp)
        new_sz = os.path.getsize(outp)
        saved = ((orig_sz - new_sz) / orig_sz) * 100 if orig_sz > 0 else 0
        print(f"[OK] Compressed PDF saved: {res} (Saved {saved:.1f}%)")
        return 0

    # Handle Extract
    if parsed.extract:
        inp = parsed.files[0]
        if not parsed.pages:
            print("[ERROR] Please specify pages to extract with --pages (e.g. --pages 1-3,5)")
            return 1
        outp = parsed.output or str(Path(inp).with_stem(Path(inp).stem + "_extracted"))
        pages = set()
        for part in parsed.pages.split(","):
            part = part.strip()
            if "-" in part:
                s, e = part.split("-")
                pages.update(range(int(s), int(e) + 1))
            else:
                pages.add(int(part))
        doc = fitz.open(inp)
        new_doc = fitz.open()
        for p in sorted(pages):
            if 1 <= p <= len(doc):
                new_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
        new_doc.save(outp)
        new_doc.close()
        doc.close()
        print(f"[OK] Extracted {len(pages)} page(s) to '{outp}'")
        return 0

    # Handle Resize
    if parsed.resize or parsed.preset or parsed.scale:
        target_size = None
        pct = None
        maintain = not parsed.no_aspect

        if parsed.preset:
            target_size = PRESET_SIZES.get(parsed.preset)
            if not target_size or target_size == "custom":
                for k, v in PRESET_SIZES.items():
                    if parsed.preset.lower() in k.lower() and v and v != "custom":
                        target_size = v
                        break
        elif parsed.resize:
            try:
                w, h = parsed.resize.lower().split("x")
                target_size = (int(w), int(h))
            except ValueError:
                print("[ERROR] Invalid --resize format. Use WIDTHxHEIGHT, e.g. 1920x1080")
                return 1
        elif parsed.scale:
            pct = parsed.scale / 100.0

        for fpath in parsed.files:
            out_dir = parsed.output or str(Path(fpath).parent)
            if pct:
                im = Image.open(fpath)
                sz = (int(im.width * pct), int(im.height * pct))
                im.close()
            else:
                sz = target_size
            res = engine.resize_image(fpath, out_dir, sz, maintain)
            print(f"[OK] Resized: {res}")
        return 0

    # Handle Format Conversion
    if parsed.format:
        fmt = parsed.format.upper()
        out_target = parsed.output

        # If combining multiple images into a single PDF
        if fmt == "PDF" and len(parsed.files) > 1 and out_target and out_target.lower().endswith(".pdf"):
            print(f"Combining {len(parsed.files)} image(s) into single PDF '{out_target}'...")
            res = engine.images_to_pdf(parsed.files, out_target)
            print(f"[OK] Combined PDF saved: {res}")
            return 0

        for fpath in parsed.files:
            ext = Path(fpath).suffix.lower()
            out_dir = out_target if (out_target and os.path.isdir(out_target)) else (str(Path(fpath).parent) if not out_target else out_target)
            if ext == ".pdf" and fmt != "PDF":
                results = engine.pdf_to_images(fpath, fmt, out_dir, dpi=parsed.dpi)
                for r in results:
                    print(f"[OK] Converted: {r}")
            elif ext != ".pdf" and fmt == "PDF":
                if out_target and out_target.lower().endswith(".pdf"):
                    out_pdf = out_target
                else:
                    out_pdf = os.path.join(out_dir, f"{Path(fpath).stem}.pdf")
                res = engine.images_to_pdf([fpath], out_pdf)
                print(f"[OK] Converted: {res}")
            else:
                res = engine.convert_image(fpath, fmt, out_dir, quality=parsed.quality)
                print(f"[OK] Converted: {res}")
        return 0

    return 0


# ─────────────────────── Entry Point ───────────────────────

def main():
    if len(sys.argv) == 1:
        app = FileConverterApp()
        app.run()
        return

    raw_args = sys.argv[1:]
    # Handle callers that pass entire argument string as a single argv element
    if len(raw_args) == 1 and (" -" in raw_args[0] or " --" in raw_args[0]):
        import shlex
        raw_args = shlex.split(raw_args[0])

    # Check if flags were passed
    flags = [arg for arg in raw_args if arg.startswith("-")]
    if not flags:
        # User passed file paths only (e.g. Drag and Drop or Windows Explorer "Open With")
        app = FileConverterApp(initial_files=raw_args)
        app.run()
        return

    # Run CLI
    sys.exit(run_cli(raw_args))


if __name__ == "__main__":
    main()

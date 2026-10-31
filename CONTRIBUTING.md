# Contributing to FileConverterPro

Thank you for your interest in contributing to **FileConverterPro**! We welcome all contributions from bug fixes to new format supports and UI improvements.

---

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/FileConverterPro.git
   cd FileConverterPro
   ```

2. **Create a Python virtual environment (Recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python converter.py
   ```

---

## 🧪 Testing Your Changes

### 1. Test GUI Mode
```bash
python converter.py
```

### 2. Test CLI Mode
```bash
# Convert image to PDF
python converter.py test.png -f pdf

# Convert PDF to JPG
python converter.py test.pdf -f jpg

# Resize image
python converter.py test.jpg --resize 800x600
```

### 3. Build & Test Standalone EXE
```bash
pyinstaller --clean FileConverterPro.spec
dist\FileConverterPro.exe --help
```

---

## 📋 Pull Request Guidelines

1. **Branch Naming**: Use clear branch names such as `feature/add-webp-lossless` or `fix/aspect-ratio-bug`.
2. **Offline-First**: FileConverterPro must **never** make external network calls. All conversions and dependencies must remain 100% offline.
3. **Commit Messages**: Write clear, descriptive commit messages.
4. **Code Style**: Follow PEP 8 guidelines.

---

## 🐞 Reporting Bugs

Please open an issue on GitHub with:
- Operating system version (e.g., Windows 10 / Windows 11)
- Input file format and size
- Steps to reproduce
- Error traceback or screenshot

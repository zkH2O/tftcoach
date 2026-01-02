# TFT Coach - Setup Notes

## Missing Dependencies

During file organization, the following dependencies were identified as missing from the codebase:

### 1. `settings.py` module
- **Used by:** `vision/ocr_engine.py`
- **Purpose:** Contains configuration for Tesseract OCR path
- **Action needed:** Create a `settings.py` file in the root directory

Example `settings.py`:
```python
"""
Global settings and configuration
"""

# Tesseract OCR Configuration
# Update this path to match your Tesseract installation
TESSERACT_TESSDATA_PATH = r"C:\Program Files\Tesseract-OCR\tessdata"  # Windows
# TESSERACT_TESSDATA_PATH = "/usr/share/tesseract-ocr/4.00/tessdata"  # Linux
# TESSERACT_TESSDATA_PATH = "/opt/homebrew/share/tessdata"  # macOS (Homebrew)
```

### 2. `mk_functions` module
- **Used by:** `vision/arena_functions.py` (lines 138, 146)
- **Purpose:** Mouse/keyboard control functions (move_mouse)
- **Action needed:** Create or import this module

Likely contains functions like:
```python
def move_mouse(coords: tuple):
    """Move mouse to screen coordinates"""
    # Implementation using pyautogui or similar
    pass
```

## Directory Structure (Current)

```
/TFT-Coach
├── /assets        # Scraped Unit Icons (empty - ready for CDragon assets)
├── /data          # Game data and ML pipeline
│   ├── __init__.py
│   ├── comps.py
│   ├── game_assets.py
│   ├── tft_data_scraper.py
│   ├── update_game_assets.py
│   └── README.md
├── /vision        # Screen capture and OCR
│   ├── __init__.py
│   ├── arena_functions.py
│   ├── ocr_engine.py
│   ├── screen_coords.py
│   ├── vec2.py
│   └── vec4.py
├── /brain         # AI logic (empty - for strategist_rag.py)
├── /ui            # PyQt6 overlay (empty)
├── /mds           # Documentation
│   ├── overview.md
│   └── steps.md
├── requirements.txt
├── SETUP_NOTES.md
└── .gitignore
```

## Installation Steps

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location
3. Update `settings.py` with the tessdata path

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

### 3. Create Missing Configuration Files

Create `settings.py` in the root directory (see template above).

### 4. Get Current TFT Data

```bash
# Run the data scraper
python data/tft_data_scraper.py

# Update game assets with current set
python data/update_game_assets.py
```

See `data/README.md` for detailed instructions on the data pipeline.

## Import Path Notes

The file structure has been reorganized into packages. Imports now use relative paths:

**Within `vision/` package:**
```python
from .vec4 import Vec4
from . import screen_coords
from . import ocr_engine as ocr
```

**From other packages:**
```python
from data import game_assets
from vision import arena_functions
```

## Next Steps

1. Create `settings.py` with Tesseract configuration
2. Create or locate `mk_functions.py` for mouse/keyboard control
3. Run the data scraper to get current TFT set data
4. Begin implementing the AI brain module (`brain/strategist_rag.py`)
5. Build the PyQt6 overlay UI

## Development Notes

- The original code was extracted from another repository
- Some files reference outdated TFT Set 13 data
- The data pipeline will fetch current set information
- Arena functions may need the Riot Client API running (https://127.0.0.1:2999)

## Testing Connectivity

Test if TFT is running and API is accessible:
```bash
curl -k https://127.0.0.1:2999/liveclientdata/allgamedata
```

This endpoint is used by `arena_functions.py` to get player level and health.

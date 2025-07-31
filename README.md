# Sofifa Scraper fc25 merger(FC25 Modding Support)

This is a Python-based tool designed to assist modders of EA Sports FC25 (formerly FIFA) by automating the process of merging player data scraped from [Sofifa.com](https://sofifa.com). The merged data can help in generating `compdata`, custom league structures, or managing squad/player IDs.

## Features

- Supports merging `.xlsx`, `.json`, and `.txt` files based on player `ID`
- Global preview of merged data (first 5 rows)
- Export to `.xlsx`, `.json`, and `.txt` formats
- Python GUI (`.pyw`) with:
  - Dark mode toggle
  - Output directory selector
  - Progress bar and status log
  - Start & Reset buttons
  - Info popup and helper guide
- Lightweight (single `.pyw` file, no database needed)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/nadhilm12/sofifa-scraper-fc25-merger.git
cd sofifa-scraper-fc25-merger

```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Run the GUI:

```bash
python Script_3.pyw
```

## Notes

- Make sure you already scraped player data using the Sofifa Scraper Tool (Script_1 & Script_2).
- Files should have the same structure and contain the ID column.
- This tool is for educational and personal modding use only.

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

---

**Created by:** [nadhilm12](https://github.com/nadhilm12)  
**Year:** 2025  
**Inspired by:** Paulv2k4, eshortX, Decoruiz
**Open-source | FC25 Modding Utility**

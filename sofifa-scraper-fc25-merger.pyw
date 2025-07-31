# =========================================================================
# sofifa-scraper-fc25-merger.pyw
#
# DESCRIPTION:
# This script provides a graphical interface (GUI) for merging two player data files
# (in .xlsx, .json, or .txt formats) generated from Sofifa scraping process.
# The script will merge data based on the "ID" column and save it back
# in the same three file formats.
#
# FEATURES:
# - Clean and modern user interface using `ttkbootstrap`.
# - Merges data from `Script_1` and `Script_2` based on player `ID`.
# - Saves merged results in .xlsx, .json, and .txt formats.
# - Supports light/dark theme and has help functionality.
# =========================================================================

# =========================================================================
# SECTION 1: LIBRARY IMPORTS
# Importing all required modules for script functionality.
# =========================================================================
import os
import threading
from datetime import datetime
from tkinter import filedialog, messagebox, Text, Toplevel
from typing import List, Dict

import pandas as pd # Library for data manipulation and analysis (DataFrame)
import ttkbootstrap as tb # Main module for modern GUI
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap as ttk

# =========================================================================
# SECTION 2: GLOBAL CONFIGURATION
# Definition of global variables used throughout the application.
# =========================================================================
# Dictionary to store application configuration, such as output folder and theme.
config = {"output_folder": "", "theme": "superhero"}

# =========================================================================
# SECTION 3: DATA MANAGER CLASS
# Class to manage data reading, merging, and saving processes.
# =========================================================================
class DataManager:
    """
    Manages data operations including reading files, merging DataFrames,
    and saving results.
    """
    MAX_FILES = 2
    REQUIRED_COL = "ID"

    def __init__(self):
        """Initialize DataManager object."""
        self.dfs: List[pd.DataFrame] = [] # List to store DataFrames
        self.paths: List[str] = [] # List to store file paths
        self.team_name: str = "" # Team name extracted from filename

    @staticmethod
    def read(path: str) -> pd.DataFrame:
        """
        Reads data file from given path, supports .xlsx, .json, .txt formats.
        
        Args:
            path: Full path to data file.
        
        Returns:
            pd.DataFrame: DataFrame containing data from file.
        
        Raises:
            FileNotFoundError: If file not found.
            ValueError: If file format not supported or error while reading.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".xlsx":
                return pd.read_excel(path)
            elif ext == ".json":
                return pd.read_json(path, orient="records", encoding='utf-8')
            elif ext == ".txt":
                # Special handling for .txt format
                with open(path, encoding="utf-8") as f:
                    header = f.readline().strip()
                    cols = [c.strip() for c in header.split("|")]
                return pd.read_csv(path, sep="|", skiprows=[0], names=cols, encoding="utf-8")
            else:
                raise ValueError(f"Format '{ext}' not supported.")
        except pd.errors.EmptyDataError:
            raise ValueError("File empty or unreadable.")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    def merge_all(self) -> pd.DataFrame:
        """
        Merges all added DataFrames based on ID column.
        
        Returns:
            pd.DataFrame: Merged DataFrame.
        
        Raises:
            ValueError: If no files selected for merging.
        """
        if not self.dfs:
            raise ValueError("No files to merge.")
        merged = self.dfs[0]
        for df in self.dfs[1:]:
            merged = merged.merge(df, on=self.REQUIRED_COL, how="left")
        return merged

    def save(self, folder: str):
        """
        Saves merged DataFrame to specified folder
        in .xlsx, .json, and .txt formats.
        
        Args:
            folder: Path to output folder.
        
        Raises:
            FileNotFoundError: If output folder invalid.
        """
        if not os.path.isdir(folder):
            raise FileNotFoundError("Invalid output folder.")
        merged = self.merge_all()
        date_str = datetime.now().strftime("%Y%m%d")
        base = os.path.join(folder, f"Data_{self.team_name}_{date_str}")
        merged.to_excel(f"{base}.xlsx", index=False)
        merged.to_json(f"{base}.json", orient="records", indent=2, force_ascii=False, encoding='utf-8')
        # Write data to .txt file with | separator
        with open(f"{base}.txt", "w", encoding="utf-8") as f:
            f.write(" | ".join(merged.columns) + "\n")
            for _, row in merged.iterrows():
                f.write(" | ".join(map(str, row.values)) + "\n")

    def add_file(self, path: str):
        """
        Adds file to merge process.
        
        Args:
            path: Full path to file to be added.
        
        Raises:
            KeyError: If file doesn't have 'ID' column.
        """
        df = self.read(path)
        if self.REQUIRED_COL not in df.columns:
            raise KeyError(f"Column '{self.REQUIRED_COL}' not found.")
        self.dfs.append(df)
        self.paths.append(path)
        if not self.team_name:
            self.team_name = self.extract_team_name(path)

    @staticmethod
    def extract_team_name(path: str) -> str:
        """Extracts team name from input filename."""
        base = os.path.basename(path)
        if base.startswith("SCRIPT_1_"):
            return base.replace("SCRIPT_1_", "").split(".")[0]
        return os.path.splitext(base)[0]

# =========================================================================
# SECTION 4: GUI CLASS
# Class to build and manage graphical user interface.
# =========================================================================
class MergerGUI:
    """
    Main class responsible for building and managing
    the application's graphical interface.
    """
    def __init__(self):
        """Initialize GUI and DataManager object."""
        self.dm = DataManager()
        self.root = tb.Window(themename=config["theme"])
        self.root.title("⚽ Sofifa Merger – Exported Scrap")
        self.root.geometry("1000x850")
        self.root.resizable(False, False)
        self._build_ui()
        self.update_status()

    def _build_ui(self):
        """Build all widgets and interface layout."""
        self.root.configure(bg="#0d0d0d")
        style = self.root.style
        style.theme_use(config["theme"])
        style.configure("TFrame")
        style.configure("Header.TLabel", foreground="#00e5ff", font=("Segoe UI", 18, "bold"))
        style.configure("Card.TLabelframe",foreground="#00e5ff", borderwidth=1, relief="solid")
        style.configure("Card.TLabelframe.Label", foreground="#00e5ff")

        top = tb.Frame(self.root, style="TFrame")
        top.pack(fill=X, padx=10, pady=5)
        tb.Label(top, text="⚽ Sofifa Merger – Exported Scrap", style="Header.TLabel").pack(side=LEFT)
        tb.Button(top, text="🌓", width=3, command=self.toggle_theme, bootstyle="secondary-outline").pack(side=RIGHT, padx=5)
        tb.Button(top, text="❓", width=3, command=self.show_help, bootstyle="info-outline").pack(side=RIGHT)

        main = tb.Frame(self.root, style="TFrame")
        main.pack(fill=BOTH, expand=YES, padx=20, pady=(0, 20))

        self.file_cards = []
        for idx in range(self.dm.MAX_FILES):
            card = self._create_file_card(main, idx)
            card.pack(fill=X, pady=6)
            self.file_cards.append(card)

        out_card = tb.LabelFrame(main, text="📁 Output Destination", padding=10, style="Card.TLabelframe")
        out_card.pack(fill=X, pady=8)
        tb.Button(out_card, text="Choose Folder", command=self.choose_output, bootstyle="info").pack(side=LEFT)
        self.out_lbl = tb.Label(out_card, text="❌ Not selected", foreground="#ffffff")
        self.out_lbl.pack(side=LEFT, padx=10)

        preview_box = tb.LabelFrame(main, text="👁️ Global Preview (5 rows)", padding=10, style="Card.TLabelframe")
        preview_box.pack(fill=BOTH, expand=YES, pady=8)
        self.global_preview = Text(preview_box, height=7, font=("Consolas", 9), bg="#111", fg="#00e5ff", relief="flat")
        self.global_preview.pack(fill=BOTH, expand=YES)

        prog = tb.Frame(main, style="TFrame")
        prog.pack(fill=X, pady=5)
        self.status_lbl = tb.Label(prog, text="Stand-by", foreground="#ffffff")
        self.status_lbl.pack(side=LEFT)
        self.progress = tb.Progressbar(prog, maximum=100, bootstyle="info-striped")
        self.progress.pack(side=RIGHT)

        btn_bar = tb.Frame(main, style="TFrame")
        btn_bar.pack(fill=X, pady=(10, 0))
        self.btn_reset = tb.Button(btn_bar, text="🔄 RESET", command=self.reset_all, bootstyle="warning", width=18)
        self.btn_reset.pack(side=LEFT, padx=(0, 5))
        self.btn_merge = tb.Button(btn_bar, text="🚀 START MERGE", command=self.start_merge, bootstyle="success", width=18, state=DISABLED)
        self.btn_merge.pack(side=RIGHT, expand=YES)

        footer_frame = tb.Frame(self.root)
        footer_frame.pack(side="bottom", fill="x", pady=(10, 5), padx=10)
        footer_label = tb.Label(footer_frame, text="Powered by Python | Open-source | 2025", font=("Segoe UI", 9), foreground="#cccccc")
        footer_label.pack(side="left")
        info_button = tb.Button(footer_frame, text="Info", command=self.show_info, bootstyle="info-outline")
        info_button.pack(side="right")

    def _create_file_card(self, parent, idx):
        """Creates input file selection card widget."""
        card = tb.LabelFrame(parent, text=f"🗂️ SCRIPT_{idx+1}", padding=12, style="Card.TLabelframe")
        lbl = tb.Label(card, text="❌ Not selected", foreground="#ffffff")
        lbl.pack(anchor="w")
        btn = tb.Button(card, text="Choose File", command=lambda i=idx: self.choose_file(i), bootstyle="info")
        btn.pack(anchor="e", pady=4)
        preview = Text(card, height=3, font=("Consolas", 8), bg="#111", fg="#00e5ff", relief="flat")
        preview.pack(fill=X)
        setattr(card, "lbl", lbl)
        setattr(card, "preview", preview)
        return card

    def choose_file(self, idx: int):
        """Opens dialog to select input file."""
        path = filedialog.askopenfilename(title=f"Select SCRIPT_{idx+1}", filetypes=[("Data Files", "*.xlsx *.json *.txt")])
        if not path:
            return
        try:
            self.dm.add_file(path)
            card = self.file_cards[idx]
            card.lbl.config(text=f"✅ {os.path.basename(path)}", foreground="#00ff7f")
            card.preview.delete("1.0", END)
            card.preview.insert(END, self.dm.dfs[idx].head().to_string(index=False))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self.update_status()

    def choose_output(self):
        """Opens dialog to select output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder", initialdir=config["output_folder"])
        if folder:
            config["output_folder"] = folder
            self.update_status()

    def update_status(self):
        """Updates UI status, such as merge button and output folder label."""
        ok = len(self.dm.dfs) >= 2 and config["output_folder"]
        self.btn_merge.config(state=NORMAL if ok else DISABLED)
        self.out_lbl.config(text=f"📂 {config['output_folder']}" if config["output_folder"] else "❌ Not selected")
        if len(self.dm.dfs) >= 2:
            self.preview_merge()

    def preview_merge(self):
        """Displays merge preview in UI."""
        try:
            merged = self.dm.merge_all()
            self.global_preview.delete("1.0", END)
            self.global_preview.insert(END, merged.head().to_string(index=False))
        except Exception as e:
            messagebox.showerror("Preview Error", str(e))

    def start_merge(self):
        """Starts merge process in separate thread to prevent UI freezing."""
        self.progress["value"] = 0
        self.status_lbl.config(text="Starting merge ...")
        threading.Thread(target=self._do_merge, daemon=True).start()

    def _do_merge(self):
        """Main function that performs merge and save operations."""
        try:
            steps = 3
            step = 100 / steps
            self.progress["value"] = 0
            self.status_lbl.config(text="Merging data ...")
            merged = self.dm.merge_all()
            self.progress["value"] += step
            self.status_lbl.config(text="Saving output ...")
            self.dm.save(config["output_folder"])
            self.progress["value"] += step
            self.status_lbl.config(text="Completed ✅")
            messagebox.showinfo("Success", "Files merged and saved successfully!")
        except Exception as e:
            messagebox.showerror("Failed", str(e))
        finally:
            self.progress.stop()
            self.status_lbl.config(text="Ready")

    def reset_all(self):
        """Resets all application status and input files."""
        self.dm.dfs.clear()
        self.dm.paths.clear()
        self.dm.team_name = ""
        for card in self.file_cards:
            card.lbl.config(text="❌ Not selected", foreground="#ffffff")
            card.preview.delete("1.0", END)
        self.global_preview.delete("1.0", END)
        self.out_lbl.config(text="❌ Not selected")
        self.progress["value"] = 0
        self.status_lbl.config(text="Stand-by")
        self.update_status()

    def toggle_theme(self):
        """Switches application theme between 'superhero' and 'flatly'."""
        new_theme = "superhero" if self.root.style.theme_use() == "flatly" else "flatly"
        config["theme"] = new_theme
        self.root.style.theme_use(new_theme)

    def show_info(self):
        """Displays pop-up window with application information."""
        messagebox.showinfo(title="About This Tool", message=("Sofifa Merger – Exported Scrap\n\n- Automates merging exported file of Sofifa Scraper Tool \n- Useful for compdata and custom league work\n- Use responsibly and support open-source projects!\n\nCreated by: nadhilm12\n\nInspired by the work of : Paulv2k4, eshortX and Decoruiz"))

    def show_help(self):
        """Displays help window with usage guide."""
        top = Toplevel(self.root)
        top.title("Help")
        top.geometry("500x400")
        tb.Label(top, text="User Guide", font=("Segoe UI", 14, "bold"), foreground="#00e5ff").pack(pady=10)
        txt = Text(top, wrap="word", padx=10, pady=10, fg="#ffffff", relief="flat")
        txt.pack(fill=BOTH, expand=YES)
        txt.insert(END, "This application merges files (.xlsx / .json / .txt) based on 'ID' column.\n\nSteps:\n1. Select input files (SCRIPT_1 … SCRIPT_N).\n2. Select input files (SCRIPT_2 … SCRIPT_N).\n3. Select output folder.\n4. Press 'START MERGE'.\n\nNotes:\n• Ensure input files have same format (txt/json/xlsx) - choose one.\n• Verify results in Global Preview column.\n")
        txt.config(state=DISABLED)

    def run(self):
        """Starts main GUI application event loop."""
        try:
            self.root.mainloop()
        finally:
            pass

# =========================================================================
# SECTION 5: MAIN EXECUTION BLOCK
# This section runs when script is executed directly.
# =========================================================================
if __name__ == "__main__":
    MergerGUI().run()
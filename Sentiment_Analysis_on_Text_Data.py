import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Matplotlib integration with Tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# File reading dependencies
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    import openpyxl
    from openpyxl.drawing.image import Image as OpenpyxlImage
except ImportError:
    openpyxl = None
    OpenpyxlImage = None

# Ensure NLTK lexicon is present
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)

sia = SentimentIntensityAnalyzer()


class SentimentApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Feedback & Sentiment Analysis Engine")
        self.geometry("1280x830")
        self.minsize(1050, 720)

        # Style Configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        # Data Store & Concurrency Controls
        self.results_df = pd.DataFrame()
        self.is_processing = False

        # Build UI Structure
        self._build_ui()

    def _configure_styles(self):
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.style.configure("Treeview", rowheight=24, font=("Segoe UI", 9))
        self.style.configure("TButton", font=("Segoe UI", 9), padding=5)

    def _build_ui(self):
        # --- TOP CONTROL PANEL ---
        control_frame = ttk.LabelFrame(self, text=" System Controls ", padding=10)
        control_frame.pack(fill="x", padx=12, pady=6)

        self.btn_import = ttk.Button(control_frame, text="📁 Import File (.csv, .txt, .pdf, .docx)", command=self.load_file)
        self.btn_import.pack(side="left", padx=4)

        self.btn_bench = ttk.Button(control_frame, text="🧪 Run Benchmark Dataset", command=self.run_benchmark)
        self.btn_bench.pack(side="left", padx=4)

        self.btn_export = ttk.Button(control_frame, text="💾 Export Report (PDF / CSV / Excel)", command=self.export_report_flow)
        self.btn_export.pack(side="left", padx=4)

        ttk.Separator(control_frame, orient="vertical").pack(side="left", fill="y", padx=10)

        ttk.Label(control_frame, text="Live Input:").pack(side="left", padx=(5, 2))
        self.live_entry = ttk.Entry(control_frame, width=32)
        self.live_entry.pack(side="left", padx=2)
        self.live_entry.bind("<Return>", lambda e: self.analyze_single_text())

        self.btn_analyze = ttk.Button(control_frame, text="Analyze", command=self.analyze_single_text)
        self.btn_analyze.pack(side="left", padx=4)

        # Progress bar for asynchronous tasks
        self.progress = ttk.Progressbar(control_frame, orient="horizontal", mode="indeterminate", length=140)
        self.progress.pack(side="right", padx=5)

        self.status_lbl = ttk.Label(control_frame, text="Ready", font=("Segoe UI", 8, "italic"))
        self.status_lbl.pack(side="right", padx=8)

        # --- KPI SUMMARY CARDS ---
        kpi_frame = ttk.Frame(self, padding=4)
        kpi_frame.pack(fill="x", padx=12, pady=4)

        self.kpi_total = self._create_kpi_card(kpi_frame, "Total Analyzed", "0", "#1e293b")
        self.kpi_pos = self._create_kpi_card(kpi_frame, "Positive", "0 (0.0%)", "#10b981")
        self.kpi_neu = self._create_kpi_card(kpi_frame, "Neutral", "0 (0.0%)", "#f59e0b")
        self.kpi_neg = self._create_kpi_card(kpi_frame, "Negative", "0 (0.0%)", "#ef4444")

        # --- MAIN SPLIT (TABLE & CHARTS) ---
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=12, pady=6)

        # Left Panel: Data Table
        table_frame = ttk.LabelFrame(main_paned, text=" Detailed Results (Top 500 Preview) ", padding=6)
        main_paned.add(table_frame, weight=3)

        cols = ("text", "pos", "neu", "neg", "compound", "sentiment")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("text", text="Feedback Text")
        self.tree.heading("pos", text="Pos")
        self.tree.heading("neu", text="Neu")
        self.tree.heading("neg", text="Neg")
        self.tree.heading("compound", text="Compound")
        self.tree.heading("sentiment", text="Sentiment")

        self.tree.column("text", width=340, anchor="w")
        self.tree.column("pos", width=55, anchor="center")
        self.tree.column("neu", width=55, anchor="center")
        self.tree.column("neg", width=55, anchor="center")
        self.tree.column("compound", width=75, anchor="center")
        self.tree.column("sentiment", width=85, anchor="center")

        v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Right Panel: Visual Analytics
        self.chart_frame = ttk.LabelFrame(main_paned, text=" Visual Analytics ", padding=6)
        main_paned.add(self.chart_frame, weight=2)

        self.fig, (self.ax_pie, self.ax_bar) = plt.subplots(2, 1, figsize=(5.2, 6.4))
        self.fig.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._render_empty_charts()

    def _create_kpi_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="#ffffff", highlightthickness=1, highlightbackground="#cbd5e1", padx=12, pady=8)
        card.pack(side="left", fill="both", expand=True, padx=4)

        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg=color).pack(anchor="w")
        lbl_val = tk.Label(card, text=value, font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a")
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    # --- ASYNC EXECUTION HELPERS ---
    def _set_busy_state(self, is_busy: bool, message: str = ""):
        self.is_processing = is_busy
        self.status_lbl.config(text=message if is_busy else "Ready")
        state = "disabled" if is_busy else "normal"
        self.btn_import.config(state=state)
        self.btn_bench.config(state=state)
        self.btn_export.config(state=state)
        self.btn_analyze.config(state=state)

        if is_busy:
            self.progress.start(10)
        else:
            self.progress.stop()

    def _threaded_process(self, text_list: list):
        def worker():
            try:
                parsed = []
                for t in text_list:
                    s = sia.polarity_scores(t)
                    c = s["compound"]
                    sent = "POSITIVE" if c >= 0.05 else ("NEGATIVE" if c <= -0.05 else "NEUTRAL")
                    parsed.append((t, round(s["pos"], 3), round(s["neu"], 3), round(s["neg"], 3), round(c, 3), sent))

                df = pd.DataFrame(parsed, columns=[
                    "Feedback Text", "Positive Score", "Neutral Score", "Negative Score", "Compound Score", "Sentiment"
                ])

                self.after(0, self._on_process_complete, df)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
                self.after(0, self._set_busy_state, False)

        self._set_busy_state(True, f"Processing {len(text_list):,} entries...")
        threading.Thread(target=worker, daemon=True).start()

    def _on_process_complete(self, df: pd.DataFrame):
        self.results_df = df
        self.update_ui()
        self._set_busy_state(False)

    # --- FILE PARSING & DISPATCH ---
    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All Supported Formats", "*.csv *.txt *.pdf *.docx"),
                ("CSV Files", "*.csv"),
                ("Text Files", "*.txt"),
                ("PDF Documents", "*.pdf"),
                ("Word Documents", "*.docx"),
            ]
        )
        if not file_path:
            return

        # Insert chosen file path into Live Input without triggering processing immediately
        self.live_entry.delete(0, tk.END)
        self.live_entry.insert(0, file_path)
        self.status_lbl.config(text="File loaded. Click 'Analyze' to process.")

    def _process_file_path(self, file_path: str):
        def file_reader_task():
            ext = os.path.splitext(file_path)[1].lower()
            lines = []
            try:
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                    cols = list(df.columns)
                    if "Title_of_Review" in cols and "Base_Review" in cols:
                        lines = (df["Title_of_Review"].fillna("") + ". " + df["Base_Review"].fillna("")).tolist()
                    else:
                        text_col = next((c for c in ["Base_Review", "Title_of_Review", "Review", "review", "text", "Feedback"] if c in cols), None)
                        if not text_col:
                            text_col = cols[1] if len(cols) > 1 and "star" in cols[0].lower() else cols[0]
                        lines = df[text_col].dropna().astype(str).tolist()

                elif ext == ".txt":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [line.strip() for line in f if line.strip()]

                elif ext == ".pdf":
                    if not PdfReader:
                        self.after(0, lambda: messagebox.showerror("Missing Library", "Run: pip install pypdf"))
                        self.after(0, self._set_busy_state, False)
                        return
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        txt = page.extract_text()
                        if txt:
                            lines.extend([l.strip() for l in txt.split("\n") if l.strip()])

                elif ext == ".docx":
                    if not docx:
                        self.after(0, lambda: messagebox.showerror("Missing Library", "Run: pip install python-docx"))
                        self.after(0, self._set_busy_state, False)
                        return
                    doc = docx.Document(file_path)
                    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

                if not lines:
                    self.after(0, lambda: messagebox.showwarning("Warning", "No readable text extracted!"))
                    self.after(0, self._set_busy_state, False)
                    return

                self._threaded_process(lines)

            except Exception as e:
                self.after(0, lambda: messagebox.showerror("File Error", f"Failed to read file:\n{e}"))
                self.after(0, self._set_busy_state, False)

        self._set_busy_state(True, "Reading file...")
        threading.Thread(target=file_reader_task, daemon=True).start()

    def analyze_single_text(self):
        text = self.live_entry.get().strip()
        if not text or self.is_processing:
            return

        cleaned_path = text.strip("'\"")
        # Check if the entered string is an existing file path
        if os.path.isfile(cleaned_path):
            self._process_file_path(cleaned_path)
            return

        # Otherwise, process single text entry
        s = sia.polarity_scores(text)
        c = s["compound"]
        sent = "POSITIVE" if c >= 0.05 else ("NEGATIVE" if c <= -0.05 else "NEUTRAL")

        row = {
            "Feedback Text": text,
            "Positive Score": round(s["pos"], 3),
            "Neutral Score": round(s["neu"], 3),
            "Negative Score": round(s["neg"], 3),
            "Compound Score": round(c, 3),
            "Sentiment": sent,
        }

        self.results_df = pd.concat([pd.DataFrame([row]), self.results_df], ignore_index=True)
        self.live_entry.delete(0, tk.END)
        self.update_ui()

    def run_benchmark(self):
        samples = [
            "The build quality is amazing and battery life exceeded my expectations!",
            "Average product. It works fine, but nothing extraordinary for this price.",
            "Worst customer experience. The item arrived broken and support was unresponsive.",
            "Delivery was super fast and packaging was secure.",
            "The software keeps crashing every time I open the settings menu.",
            "Completely unusable. Crashes on startup Kindle Fire 10.",
            "Best value for money. Would definitely recommend!",
            "Decent app but not the best. Missing basic search functionality.",
            "Scam product. Does not work as advertised.",
            "Outstanding performance and very intuitive interface.",
        ]
        self._threaded_process(samples * 100)

    # --- ADVANCED EXPORT SYSTEM (PDF, CSV, EXCEL WITH CHARTS, IMAGE) ---
    def export_report_flow(self):
        if self.results_df.empty:
            messagebox.showwarning("Warning", "No data available to export!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Sentiment Report",
            defaultextension=".pdf",
            filetypes=[
                ("PDF Analytics Report (*.pdf)", "*.pdf"),
                ("CSV Data File (*.csv)", "*.csv"),
                ("Excel Workbook with Charts (*.xlsx)", "*.xlsx"),
                ("High-Res Chart Image (*.png)", "*.png"),
            ]
        )
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == ".csv":
                self.results_df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Successful", f"Data rows saved successfully to CSV:\n{file_path}")

            elif ext == ".pdf":
                # Save visual dashboard directly as a multi-chart PDF
                self.fig.savefig(file_path, format="pdf", bbox_inches="tight")
                messagebox.showinfo("Export Successful", f"Visual analytics report exported as PDF:\n{file_path}")

            elif ext == ".png":
                # High-res chart PNG
                self.fig.savefig(file_path, dpi=300, bbox_inches="tight")
                messagebox.showinfo("Export Successful", f"High-resolution chart saved as PNG:\n{file_path}")

            elif ext == ".xlsx":
                if openpyxl is None:
                    messagebox.showerror(
                        "Library Missing",
                        "openpyxl is required to embed charts into Excel.\nInstall it using:\npip install openpyxl"
                    )
                    return

                temp_chart_path = os.path.join(os.path.dirname(file_path), "_temp_chart_export.png")
                self.fig.savefig(temp_chart_path, dpi=180, bbox_inches="tight")

                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    self.results_df.to_excel(writer, sheet_name="Sentiment Data", index=False)
                    ws = writer.sheets["Sentiment Data"]
                    img = OpenpyxlImage(temp_chart_path)
                    ws.add_image(img, "H2")

                if os.path.exists(temp_chart_path):
                    os.remove(temp_chart_path)

                messagebox.showinfo("Export Successful", f"Excel workbook with embedded charts saved:\n{file_path}")

            else:
                messagebox.showwarning("Unsupported Format", f"Unknown format '{ext}'. Please save as .pdf, .csv, or .xlsx")

        except Exception as err:
            messagebox.showerror("Export Error", f"Failed to export file:\n{err}")

    # --- UI & CHART UPDATES ---
    def update_ui(self):
        # 1. Update Treeview (Render preview of top 500 rows to avoid Tkinter UI lag on large datasets)
        self.tree.delete(*self.tree.get_children())
        for _, row in self.results_df.head(500).iterrows():
            self.tree.insert("", "end", values=(
                row["Feedback Text"],
                row["Positive Score"],
                row["Neutral Score"],
                row["Negative Score"],
                row["Compound Score"],
                row["Sentiment"]
            ))

        # 2. Update KPI Cards (Calculated on 100% of the dataset)
        total = len(self.results_df)
        counts = self.results_df["Sentiment"].value_counts()
        pos = counts.get("POSITIVE", 0)
        neu = counts.get("NEUTRAL", 0)
        neg = counts.get("NEGATIVE", 0)

        self.kpi_total.config(text=f"{total:,}")
        self.kpi_pos.config(text=f"{pos:,} ({pos/total*100:.1f}%)" if total else "0 (0.0%)")
        self.kpi_neu.config(text=f"{neu:,} ({neu/total*100:.1f}%)" if total else "0 (0.0%)")
        self.kpi_neg.config(text=f"{neg:,} ({neg/total*100:.1f}%)" if total else "0 (0.0%)")

        # 3. Redraw Visual Charts
        self.plot_charts(pos, neu, neg)

    def _render_empty_charts(self):
        self.ax_pie.clear()
        self.ax_bar.clear()

        for ax in (self.ax_pie, self.ax_bar):
            ax.set_facecolor("#ffffff")

        self.ax_pie.text(0, 0, "No Data Loaded", ha="center", va="center", color="#94a3b8", fontsize=10, fontweight="bold")
        self.ax_pie.set_title("Sentiment Category Breakdown", fontsize=10, fontweight="bold", pad=12, color="#0f172a")

        self.ax_bar.set_title("Compound Score Distribution & Density", fontsize=10, fontweight="bold", pad=12, color="#0f172a")
        self.ax_bar.set_xlim(-1.05, 1.05)
        self.ax_bar.grid(True, linestyle=":", alpha=0.5, color="#cbd5e1")

        self.fig.tight_layout(pad=2.2)
        self.canvas.draw()

    def plot_charts(self, pos, neu, neg):
        self.ax_pie.clear()
        self.ax_bar.clear()

        self.ax_pie.set_facecolor("#ffffff")
        self.ax_bar.set_facecolor("#ffffff")

        total = pos + neu + neg
        categories = ["Positive", "Neutral", "Negative"]
        raw_vals = [pos, neu, neg]
        palette = {"Positive": "#10b981", "Neutral": "#f59e0b", "Negative": "#ef4444"}

        # Filter categories with data
        data_items = [(cat, val, palette[cat]) for cat, val in zip(categories, raw_vals) if val > 0]

        # --- 1. DONUT CHART ---
        if data_items and total > 0:
            labels, values, colors = zip(*data_items)
            explode = [0.02] * len(values) if len(values) > 1 else [0.0]

            def smart_autopct(pct):
                return f"{pct:.1f}%" if pct >= 5.0 else ""

            wedges, texts, autotexts = self.ax_pie.pie(
                values,
                colors=colors,
                explode=explode,
                autopct=smart_autopct,
                pctdistance=0.72,
                startangle=140,
                wedgeprops=dict(width=0.38, edgecolor="#ffffff", linewidth=2.0),
            )

            for autotext in autotexts:
                autotext.set_color("#ffffff")
                autotext.set_fontsize(8.5)
                autotext.set_weight("bold")

            # Center Details Box
            net_ratio = ((pos - neg) / total) * 100
            health_color = "#10b981" if net_ratio > 10 else ("#ef4444" if net_ratio < -10 else "#f59e0b")
            health_txt = f"+{net_ratio:.0f}%" if net_ratio > 0 else f"{net_ratio:.0f}%"

            self.ax_pie.text(0, 0.14, f"{total:,}", ha="center", va="center", fontsize=11, fontweight="bold", color="#0f172a")
            self.ax_pie.text(0, -0.02, "Total Reviews", ha="center", va="center", fontsize=7.5, color="#64748b")
            self.ax_pie.text(
                0, -0.22, f"Net: {health_txt}", ha="center", va="center",
                fontsize=7.5, fontweight="bold", color=health_color,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=0.8)
            )

            # Bottom Legend
            legend_labels = [f"{label}: {val:,} ({val/total*100:.1f}%)" for label, val in zip(labels, values)]
            self.ax_pie.legend(
                wedges, legend_labels, loc="lower center", bbox_to_anchor=(0.5, -0.16),
                ncol=3, fontsize=7.5, frameon=False, handlelength=1.0, handletextpad=0.4
            )
            self.ax_pie.set_title("Sentiment Category Breakdown", fontsize=10, fontweight="bold", pad=12, color="#0f172a")

        # --- 2. MULTI-ZONE COMPOUND DISTRIBUTION HISTOGRAM ---
        if not self.results_df.empty:
            scores = self.results_df["Compound Score"]
            mean_score = scores.mean()

            # Soft background category bands
            self.ax_bar.axvspan(-1.05, -0.05, facecolor="#fee2e2", alpha=0.35, zorder=1)
            self.ax_bar.axvspan(-0.05, 0.05, facecolor="#fef3c7", alpha=0.45, zorder=1)
            self.ax_bar.axvspan(0.05, 1.05, facecolor="#dcfce7", alpha=0.35, zorder=1)

            n, bins, patches = self.ax_bar.hist(
                scores,
                bins=15,
                range=(-1.0, 1.0),
                edgecolor="#ffffff",
                linewidth=1.2,
                alpha=0.92,
                zorder=3
            )

            for patch, bin_left in zip(patches, bins[:-1]):
                if bin_left < -0.05:
                    patch.set_facecolor("#ef4444")
                elif bin_left >= 0.05:
                    patch.set_facecolor("#10b981")
                else:
                    patch.set_facecolor("#f59e0b")

            # Value badges above active bars
            max_freq = max(n) if len(n) > 0 and max(n) > 0 else 1
            for count, patch in zip(n, patches):
                if count > 0:
                    x = patch.get_x() + patch.get_width() / 2
                    y = patch.get_height()
                    self.ax_bar.annotate(
                        f"{int(count):,}" if count >= 1000 else f"{int(count)}",
                        (x, y),
                        textcoords="offset points",
                        xytext=(0, 3),
                        ha="center",
                        va="bottom",
                        fontsize=6.5,
                        fontweight="bold",
                        color="#334155",
                        zorder=4
                    )

            # Mean Reference Line
            self.ax_bar.axvline(
                mean_score,
                color="#0f172a",
                linestyle="--",
                linewidth=1.5,
                zorder=5,
                label=f"Avg Score: {mean_score:.2f}"
            )

            # Visual Region Badges
            y_watermark = max_freq * 0.90
            self.ax_bar.text(-0.55, y_watermark, "NEGATIVE", ha="center", fontsize=7, fontweight="bold", color="#b91c1c", alpha=0.4, zorder=2)
            self.ax_bar.text(0.0, y_watermark, "NEU", ha="center", fontsize=7, fontweight="bold", color="#b45309", alpha=0.4, zorder=2)
            self.ax_bar.text(0.55, y_watermark, "POSITIVE", ha="center", fontsize=7, fontweight="bold", color="#15803d", alpha=0.4, zorder=2)

            self.ax_bar.set_title("Compound Score Distribution & Density", fontsize=10, fontweight="bold", pad=12, color="#0f172a")
            self.ax_bar.set_xlabel("Compound Polarity Score", fontsize=8, color="#475569")
            self.ax_bar.set_ylabel("Count / Frequency", fontsize=8, color="#475569")
            self.ax_bar.set_xlim(-1.05, 1.05)
            self.ax_bar.set_ylim(0, max_freq * 1.16)
            self.ax_bar.tick_params(labelsize=8, colors="#475569")
            self.ax_bar.grid(True, linestyle=":", alpha=0.5, color="#cbd5e1", axis="y", zorder=1)
            self.ax_bar.legend(loc="upper left", fontsize=7.5, framealpha=0.9)

        self.fig.tight_layout(pad=2.2)
        self.canvas.draw()


if __name__ == "__main__":
    app = SentimentApp()
    app.mainloop()
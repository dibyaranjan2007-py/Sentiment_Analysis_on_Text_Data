# Feedback & Sentiment Analysis on Text Data

A high-performance Python desktop application engineered for Natural Language Processing (NLP) sentiment classification across multi-format documents (.csv, .txt, .pdf, .docx). Built with an asynchronous, multi-threaded Tkinter interface and powered by the NLTK VADER lexicon, it processes massive text corpora with zero UI lag while providing interactive, rich visual analytics and automated multi-format business reporting.

---

## 📌 Key Features

* **Multi-Format Ingestion:** Direct parsing for CSV datasets (with automated review column detection), plain text files (.txt), PDF documents via pypdf, and Word documents via python-docx.
* **Controlled File & Text Dispatch:** Selecting a document populates the file path directly into the inspection field, allowing verification before executing the analysis.
* **Dual Live Input & File Evaluation:** Seamlessly handles individual manual text prompts as well as path-based batch dataset processing from a unified entry point.
* **Non-Blocking Multi-Threading:** Offloads CPU-intensive lexicon parsing to dedicated background daemon workers to keep the desktop UI smooth and responsive.
* **Smart UI Virtualization:** Efficiently handles datasets with 70,000+ entries using an optimized preview rendering system (top 500 records) to prevent memory saturation and GUI freezing.
* **Dynamic Visual Analytics:**
  * **Interactive Donut Breakdown:** Visualizes category distributions with net polarity health metrics and collision-avoidance percentage labeling.
  * **Multi-Zone Compound Density Histogram:** Categorizes compound polarity scores across color-coded frequency zones with mean-score annotations.
* **Enterprise Multi-Format Export Engine:**
  * **PDF Analytics Report (.pdf):** Exports a publication-ready visual dashboard.
  * **Excel Workbook with Embedded Charts (.xlsx):** Bundles tabular sentiment data and high-resolution chart graphics side-by-side using openpyxl.
  * **Structured CSV Data (.csv):** Standard data export with full polarity metadata (pos, neu, neg, compound, sentiment).
  * **High-Resolution Graphics (.png):** 300 DPI visualization snapshots for stakeholder presentations.

---

## 🛠️ Technologies Used

* **Programming Language:** Python 3.10+
* **NLP & Polarity Engine:** NLTK (VADER Lexicon Analyzer)
* **Data Engineering:** Pandas[cite: 7]
* **Data Visualization:** Matplotlib (Embedded via TkAgg canvas backend)[cite: 7]
* **GUI Framework:** Tkinter / TTK[cite: 7]
* **Document & Spreadsheet Parsers:** pypdf, python-docx, openpyxl[cite: 7]

---

## 📋 Setup & Installation Instructions

### 1. Clone the Repository
```bash
git clone [https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data.git](https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data.git)
cd Sentiment_Analysis_on_Text_Data
2. Set Up a Virtual Environment (Recommended)
Bash
# Create environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
3. Install Dependencies
Bash
pip install pandas nltk matplotlib pypdf python-docx openpyxl
4. Launch the Application
Bash
python "Sentiment Analysis on Text Data.py"
📊 Polarity Scoring Logic & Detailed Thresholds
The sentiment classification engine relies on the NLTK VADER (Valence Aware Dictionary and sEntiment Reasoner) model, which computes normalized compound polarity scores ranging from -1.0 (extreme negative) to +1.0 (extreme positive)[cite: 7]. The engine interprets scores through three structured operational zones[cite: 7]:

1. Positive Sentiment Zone
Compound Score Threshold: Greater than or equal to +0.05[cite: 7]

UI Palette Accent: Emerald Green (#10b981)[cite: 7]

Detailed Breakdown: Identifies user responses, product reviews, and customer messages containing favorable, approving, or enthusiastic wording[cite: 7]. The scoring algorithm evaluates lexical intensity, punctuation emphasis, and positive semantic modifiers to score statements where constructive customer satisfaction clearly predominates[cite: 7].

2. Neutral Sentiment Zone
Compound Score Threshold: Between -0.05 and +0.05 (-0.05 < Compound < +0.05)[cite: 7]

UI Palette Accent: Amber Yellow (#f59e0b)[cite: 7]

Detailed Breakdown: Classifies non-polarized text such as objective statements, technical questions, factual reporting, or balanced reviews containing an equal distribution of mild pros and cons[cite: 7]. This category isolates purely informative customer feedback from emotionally charged reviews[cite: 7].

3. Negative Sentiment Zone
Compound Score Threshold: Less than or equal to -0.05[cite: 7]

UI Palette Accent: Crimson Red (#ef4444)[cite: 7]

Detailed Breakdown: Detects complaints, frustration, product defect reports, and negative feedback dominated by critical vocabulary[cite: 7]. The engine flags these items with prioritized visual status bars, enabling teams to spot issues, track escalations, and calculate net brand sentiment ratios[cite: 7].

🔗 Repository Reference
GitHub Repository: https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data

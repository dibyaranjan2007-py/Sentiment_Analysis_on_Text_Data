# Sentiment_Analysis_on_Text_Data
A high-performance Python desktop application engineered for Natural Language Processing (NLP) sentiment classification across multi-format documents (`.csv`, `.txt`, `.pdf`, `.docx`). Built with an asynchronous, multi-threaded Tkinter interface and powered by the NLTK VADER lexicon, it processes massive text corpora with zero UI lag while providing interactive, rich visual analytics.

---

## 📌 Features

* **Multi-Format Ingestion:** Direct parsing for CSV datasets (with automated column detection), raw text files (`.txt`), PDF documents (`pypdf`), and Word documents (`python-docx`).
* **Non-Blocking Multi-Threading:** Offloads CPU-intensive lexicon parsing to dedicated background daemon workers to keep the desktop UI smooth and responsive.
* **Smart UI Virtualization:** Efficiently handles datasets with 70,000+ entries using optimized preview rendering to prevent memory saturation.
* **Dynamic Visual Analytics:**
  * **Interactive Donut Breakdown:** Visualizes category distributions with net polarity health metrics and smart collision-avoidance labeling.
  * **Multi-Zone Compound Density Histogram:** Categorizes compound polarity scores across color-coded frequency zones with mean-score annotations.
* **Real-Time Text Tester:** Live single-sentence evaluation with instant metric updates.
* **Export Engine:** One-click tabular CSV exporting with full polarity metadata (`pos`, `neu`, `neg`, `compound`, `sentiment`).

---

## 🛠️ Technologies Used

* **Language:** Python 3.10+
* **NLP & Scoring:** NLTK (VADER Lexicon Analyzer)
* **Data Handling:** Pandas
* **Data Visualization:** Matplotlib (Embedded via `TkAgg`)
* **GUI Framework:** Tkinter / ttk
* **Document Parsers:** `pypdf`, `python-docx`

---

## 📋 Setup & Installation Instructions

### 1. Clone the Repository
```bash
git clone [https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data.git](https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data.git)
cd Sentiment_Analysis_on_Text_Data
2. Set Up a Virtual Environment (Recommended)
Bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
3. Install Dependencies
Bash
pip install pandas nltk matplotlib pypdf python-docx
4. Launch the Application
Bash
python "Sentiment Analysis on Text Data.py"
📊 Compound Score Thresholds
Positive Sentiment:

Threshold Range: Score≥0.05

UI Zone Color: Emerald (#10b981)

Description: Represents distinctly favorable or optimistic feedback where positive polarity words outweigh negative expressions.

Neutral Sentiment:

Threshold Range: −0.05<Score<0.05

UI Zone Color: Amber (#f59e0b)

Description: Denotes objective statements, factual data, or balanced text where positive and negative sentiments cancel each other out.

Negative Sentiment:

Threshold Range: Score≤−0.05

UI Zone Color: Red (#ef4444)

Description: Indicates critical, dissatisfied, or unfavorable feedback dominated by negative vocabulary.
🔗 Repository LinkGitHub Repository:
 https://github.com/dibyaranjan2007-py/Sentiment_Analysis_on_Text_Data

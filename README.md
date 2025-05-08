# FMEA-Manager

**Lean, mean FMEA machine** – spot, analyze, and fix your process risks before they bite you in the ass.

---

## 🚀 why you need this

* **Instant prioritization**: calculate Risk Priority Number (RPN = G × O × D) in real time and laser-focus on your worst offenders.
* **Zero overhead**: JSON-based storage – human-readable, Git-friendly, zero-config.
* **Audit-ready**: every create/edit/delete/restoration logged in `fmea_log.json`, auto-pruned after 30 days.
* **Lightweight UI**: Flet frontend with dark theme, maximized by default – no corporate bullshit.

## 🔧 features

* **CRUD operations**: add, edit, soft-delete, restore, or permanently remove failure modes.
* **Auto‑RPN**: instant G (gravidade), O (ocorrência), D (detecção) multiplication.
* **3‑month reliability**: optional field → compute system reliability & failure probability.
* **Real‑time histograms**: G, O, D, and RPN charts for at-a-glance decision making.
* **Flexible export**: `.xlsx` (sheet “itens”), `.csv` (semicolon-delimited), `.pdf` (auto-table), or `.png` (table snapshot).

## ⚡️ quickstart

1. **clone** the repo:

   ```bash
   git clone https://github.com/upprgt/FMEA-Manager.git
   cd FMEA-Manager
   ```
2. **install** dependencies:

   ```bash
   pip install flet pandas matplotlib dataframe_image
   ```
3. **run** the app:

   ```bash
   python auto_fmea.py
   ```
4. **enter** your failure modes, eyeball histograms, export your report, and sleep easy.

## 📂 config files

* `fmea_config.json`: your data store (edit by hand or via UI).
* `fmea_log.json`: immutable audit trail of last 30 days of changes.

## 🛣 roadmap

* AI-powered failure-mode suggestions & in-app chat.
* Interactive threshold sliders & color-coded risk levels.
* Optional SQLite fallback for enterprise power users.
* CLI tools: `fmea validate`, `fmea export --high-risk`.

## 📜 license

MIT License – use, modify, and sell. just don’t sue.

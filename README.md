fmea-managerlean. mean. fmea machine.

–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

why the fuck you need this

spot your process’s worst offenders by risk priority number (rpn) in literally 2 seconds

no database bullshit: everything lives in a human‑readable json

portable audit log: every create/edit/delete/restoration stamped in fmea_log.json

lightweight flet ui: drop‑in, dark‑mode, maximized by default, zero config

features

crud: add, edit, soft‑delete, restore, permanently delete entries

auto-rpn: gravidade (g) × ocorrência (o) × detecção (d) calculated on the fly

3-month reliability: optional reliability field → system reliability & failure probability

histograms: instant charts for g, o, d & total rpn for instant prioritization

export: .xlsx, .csv (semicolon), .pdf (table), .png (snapshot)

audit-log pruning: auto‑removes deleted logs older than 30 days

install & run

clone this shit

git clone https://github.com/upprgt/FMEA-Manager.git
cd FMEA-Manager

install dependencies

pip install flet pandas matplotlib dataframe_image

run the app

python auto_fmea.py

profit—enter your failure modes, eyeball the histograms, export reports

config files

fmea_config.json: your entries (human‑editable)

fmea_log.json: audit trail (don’t manually edit unless you’re masochistic)

coming up next

ai‑driven failure‑mode suggestions & chat assistant

interactive threshold sliders & color‑coded bars

sqlite fallback for power users

cli tools: fmea validate, fmea export --high-risk

license

mit. do whatever you want, just don’t sue me.

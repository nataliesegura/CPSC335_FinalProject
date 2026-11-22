# GridRestore

Power restoration planner after a Southern California windstorm

CPSC 335 Algorithm Engineering - Final Project (pairs). All data is simulated for learning.

## Quick start
```
pip install -r requirements.txt
streamlit run app.py          # the app opens in your browser
python check_project.py       # which parts of core.py pass
python main.py --demo         # every part, printed in the terminal
```
On Mac use `pip3` / `python3`. If `streamlit` is "not found", use `python -m streamlit run app.py`.

## What you write
Only **core.py** (the 8 algorithm parts). Every tab of the app shows "Not implemented yet"
until the function it needs works.

| File | What it is | Edit it? |
|---|---|---|
| core.py | The algorithm engine, Parts 1-8 | **Yes, this is your work** |
| app.py | Streamlit app, one tab per part | Optional (improve the look) |
| theme.py | This project's words, priority rule and data mapping | No |
| glue.py | Small helpers that connect the data to core.py | No |
| main.py | Terminal demo | No |
| check_project.py, tests/ | Self-check and public tests | No |
| data/ | Simulated data | No |
| REPORT_TEMPLATE.md | Your report outline | Fill in, export as PDF |

## Suggested split
- Student A: Parts 1, 2, 3, 7  (data and text)
- Student B: Parts 4, 5, 6     (decisions and routes)
- Together: Part 8, the report, deployment and the presentation

Write Part 2 (merge_sort) and Part 3 (MinHeap) early: other parts use them.

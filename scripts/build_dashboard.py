"""Build the self-contained HTML dashboard from the saved report files.

Run after the notebooks (or `python scripts/run_pipeline.py`):

    python scripts/build_dashboard.py

Output: dashboard/smart_basket_dashboard.html. It needs no server and no
internet connection; just open it in a browser.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from smart_basket import config  # noqa: E402


def main() -> Path:
    r = config.REPORTS_DIR
    monthly = pd.read_csv(r / "monthly_kpis.csv")
    cohorts = pd.read_csv(r / "cohort_retention.csv")
    data = {
        "summary": json.loads((r / "metrics_summary.json").read_text()),
        "experiment": json.loads((r / "experiment_results.json").read_text()),
        "monthly": monthly.to_dict(orient="records"),
        "categories": pd.read_csv(r / "category_kpis.csv").to_dict(orient="records"),
        "cohorts": cohorts.to_dict(orient="records"),
        "rules": pd.read_csv(r / "top_affinity_rules.csv").to_dict(orient="records"),
    }
    template = (Path(__file__).resolve().parents[1] / "src" / "smart_basket" / "dashboard_template.html").read_text()
    html = template.replace("/*__DATA__*/", json.dumps(data, default=float))
    config.DASHBOARD_DIR.mkdir(exist_ok=True)
    out = config.DASHBOARD_DIR / "smart_basket_dashboard.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(config.ROOT)} ({len(html) / 1024:.0f} KB)")
    return out


if __name__ == "__main__":
    main()

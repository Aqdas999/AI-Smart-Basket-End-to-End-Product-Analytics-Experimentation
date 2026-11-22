"""Run the whole project end to end:

1. build the analytics tables (data/processed/)
2. execute the three notebooks in order (refreshing their outputs, figures and reports/)
3. build the HTML dashboard

    python scripts/run_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from smart_basket import data_model  # noqa: E402

NOTEBOOKS = ["01_Data_Modeling", "02_Product_Metrics", "03_Smart_Basket_Experiment"]


def main() -> None:
    print("1/3 Building analytics tables...")
    data_model.build_all()

    print("2/3 Executing notebooks...")
    for nb in NOTEBOOKS:
        print(f"    {nb}")
        subprocess.run(
            [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
             "--ExecutePreprocessor.timeout=900", f"{nb}.ipynb"],
            cwd=ROOT / "notebooks",
            check=True,
        )

    print("3/3 Building dashboard...")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_dashboard.py")], check=True)
    print("Done. Open dashboard/smart_basket_dashboard.html in your browser.")


if __name__ == "__main__":
    main()

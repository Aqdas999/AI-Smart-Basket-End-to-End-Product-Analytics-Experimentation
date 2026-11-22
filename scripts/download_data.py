"""Download the Olist dataset from Kaggle into data/raw/.

Needs `pip install kagglehub` and a Kaggle API token
(Kaggle -> Settings -> Create New Token -> save as ~/.kaggle/kaggle.json).
Prefer not to set that up? Download the zip manually instead; see data/README.md.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from smart_basket import config  # noqa: E402

DATASET = "olistbr/brazilian-ecommerce"


def main() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    if all((config.RAW_DIR / f).exists() for f in config.RAW_FILES.values()):
        print(f"All files already in {config.RAW_DIR}. Nothing to do.")
        return
    try:
        import kagglehub
    except ImportError:
        sys.exit("kagglehub is not installed: run `pip install kagglehub`, or download manually (see data/README.md).")

    src = Path(kagglehub.dataset_download(DATASET))
    copied = 0
    for csv in src.rglob("*.csv"):
        shutil.copy2(csv, config.RAW_DIR / csv.name)
        copied += 1
    missing = [f for f in config.RAW_FILES.values() if not (config.RAW_DIR / f).exists()]
    if missing:
        sys.exit(f"Download finished but these files are missing: {missing}")
    print(f"Copied {copied} files to {config.RAW_DIR}")


if __name__ == "__main__":
    main()

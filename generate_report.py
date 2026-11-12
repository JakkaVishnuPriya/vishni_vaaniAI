import pandas as pd
from pathlib import Path

path = Path("results/results.csv")
if not path.exists():
    raise SystemExit("results/results.csv does not exist yet. Run experiments first.")
df = pd.read_csv(path)
print("Rows:", len(df))
print(df.groupby(["scenario", "source"])["total_ms"].agg(["count", "median", lambda s: s.quantile(.95)]))
print("\nDo not use this summary until results.csv contains one row per actual request.")

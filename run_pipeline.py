"""Rebuild every table and figure: `python run_pipeline.py`."""
import json
from pathlib import Path

from src import analysis, data, viz

OUT = Path(__file__).parent / "reports" / "tables"


def main():
    panel = data.load_panel()
    snapshot = analysis.asean_snapshot(panel)
    growth = analysis.asean_growth(panel)
    headline = analysis.vietnam_headline(panel)

    OUT.mkdir(parents=True, exist_ok=True)
    panel.round(3).to_csv(OUT / "asean_panel.csv", index=False)
    snapshot.round(3).to_csv(OUT / "asean_2024_snapshot.csv", index=False)
    growth.round(3).to_csv(OUT / "asean_growth_2000_2024.csv")
    (OUT / "vietnam_headline.json").write_text(json.dumps(headline, indent=2, default=float))

    figures = [viz.vietnam_trend(panel), viz.remittances_vs_fdi(panel), viz.asean_trends(panel),
               viz.asean_2024_ranking(snapshot), viz.remittance_gdp_share(panel),
               viz.remittance_fdi_ratio(panel)]
    print(json.dumps(headline, indent=2, default=float))
    print(snapshot.round(2).to_string(index=False))
    print(growth.round(2).to_string())
    print(*[f"saved {p.name}" for p in figures], sep="\n")


if __name__ == "__main__":
    main()

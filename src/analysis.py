"""Summary statistics used in the Vietnam remittance study."""
import pandas as pd

from .data import END_YEAR, START_YEAR


def vietnam(panel: pd.DataFrame) -> pd.DataFrame:
    return panel[panel["Code"] == "VNM"].set_index("Year")


def cagr(first: float, last: float, years: int) -> float:
    """Compound annual growth rate in percent."""
    return ((last / first) ** (1 / years) - 1) * 100


def vietnam_headline(panel: pd.DataFrame) -> dict:
    """Key numbers behind the three-part thesis."""
    vn = vietnam(panel)
    r, f = vn["Remittances"], vn["FDI"]
    yoy = vn["Remit_YoY_pct"]
    gap = r - f
    return {
        "remit_start": r[START_YEAR],
        "remit_end": r[END_YEAR],
        "multiple": r[END_YEAR] / r[START_YEAR],
        "cagr_pct": cagr(r[START_YEAR], r[END_YEAR], END_YEAR - START_YEAR),
        "decline_years": [int(y) for y in yoy[yoy < 0].index],
        "fdi_end": f[END_YEAR],
        "remit_to_fdi_end": r[END_YEAR] / f[END_YEAR],
        "years_remit_above_fdi": [int(y) for y in gap[gap > 0].index],
        "remit_pct_gdp_start": vn["Remit_pct_GDP"][START_YEAR],
        "remit_pct_gdp_peak": vn["Remit_pct_GDP"].max(),
        "remit_pct_gdp_peak_year": int(vn["Remit_pct_GDP"].idxmax()),
        "remit_pct_gdp_end": vn["Remit_pct_GDP"][END_YEAR],
        "remit_pct_gdp_mean_2015_2024": vn["Remit_pct_GDP"].loc[2015:END_YEAR].mean(),
    }


def asean_snapshot(panel: pd.DataFrame, year: int = END_YEAR) -> pd.DataFrame:
    """Cross-section of ASEAN recipients in `year`, ranked by remittance inflows."""
    snap = panel[panel["Year"] == year].dropna(subset=["Remittances"]).copy()
    snap["Rank"] = snap["Remittances"].rank(ascending=False).astype(int)
    snap["Share_of_ASEAN_pct"] = snap["Remittances"] / snap["Remittances"].sum() * 100
    cols = ["Rank", "Country", "Remittances", "Share_of_ASEAN_pct",
            "Remit_pct_GDP", "FDI", "Remit_to_FDI"]
    return snap.sort_values("Rank")[cols].reset_index(drop=True)


def asean_growth(panel: pd.DataFrame) -> pd.DataFrame:
    """Remittance growth multiple and CAGR for each country, 2000 -> 2024."""
    wide = panel.pivot(index="Country", columns="Year", values="Remittances")
    out = pd.DataFrame({"2000": wide[START_YEAR], "2024": wide[END_YEAR]}).dropna()
    out = out[out["2000"] >= 10]  # skip near-zero bases that give meaningless multiples
    out["Multiple"] = out["2024"] / out["2000"]
    out["CAGR_pct"] = [cagr(a, b, END_YEAR - START_YEAR) for a, b in zip(out["2000"], out["2024"])]
    return out.sort_values("Multiple", ascending=False)

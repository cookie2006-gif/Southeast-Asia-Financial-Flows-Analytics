"""Load and clean the three raw datasets into one tidy ASEAN panel.

Sources
-------
* World Bank / KNOMAD  - inward remittance flows (US$ million, wide format)
* World Bank WDI       - FDI net inflows, BoP (current US$, wide format)
* World Bank WDI       - GDP (current US$, wide format)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

START_YEAR, END_YEAR = 2000, 2024

# ISO3 code -> (display name, name used in the KNOMAD remittance file)
ASEAN = {
    "BRN": ("Brunei", "Brunei Darussalam"),
    "KHM": ("Cambodia", "Cambodia"),
    "IDN": ("Indonesia", "Indonesia"),
    "LAO": ("Lao PDR", "Lao PDR"),
    "MYS": ("Malaysia", "Malaysia"),
    "MMR": ("Myanmar", "Myanmar"),
    "PHL": ("Philippines", "Philippines"),
    "SGP": ("Singapore", "Singapore"),
    "THA": ("Thailand", "Thailand"),
    "TLS": ("Timor-Leste", "Timor-Leste"),
    "VNM": ("Vietnam", "Vietnam"),
}


def load_remittances() -> pd.DataFrame:
    """Return ASEAN remittance inflows in US$ million (Country, Code, Year, Remittances).

    The KNOMAD file encodes "not reported" as 0 for several economies
    (e.g. Singapore, Brunei), so zeros are treated as missing.
    """
    raw = pd.read_excel(RAW / "inward_remittance_flows.xlsx")
    raw = raw.rename(columns={raw.columns[0]: "knomad_name"})
    raw["knomad_name"] = raw["knomad_name"].astype(str).str.replace("\xa0", " ").str.strip()

    name_to_code = {v[1]: code for code, v in ASEAN.items()}
    raw = raw[raw["knomad_name"].isin(name_to_code)].copy()
    raw["Code"] = raw["knomad_name"].map(name_to_code)

    long = raw.melt(id_vars=["knomad_name", "Code"], var_name="Year", value_name="Remittances")
    long["Year"] = pd.to_numeric(long["Year"], errors="coerce")
    long["Remittances"] = pd.to_numeric(long["Remittances"], errors="coerce").replace(0, np.nan)
    return long.dropna(subset=["Year"]).astype({"Year": int}).drop(columns="knomad_name")


def _load_wdi(filename: str, value_name: str) -> pd.DataFrame:
    """Load a World Bank WDI wide CSV (4 metadata rows) into long US$ million format."""
    raw = pd.read_csv(RAW / filename, skiprows=4)
    raw = raw[raw["Country Code"].isin(ASEAN)]
    years = [str(y) for y in range(START_YEAR, END_YEAR + 1)]
    long = raw.melt(id_vars="Country Code", value_vars=years, var_name="Year", value_name=value_name)
    long = long.rename(columns={"Country Code": "Code"})
    long["Year"] = long["Year"].astype(int)
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce") / 1e6
    return long


def load_panel() -> pd.DataFrame:
    """ASEAN country-year panel: Remittances, FDI, GDP (US$ million) and derived ratios."""
    panel = (
        load_remittances()
        .merge(_load_wdi("fdi_net_flows.csv", "FDI"), on=["Code", "Year"], how="outer")
        .merge(_load_wdi("gdp.csv", "GDP"), on=["Code", "Year"], how="outer")
    )
    panel["Country"] = panel["Code"].map(lambda c: ASEAN[c][0])
    panel = panel[panel["Year"].between(START_YEAR, END_YEAR)]
    panel = panel.sort_values(["Code", "Year"]).reset_index(drop=True)

    panel["Remit_pct_GDP"] = panel["Remittances"] / panel["GDP"] * 100
    panel["FDI_pct_GDP"] = panel["FDI"] / panel["GDP"] * 100
    panel["Remit_to_FDI"] = panel["Remittances"] / panel["FDI"].where(panel["FDI"] > 0)
    panel["Remit_YoY_pct"] = panel.groupby("Code")["Remittances"].pct_change(fill_method=None) * 100
    return panel[["Country", "Code", "Year", "Remittances", "FDI", "GDP",
                  "Remit_pct_GDP", "FDI_pct_GDP", "Remit_to_FDI", "Remit_YoY_pct"]]

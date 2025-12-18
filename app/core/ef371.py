import pandas as pd
from pathlib import Path

EF_PATH = Path(__file__).resolve().parents[1] / "data" / "tblEF_371.csv"

def load_ef_table() -> pd.DataFrame:
    df = pd.read_csv(EF_PATH)
    # ensure numeric
    df["LHV"] = pd.to_numeric(df["LHV"], errors="coerce")
    df["EF_CO2"] = pd.to_numeric(df["EF_CO2"], errors="coerce")
    return df

def list_fuels(df_ef: pd.DataFrame) -> list[str]:
    return sorted(df_ef["fuel_name"].dropna().unique().tolist())

def get_unit_for_fuel(df_ef: pd.DataFrame, fuel_name: str) -> str:
    row = df_ef[df_ef["fuel_name"] == fuel_name].head(1)
    if row.empty:
        return ""
    return str(row.iloc[0]["unit"])

import pandas as pd

def calculate_co2(df_usage: pd.DataFrame, df_ef: pd.DataFrame) -> pd.DataFrame:
    """
    CO2 (kg CO2) = Q * LHV * EF_CO2
    Interpreting EF_CO2 as kg CO2 / GJ and LHV as GJ per unit of activity data.
    (This matches the common structure: qty * НТС * EF_CO2.)
    If your EF_CO2/LHV units differ, adjust here.
    """
    if df_usage.empty:
        return df_usage.copy()

    left = df_usage.copy()
    ef = df_ef.copy()

    merged = left.merge(
        ef[["fuel_name", "unit", "LHV", "EF_CO2"]],
        on="fuel_name",
        how="left",
        suffixes=("", "_ef")
    )

    # mark unit mismatch
    merged["unit_match"] = merged["unit"] == merged["unit_ef"]

    merged["LHV"] = pd.to_numeric(merged["LHV"], errors="coerce")
    merged["EF_CO2"] = pd.to_numeric(merged["EF_CO2"], errors="coerce")
    merged["qty"] = pd.to_numeric(merged["qty"], errors="coerce")

    merged["CO2_kg"] = merged["qty"] * merged["LHV"] * merged["EF_CO2"]
    merged["CO2_t"] = merged["CO2_kg"] / 1000.0

    return merged

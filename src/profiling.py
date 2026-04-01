import pandas as pd

def _sample_values(series: pd.Series, max_samples: int = 5) -> list:
    values = series.dropna().astype(str).head(max_samples).tolist()
    return values


def build_column_profiles(df: pd.DataFrame, max_samples: int = 5) -> list[dict]:
    profiles = []
    n_rows = len(df)

    for col in df.columns:
        s = df[col]
        non_null = s.dropna()

        null_count = int(s.isna().sum())
        null_rate = null_count / n_rows if n_rows > 0 else 0.0
        n_unique = int(non_null.nunique())
        unique_ratio = n_unique / len(non_null) if len(non_null) > 0 else 0.0

        profiles.append({
            "column_name": col,
            "dtype": str(s.dtype),
            "row_count": n_rows,
            "null_count": null_count,
            "null_rate": round(null_rate, 4),
            "n_unique_non_null": n_unique,
            "unique_ratio_non_null": round(unique_ratio, 4),
            "sample_values": _sample_values(s, max_samples=max_samples),
        })

    return profiles
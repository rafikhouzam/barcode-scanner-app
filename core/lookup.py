# core/lookup.py

def load_lookup_df(unit):
    import pandas as pd
    if unit == "Aneri Jewels" or unit == "EDB":
        return pd.read_parquet("barcode_lookup.parquet")
    return pd.DataFrame()

def lookup_barcode(bc, lookup_df, comment):
    from datetime import datetime
    if bc not in lookup_df.index:
        return None
    row = lookup_df.loc[bc]
    return {
        "barcode": bc,
        "style_cd": row["style_cd"],
        "description": row["style_description"],
        "category": row["style_category"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comment": comment.strip()
    }
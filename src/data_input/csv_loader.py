from pathlib import Path

import pandas as pd


VALIDATION_COLUMN_MAPPING = {
    "Poszt ID": "post_id",
    "Poszt típusa": "post_type",
    "Poszt link": "post_link",
    "Komment ID": "comment_id",
    "Komment tartalma": "comment_text",
    "Kézi címke": "manual_label",
    "Modell címke": "model_label",
    "Megjegyzés": "note",
}

INTERNAL_REQUIRED_COLUMNS = {
    "comment_id",
    "comment_text",
}


def load_csv(file_path: str | Path) -> pd.DataFrame:
    
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"A megadott fájl nem található: {path}")

    return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.copy()
    df.columns = df.columns.str.strip()
    return df


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
) -> None:
    
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "A bemeneti fájl nem tartalmazza a szükséges oszlopokat: "
            f"{missing_columns}"
        )


def normalize_columns(
    df: pd.DataFrame,
    column_mapping: dict[str, str],
) -> pd.DataFrame:
    
    df = df.copy()
    return df.rename(columns=column_mapping)


def clean_comment_rows(df: pd.DataFrame) -> pd.DataFrame:
    
    validate_required_columns(df, INTERNAL_REQUIRED_COLUMNS)

    df = df.copy()
    df = df.dropna(subset=["comment_text"])
    df["comment_text"] = df["comment_text"].astype(str).str.strip()
    df = df[df["comment_text"] != ""]

    return df


def load_validation_dataset(file_path: str | Path) -> pd.DataFrame:
    
    df = load_csv(file_path)
    df = clean_column_names(df)

    validate_required_columns(df, set(VALIDATION_COLUMN_MAPPING.keys()))

    df = normalize_columns(df, VALIDATION_COLUMN_MAPPING)
    df = clean_comment_rows(df)

    return df
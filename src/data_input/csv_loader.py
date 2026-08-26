from pathlib import Path

import pandas as pd

from data_model.schema import (
    REQUIRED_POST_CONTEXT_COLUMNS,
    INTERNAL_DATA_COLUMNS,
)


VALIDATION_COLUMN_MAPPING = {
    "Poszt ID": "post_id",
    "Poszt típusa": "post_type",
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

def load_post_context_csv(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"A megadott fájl nem található: {path}")

    df = pd.read_csv(path, sep=",", encoding="utf-8-sig")
    df = clean_column_names(df)

    validate_required_columns(df, set(REQUIRED_POST_CONTEXT_COLUMNS))

    text_columns = [
        "post_text",
        "image_context_text",
        "video_context_text",
        "note",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str).str.strip()

    return df

def merge_comments_with_post_context(
    comments_df: pd.DataFrame,
    post_context_df: pd.DataFrame,
) -> pd.DataFrame:
    merged_df = comments_df.merge(
        post_context_df,
        on="post_id",
        how="left",
        suffixes=("", "_post"),
    )

    if "post_type_post" in merged_df.columns:
        merged_df["post_type"] = merged_df["post_type"].fillna(
            merged_df["post_type_post"]
        )
        merged_df = merged_df.drop(columns=["post_type_post"])

    if "note_post" in merged_df.columns:
        merged_df = merged_df.rename(columns={"note_post": "post_context_note"})

    if "confidence" not in merged_df.columns:
        merged_df["confidence"] = None

    for column in INTERNAL_DATA_COLUMNS:
        if column not in merged_df.columns:
            merged_df[column] = None

    return merged_df
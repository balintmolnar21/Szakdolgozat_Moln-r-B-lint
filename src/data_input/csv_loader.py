from pathlib import Path

import pandas as pd

from data_model.schema import (
    REQUIRED_POST_CONTEXT_COLUMNS,
    INTERNAL_DATA_COLUMNS,
)


# A CSV-fájlok magyar oszlopneveinek leképezése
# a program belső angol oszlopneveire.
LABELED_COMMENT_COLUMN_MAPPING = {
    "Poszt ID": "post_id",
    "Poszt típusa": "post_type",
    "Komment ID": "comment_id",
    "Komment tartalma": "comment_text",
    "Kézi címke": "manual_label",
    "Modell címke": "model_label",
    "Megjegyzés": "note",
}


# A kézzel címkézett komment-adathalmazokban
# ténylegesen kötelező bemeneti oszlopok.
REQUIRED_LABELED_COMMENT_COLUMNS = {
    "Poszt ID",
    "Komment ID",
    "Komment tartalma",
    "Kézi címke",
}


# A kommentadatok belső feldolgozásához szükséges minimum.
INTERNAL_REQUIRED_COLUMNS = {
    "comment_id",
    "comment_text",
}


# Támogatott kézi sentimentcímkék.
SUPPORTED_MANUAL_LABELS = {
    "positive",
    "negative",
    "neutral",
}


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Általános CSV-beolvasó függvény.

    Automatikusan megpróbálja felismerni az elválasztó karaktert,
    és UTF-8-SIG kódolást használ.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"A megadott fájl nem található: {path}"
        )

    return pd.read_csv(
        path,
        sep=None,
        engine="python",
        encoding="utf-8-sig",
    )


def clean_column_names(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Eltávolítja az oszlopnevek elején és végén
    található felesleges szóközöket.
    """

    df = df.copy()
    df.columns = df.columns.str.strip()

    return df


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
) -> None:
    """
    Ellenőrzi, hogy az adathalmaz tartalmazza-e
    az összes szükséges oszlopot.
    """

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
    """
    A magyar CSV-oszlopneveket a rendszer
    belső angol mezőneveire alakítja.
    """

    df = df.copy()

    return df.rename(
        columns=column_mapping
    )


def clean_comment_rows(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Eltávolítja azokat a rekordokat, amelyekhez
    nem tartozik feldolgozható komment.
    """

    validate_required_columns(
        df,
        INTERNAL_REQUIRED_COLUMNS,
    )

    df = df.copy()

    df = df.dropna(
        subset=["comment_text"]
    )

    df["comment_text"] = (
        df["comment_text"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["comment_text"] != ""
    ]

    return df


def normalize_manual_labels(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalizálja és ellenőrzi a kézzel megadott
    sentimentcímkéket.
    """

    if "manual_label" not in df.columns:
        raise ValueError(
            "A kézzel címkézett adathalmazból "
            "hiányzik a manual_label oszlop."
        )

    df = df.copy()

    df["manual_label"] = (
        df["manual_label"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    missing_label_mask = (
        df["manual_label"] == ""
    )

    if missing_label_mask.any():
        missing_count = int(
            missing_label_mask.sum()
        )

        raise ValueError(
            "A kézzel címkézett adathalmazban "
            f"{missing_count} kommenthez nem tartozik "
            "manual_label érték."
        )

    unknown_labels = sorted(
        set(df["manual_label"].unique())
        - SUPPORTED_MANUAL_LABELS
    )

    if unknown_labels:
        raise ValueError(
            "Az adathalmaz nem támogatott kézi "
            "sentimentcímkéket tartalmaz: "
            + ", ".join(unknown_labels)
        )

    return df


def add_optional_comment_columns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Létrehozza az opcionális kommentmezőket,
    ha azok nem szerepelnek a bemeneti CSV-ben.

    Ez lehetővé teszi, hogy a train, validation
    és test adatok egyszerűbb CSV-struktúrával
    is használhatók legyenek.
    """

    df = df.copy()

    optional_columns = {
        "post_type": None,
        "model_label": None,
        "note": None,
    }

    for column_name, default_value in optional_columns.items():
        if column_name not in df.columns:
            df[column_name] = default_value

    return df


def load_labeled_comments_dataset(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Kézzel címkézett komment-adathalmaz betöltése.

    Ugyanez a függvény használható:
    - train halmazhoz,
    - validation halmazhoz,
    - test halmazhoz.
    """

    df = load_csv(
        file_path
    )

    df = clean_column_names(
        df
    )

    validate_required_columns(
        df,
        REQUIRED_LABELED_COMMENT_COLUMNS,
    )

    df = normalize_columns(
        df,
        LABELED_COMMENT_COLUMN_MAPPING,
    )

    df = clean_comment_rows(
        df
    )

    df = normalize_manual_labels(
        df
    )

    df = add_optional_comment_columns(
        df
    )

    return df


def load_validation_dataset(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Visszafelé kompatibilis wrapper.

    A régi pipeline jelenleg ezt a függvénynevet használja.
    A későbbi refaktorálásig meghagyjuk, így a meglévő
    alkalmazás működése nem törik el.
    """

    return load_labeled_comments_dataset(
        file_path
    )


def load_post_context_csv(
    file_path: str | Path,
) -> pd.DataFrame:
    """
    Posztkontextus-adatok betöltése.
    """

    path = Path(
        file_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"A megadott fájl nem található: {path}"
        )

    df = pd.read_csv(
        path,
        sep=",",
        encoding="utf-8-sig",
    )

    df = clean_column_names(
        df
    )

    validate_required_columns(
        df,
        set(REQUIRED_POST_CONTEXT_COLUMNS),
    )

    text_columns = [
        "post_text",
        "image_context_text",
        "video_context_text",
        "note",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


def merge_comments_with_post_context(
    comments_df: pd.DataFrame,
    post_context_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    A kommenteket post_id alapján összekapcsolja
    a hozzájuk tartozó posztkontextussal.
    """

    merged_df = comments_df.merge(
        post_context_df,
        on="post_id",
        how="left",
        suffixes=("", "_post"),
    )

    if "post_type_post" in merged_df.columns:
        merged_df["post_type"] = (
            merged_df["post_type"].fillna(
                merged_df["post_type_post"]
            )
        )

        merged_df = merged_df.drop(
            columns=["post_type_post"]
        )

    if "note_post" in merged_df.columns:
        merged_df = merged_df.rename(
            columns={
                "note_post": "post_context_note"
            }
        )

    if "confidence" not in merged_df.columns:
        merged_df["confidence"] = None

    for column in INTERNAL_DATA_COLUMNS:
        if column not in merged_df.columns:
            merged_df[column] = None

    return merged_df
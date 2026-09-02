from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from data_input.csv_loader import (
    load_labeled_comments_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)
from preprocessing.text_preprocessor import clean_text
from preprocessing.emoji_lib import validate_emoji_mode


LABEL_TO_ID = {
    "negative": 0,
    "neutral": 1,
    "positive": 2,
}

ID_TO_LABEL = {
    0: "negative",
    1: "neutral",
    2: "positive",
}


@dataclass
class TrainingDatasetBundle:
    """
    A context-aware fine-tuninghoz használt
    train és validation adathalmazokat tartalmazza.
    """

    train_dataframe: pd.DataFrame
    validation_dataframe: pd.DataFrame
    emoji_mode: str


def add_numeric_labels(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    A kézi sentimentcímkéket numerikus
    osztályazonosítókká alakítja.

    negative -> 0
    neutral  -> 1
    positive -> 2
    """

    dataframe = dataframe.copy()

    if "manual_label" not in dataframe.columns:
        raise ValueError(
            "A tanító adathalmazból hiányzik "
            "a manual_label oszlop."
        )

    dataframe["label"] = dataframe[
        "manual_label"
    ].map(
        LABEL_TO_ID
    )

    if dataframe["label"].isna().any():
        invalid_labels = (
            dataframe.loc[
                dataframe["label"].isna(),
                "manual_label",
            ]
            .dropna()
            .unique()
        )

        raise ValueError(
            "Nem támogatott sentimentcímke található: "
            + ", ".join(
                str(label)
                for label in invalid_labels
            )
        )

    dataframe["label"] = dataframe[
        "label"
    ].astype(int)

    return dataframe


def validate_post_context(
    dataframe: pd.DataFrame,
) -> None:
    """
    Ellenőrzi, hogy minden kommenthez
    rendelkezésre áll-e posztszöveg.
    """

    if "post_text" not in dataframe.columns:
        raise ValueError(
            "A context-aware tanításhoz hiányzik "
            "a post_text oszlop."
        )

    missing_context_mask = (
        dataframe["post_text"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
    )

    if missing_context_mask.any():
        missing_post_ids = (
            dataframe.loc[
                missing_context_mask,
                "post_id",
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        raise ValueError(
            "A context-aware tanításhoz egy vagy több "
            "kommenthez nem található használható posztszöveg. "
            "Érintett post_id értékek: "
            + ", ".join(missing_post_ids)
        )


def add_processed_context_fields(
    dataframe: pd.DataFrame,
    emoji_mode: str,
) -> pd.DataFrame:
    """
    Külön előfeldolgozza a poszt és a komment
    szövegét.

    Az eredeti post_text és comment_text mezők
    változatlanul megmaradnak.
    """

    dataframe = dataframe.copy()

    validate_emoji_mode(
        emoji_mode
    )

    validate_post_context(
        dataframe
    )

    if "comment_text" not in dataframe.columns:
        raise ValueError(
            "A tanító adathalmazból hiányzik "
            "a comment_text oszlop."
        )

    dataframe["processed_post_text"] = (
        dataframe["post_text"].apply(
            lambda text: clean_text(
                text,
                emoji_mode=emoji_mode,
            )
        )
    )

    dataframe["processed_comment_text"] = (
        dataframe["comment_text"].apply(
            lambda text: clean_text(
                text,
                emoji_mode=emoji_mode,
            )
        )
    )

    empty_comment_mask = (
        dataframe["processed_comment_text"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
    )

    if empty_comment_mask.any():
        empty_count = int(
            empty_comment_mask.sum()
        )

        raise ValueError(
            "Az előfeldolgozás után "
            f"{empty_count} komment szövege üres."
        )

    return dataframe


def prepare_context_training_dataframe(
    comments_file: str | Path,
    post_context_file: str | Path,
    emoji_mode: str = "raw",
) -> pd.DataFrame:
    """
    Egy context-aware adathalmaz teljes
    előkészítését végzi el.

    Folyamat:
    1. kommentek betöltése,
    2. posztkontextus betöltése,
    3. összekapcsolás post_id alapján,
    4. poszt és komment előfeldolgozása,
    5. numerikus label létrehozása.
    """

    normalized_emoji_mode = validate_emoji_mode(
        emoji_mode
    )

    comments_dataframe = (
        load_labeled_comments_dataset(
            comments_file
        )
    )

    post_context_dataframe = (
        load_post_context_csv(
            post_context_file
        )
    )

    merged_dataframe = (
        merge_comments_with_post_context(
            comments_dataframe,
            post_context_dataframe,
        )
    )

    merged_dataframe = (
        add_processed_context_fields(
            dataframe=merged_dataframe,
            emoji_mode=normalized_emoji_mode,
        )
    )

    merged_dataframe = add_numeric_labels(
        merged_dataframe
    )

    return merged_dataframe


def create_training_dataset_bundle(
    train_comments_file: str | Path,
    train_post_context_file: str | Path,
    validation_comments_file: str | Path,
    validation_post_context_file: str | Path,
    emoji_mode: str = "raw",
) -> TrainingDatasetBundle:
    """
    A train és validation halmazt azonos
    preprocessing-beállítással készíti elő.
    """

    normalized_emoji_mode = validate_emoji_mode(
        emoji_mode
    )

    train_dataframe = (
        prepare_context_training_dataframe(
            comments_file=train_comments_file,
            post_context_file=train_post_context_file,
            emoji_mode=normalized_emoji_mode,
        )
    )

    validation_dataframe = (
        prepare_context_training_dataframe(
            comments_file=validation_comments_file,
            post_context_file=validation_post_context_file,
            emoji_mode=normalized_emoji_mode,
        )
    )

    return TrainingDatasetBundle(
        train_dataframe=train_dataframe,
        validation_dataframe=validation_dataframe,
        emoji_mode=normalized_emoji_mode,
    )


def calculate_label_distribution(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Sentimentosztályonként kiszámítja
    a darabszámot és az arányt.
    """

    total_count = len(
        dataframe
    )

    records = []

    for label_name, label_id in LABEL_TO_ID.items():
        count = int(
            (
                dataframe["manual_label"]
                == label_name
            ).sum()
        )

        ratio = (
            count / total_count * 100
            if total_count > 0
            else 0.0
        )

        records.append(
            {
                "label": label_name,
                "label_id": label_id,
                "count": count,
                "ratio": round(
                    ratio,
                    2,
                ),
            }
        )

    return pd.DataFrame(
        records
    )


def print_dataset_summary(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """
    Konzolos összefoglalót készít
    az előkészített halmazról.
    """

    print(
        f"\n{dataset_name}"
    )

    print(
        "-" * 60
    )

    print(
        f"Rekordok száma: {len(dataframe)}"
    )

    print(
        f"Posztok száma: "
        f"{dataframe['post_id'].nunique()}"
    )

    print(
        calculate_label_distribution(
            dataframe
        ).to_string(
            index=False
        )
    )
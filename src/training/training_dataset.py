from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from data_input.csv_loader import (
    load_labeled_comments_dataset,
)
from preprocessing.text_preprocessor import (
    clean_text,
)
from preprocessing.emoji_lib import (
    validate_emoji_mode,
)


# A saját háromosztályos fine-tuning modell címkézése.
LABEL_TO_ID = {
    "negative": 0,
    "neutral": 1,
    "positive": 2,
}

ID_TO_LABEL = {
    label_id: label
    for label, label_id in LABEL_TO_ID.items()
}


@dataclass
class TrainingDatasetBundle:
    """
    A fine-tuninghoz használt train és validation
    adathalmazokat összefogó adatstruktúra.
    """

    train_dataframe: pd.DataFrame
    validation_dataframe: pd.DataFrame
    emoji_mode: str


def add_numeric_labels(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    A szöveges sentimentcímkéket numerikus
    osztályazonosítóra alakítja.

    negative -> 0
    neutral  -> 1
    positive -> 2
    """

    dataframe = dataframe.copy()

    if "manual_label" not in dataframe.columns:
        raise ValueError(
            "A numerikus címkézéshez hiányzik "
            "a manual_label oszlop."
        )

    dataframe["label"] = (
        dataframe["manual_label"]
        .map(LABEL_TO_ID)
    )

    if dataframe["label"].isna().any():
        invalid_rows = dataframe.loc[
            dataframe["label"].isna(),
            "manual_label",
        ].unique()

        raise ValueError(
            "Nem támogatott sentimentcímke található "
            "az adathalmazban: "
            + ", ".join(
                str(value)
                for value in invalid_rows
            )
        )

    dataframe["label"] = (
        dataframe["label"]
        .astype(int)
    )

    return dataframe


def add_processed_text(
    dataframe: pd.DataFrame,
    emoji_mode: str,
) -> pd.DataFrame:
    """
    A nyers comment_text oszlopból létrehozza
    a fine-tuninghoz használt processed_text mezőt.

    Az eredeti comment_text változatlan marad.
    """

    dataframe = dataframe.copy()

    validate_emoji_mode(
        emoji_mode
    )

    if "comment_text" not in dataframe.columns:
        raise ValueError(
            "Az előfeldolgozáshoz hiányzik "
            "a comment_text oszlop."
        )

    dataframe["processed_text"] = (
        dataframe["comment_text"]
        .apply(
            lambda text: clean_text(
                text,
                emoji_mode=emoji_mode,
            )
        )
    )

    empty_text_mask = (
        dataframe["processed_text"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
    )

    if empty_text_mask.any():
        empty_count = int(
            empty_text_mask.sum()
        )

        raise ValueError(
            "Az előfeldolgozás után "
            f"{empty_count} rekord szövege üres."
        )

    return dataframe


def prepare_training_dataframe(
    file_path: str | Path,
    emoji_mode: str = "raw",
) -> pd.DataFrame:
    """
    Egy kézzel címkézett kommentfájlt előkészít
    a fine-tuninghoz.

    A függvény:
    1. betölti a CSV-t,
    2. ellenőrzi a kézi címkéket,
    3. létrehozza a processed_text mezőt,
    4. numerikus label értéket rendel a címkéhez.
    """

    validate_emoji_mode(
        emoji_mode
    )

    dataframe = load_labeled_comments_dataset(
        file_path
    )

    dataframe = add_processed_text(
        dataframe=dataframe,
        emoji_mode=emoji_mode,
    )

    dataframe = add_numeric_labels(
        dataframe
    )

    return dataframe


def create_training_dataset_bundle(
    train_file: str | Path,
    validation_file: str | Path,
    emoji_mode: str = "raw",
) -> TrainingDatasetBundle:
    """
    Betölti és előkészíti a train és validation
    adathalmazokat ugyanazzal az emoji-stratégiával.
    """

    normalized_emoji_mode = validate_emoji_mode(
        emoji_mode
    )

    train_dataframe = prepare_training_dataframe(
        file_path=train_file,
        emoji_mode=normalized_emoji_mode,
    )

    validation_dataframe = prepare_training_dataframe(
        file_path=validation_file,
        emoji_mode=normalized_emoji_mode,
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
    Elkészíti az adathalmaz sentimentosztályainak
    darabszám- és százalékos megoszlását.
    """

    required_columns = {
        "manual_label",
        "label",
    }

    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "Az osztályeloszlás számításához "
            "szükséges oszlopok közül hiányzik: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    total_count = len(
        dataframe
    )

    distribution_records = []

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

        distribution_records.append(
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
        distribution_records
    )


def print_dataset_summary(
    dataframe: pd.DataFrame,
    dataset_name: str,
) -> None:
    """
    Rövid konzolos összefoglalót ír ki
    az előkészített adathalmazról.
    """

    print(
        f"\n{dataset_name}"
    )

    print(
        "-" * 50
    )

    print(
        f"Rekordok száma: {len(dataframe)}"
    )

    print(
        calculate_label_distribution(
            dataframe
        ).to_string(
            index=False
        )
    )
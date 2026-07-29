from dataclasses import dataclass

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


SENTIMENT_LABELS = [
    "negative",
    "neutral",
    "positive",
]

LABEL_MAPPING = {
    "negative": "negative",
    "negatív": "negative",
    "negative_sentiment": "negative",

    "neutral": "neutral",
    "semleges": "neutral",
    "neutral_sentiment": "neutral",

    "positive": "positive",
    "pozitív": "positive",
    "positive_sentiment": "positive",
}


@dataclass
class ModelEvaluationResult:
    """
    A sentimentmodell kiértékelésének eredményeit tárolja.
    """

    evaluated_data: pd.DataFrame
    metrics: pd.DataFrame
    confusion_matrix: pd.DataFrame
    misclassified_comments: pd.DataFrame
    low_confidence_comments: pd.DataFrame
    accuracy: float


def normalize_sentiment_label(value: object) -> str | None:
    """
    Egy sentimentcímkét egységes angol formátumra alakít.

    Támogatott végleges címkék:
    - positive
    - negative
    - neutral

    Args:
        value: A normalizálandó címke.

    Returns:
        Az egységesített címke, vagy None hiányzó érték esetén.

    Raises:
        ValueError: Ha a címke nem támogatott.
    """
    if pd.isna(value):
        return None

    normalized_value = str(value).strip().lower()

    if not normalized_value:
        return None

    if normalized_value not in LABEL_MAPPING:
        raise ValueError(
            f"Nem támogatott sentimentcímke: {value!r}. "
            f"Engedélyezett címkék: "
            f"{', '.join(SENTIMENT_LABELS)}."
        )

    return LABEL_MAPPING[normalized_value]


def validate_evaluation_columns(
    dataframe: pd.DataFrame,
    manual_label_column: str,
    model_label_column: str,
) -> None:
    """
    Ellenőrzi a kiértékeléshez szükséges oszlopokat.

    Args:
        dataframe: A kiértékelendő adathalmaz.
        manual_label_column: A kézi címkéket tartalmazó oszlop.
        model_label_column: A modell címkéit tartalmazó oszlop.

    Raises:
        ValueError: Üres adathalmaz vagy hiányzó oszlop esetén.
    """
    if dataframe.empty:
        raise ValueError(
            "A modellkiértékeléshez kapott adathalmaz üres."
        )

    required_columns = {
        manual_label_column,
        model_label_column,
    }

    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        missing_columns_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "A modellkiértékeléshez szükséges oszlopok "
            f"közül hiányzik: {missing_columns_text}."
        )


def prepare_evaluation_data(
    dataframe: pd.DataFrame,
    manual_label_column: str,
    model_label_column: str,
) -> pd.DataFrame:
    """
    Előkészíti és egységesíti a kézi, valamint a modellcímkéket.

    A hiányzó kézi vagy modellcímkével rendelkező sorok nem
    kerülnek bele a kiértékelésbe.
    """
    validate_evaluation_columns(
        dataframe=dataframe,
        manual_label_column=manual_label_column,
        model_label_column=model_label_column,
    )

    evaluation_data = dataframe.copy()

    evaluation_data["manual_label_normalized"] = (
        evaluation_data[manual_label_column].apply(
            normalize_sentiment_label
        )
    )

    evaluation_data["model_label_normalized"] = (
        evaluation_data[model_label_column].apply(
            normalize_sentiment_label
        )
    )

    evaluation_data = evaluation_data.dropna(
        subset=[
            "manual_label_normalized",
            "model_label_normalized",
        ]
    ).copy()

    if evaluation_data.empty:
        raise ValueError(
            "Nincs olyan rekord, amely egyszerre tartalmaz "
            "kézi és modell által létrehozott sentimentcímkét."
        )

    evaluation_data["is_correct_prediction"] = (
        evaluation_data["manual_label_normalized"]
        == evaluation_data["model_label_normalized"]
    )

    return evaluation_data


def create_metrics_dataframe(
    manual_labels: pd.Series,
    model_labels: pd.Series,
) -> pd.DataFrame:
    """
    Osztályonkénti és összesített kiértékelési mutatókat készít.
    """
    report = classification_report(
        manual_labels,
        model_labels,
        labels=SENTIMENT_LABELS,
        output_dict=True,
        zero_division=0,
    )

    metric_rows: list[dict[str, object]] = []

    for label in SENTIMENT_LABELS:
        label_metrics = report[label]

        metric_rows.append(
            {
                "category": label,
                "precision": label_metrics["precision"],
                "recall": label_metrics["recall"],
                "f1_score": label_metrics["f1-score"],
                "support": int(label_metrics["support"]),
            }
        )

    for average_name in ["macro avg", "weighted avg"]:
        average_metrics = report[average_name]

        metric_rows.append(
            {
                "category": average_name.replace(" ", "_"),
                "precision": average_metrics["precision"],
                "recall": average_metrics["recall"],
                "f1_score": average_metrics["f1-score"],
                "support": int(average_metrics["support"]),
            }
        )

    return pd.DataFrame(metric_rows)


def create_confusion_matrix_dataframe(
    manual_labels: pd.Series,
    model_labels: pd.Series,
) -> pd.DataFrame:
    """
    Elkészíti a confusion matrix táblázatos változatát.

    A sorok a kézi címkéket, az oszlopok a modell
    predikcióit jelentik.
    """
    matrix = confusion_matrix(
        manual_labels,
        model_labels,
        labels=SENTIMENT_LABELS,
    )

    return pd.DataFrame(
        matrix,
        index=[
            f"actual_{label}"
            for label in SENTIMENT_LABELS
        ],
        columns=[
            f"predicted_{label}"
            for label in SENTIMENT_LABELS
        ],
    )


def evaluate_sentiment_model(
    dataframe: pd.DataFrame,
    manual_label_column: str,
    model_label_column: str,
    confidence_column: str = "confidence",
    confidence_threshold: float = 0.60,
) -> ModelEvaluationResult:
    """
    Végrehajtja a sentimentmodell teljes alapkiértékelését.

    Args:
        dataframe: A kézi és modellcímkéket tartalmazó adathalmaz.
        manual_label_column: A kézi címke oszlopának neve.
        model_label_column: A modellcímke oszlopának neve.

    Returns:
        A mérőszámokat, confusion matrixot és hibás
        predikciókat tartalmazó eredményobjektum.
    """
    evaluation_data = prepare_evaluation_data(
        dataframe=dataframe,
        manual_label_column=manual_label_column,
        model_label_column=model_label_column,
    )

    manual_labels = evaluation_data[
        "manual_label_normalized"
    ]

    model_labels = evaluation_data[
        "model_label_normalized"
    ]

    accuracy = accuracy_score(
        manual_labels,
        model_labels,
    )

    metrics = create_metrics_dataframe(
        manual_labels=manual_labels,
        model_labels=model_labels,
    )

    confusion_matrix_dataframe = (
        create_confusion_matrix_dataframe(
            manual_labels=manual_labels,
            model_labels=model_labels,
        )
    )

    misclassified_comments = evaluation_data.loc[
        ~evaluation_data["is_correct_prediction"]
    ].copy()

    if confidence_column not in evaluation_data.columns:
        raise ValueError(
            "A konfidenciaelemzéshez szükséges oszlop hiányzik: "
            f"{confidence_column}."
        )

    evaluation_data[confidence_column] = pd.to_numeric(
        evaluation_data[confidence_column],
        errors="coerce",
    )

    low_confidence_comments = evaluation_data.loc[
        evaluation_data[confidence_column].notna()
        & (
            evaluation_data[confidence_column]
            < confidence_threshold
        )
    ].copy()

    return ModelEvaluationResult(
        evaluated_data=evaluation_data,
        metrics=metrics,
        confusion_matrix=confusion_matrix_dataframe,
        misclassified_comments=misclassified_comments,
        low_confidence_comments=low_confidence_comments,
        accuracy=float(accuracy),
    )
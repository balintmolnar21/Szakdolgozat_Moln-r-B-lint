import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
)


def compute_training_metrics(
    evaluation_prediction,
) -> dict[str, float]:
    """
    A validation halmazon kiszámítja
    a fine-tuning főbb metrikáit.

    A modellválasztás alapja a macro F1.
    """

    predictions = (
        evaluation_prediction.predictions
    )

    labels = (
        evaluation_prediction.label_ids
    )

    if isinstance(predictions, tuple):
        predictions = predictions[0]

    predicted_labels = np.argmax(
        predictions,
        axis=-1,
    )

    accuracy = accuracy_score(
        labels,
        predicted_labels,
    )

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            labels,
            predicted_labels,
            average="macro",
            zero_division=0,
        )
    )

    return {
        "accuracy": float(accuracy),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
    }
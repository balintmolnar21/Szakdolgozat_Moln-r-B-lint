from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from torch.nn.functional import softmax
from transformers import AutoModelForSequenceClassification, AutoTokenizer


LABELS = ["negative", "neutral", "positive"]

ID_TO_LABEL = {
    0: "negative",
    1: "neutral",
    2: "positive",
}


@dataclass
class ContextAwareErrorAnalysisResult:
    """
    A context-aware modell validációs hibaanalízisének eredménye.
    """

    predictions: pd.DataFrame
    misclassified_comments: pd.DataFrame
    classification_report: pd.DataFrame
    confusion_matrix: pd.DataFrame
    accuracy: float
    macro_f1: float


def load_fine_tuned_model(model_directory: str):
    """
    Betölti a korábban finomhangolt context-aware modellt
    és a hozzá tartozó tokenizert.
    """

    tokenizer = AutoTokenizer.from_pretrained(model_directory)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_directory
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model.to(device)
    model.eval()

    return model, tokenizer, device


def predict_validation_dataframe(
    dataframe: pd.DataFrame,
    model,
    tokenizer,
    device,
    max_length: int = 128,
) -> pd.DataFrame:
    """
    A validation DataFrame minden rekordjára predikciót készít.

    A modell bemenete:
        post_text + comment_text

    A predikció célja:
        a komment sentiment címkéje.
    """

    required_columns = {
        "post_id",
        "comment_id",
        "post_text",
        "comment_text",
        "manual_label",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            "Hiányzó oszlopok a validation DataFrame-ből: "
            + ", ".join(sorted(missing_columns))
        )

    result_dataframe = dataframe.copy()

    predicted_labels = []
    confidence_values = []

    negative_probabilities = []
    neutral_probabilities = []
    positive_probabilities = []

    for _, row in result_dataframe.iterrows():

        post_text = str(row["post_text"])
        comment_text = str(row["comment_text"])

        encoding = tokenizer(
            post_text,
            comment_text,
            truncation="longest_first",
            max_length=max_length,
            return_tensors="pt",
        )

        encoding = {
            key: value.to(device)
            for key, value in encoding.items()
        }

        with torch.no_grad():
            outputs = model(**encoding)

        probabilities = softmax(
            outputs.logits,
            dim=-1
        )[0]

        probabilities = probabilities.cpu().numpy()

        predicted_id = int(np.argmax(probabilities))

        predicted_label = ID_TO_LABEL[predicted_id]

        confidence = float(probabilities[predicted_id])

        predicted_labels.append(predicted_label)
        confidence_values.append(confidence)

        negative_probabilities.append(float(probabilities[0]))
        neutral_probabilities.append(float(probabilities[1]))
        positive_probabilities.append(float(probabilities[2]))

    result_dataframe["predicted_label"] = predicted_labels
    result_dataframe["confidence"] = confidence_values

    result_dataframe["prob_negative"] = negative_probabilities
    result_dataframe["prob_neutral"] = neutral_probabilities
    result_dataframe["prob_positive"] = positive_probabilities

    result_dataframe["correct"] = (
        result_dataframe["manual_label"]
        == result_dataframe["predicted_label"]
    )

    return result_dataframe


def create_error_analysis(
    predictions: pd.DataFrame,
) -> ContextAwareErrorAnalysisResult:
    """
    Elkészíti a modell részletes validációs kiértékelését.
    """

    y_true = predictions["manual_label"]
    y_pred = predictions["predicted_label"]

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    report_dataframe = (
        pd.DataFrame(report_dict)
        .transpose()
        .reset_index()
        .rename(columns={"index": "label"})
    )

    macro_f1 = float(
        report_dict["macro avg"]["f1-score"]
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    confusion_dataframe = pd.DataFrame(
        matrix,
        index=[
            "actual_negative",
            "actual_neutral",
            "actual_positive",
        ],
        columns=[
            "predicted_negative",
            "predicted_neutral",
            "predicted_positive",
        ],
    )

    misclassified = predictions[
        predictions["correct"] == False
    ].copy()

    misclassified = misclassified.sort_values(
        by="confidence",
        ascending=False,
    )

    return ContextAwareErrorAnalysisResult(
        predictions=predictions,
        misclassified_comments=misclassified,
        classification_report=report_dataframe,
        confusion_matrix=confusion_dataframe,
        accuracy=float(accuracy),
        macro_f1=macro_f1,
    )


def export_error_analysis(
    result: ContextAwareErrorAnalysisResult,
    output_directory: str,
):
    """
    CSV és Excel formátumban elmenti a hibaanalízis eredményeit.
    """

    from pathlib import Path

    output_path = Path(output_directory)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions_path = (
        output_path / "validation_predictions.csv"
    )

    errors_path = (
        output_path / "misclassified_comments.csv"
    )

    report_path = (
        output_path / "classification_report.csv"
    )

    confusion_path = (
        output_path / "confusion_matrix.csv"
    )

    excel_path = (
        output_path / "validation_error_analysis.xlsx"
    )

    result.predictions.to_csv(
        predictions_path,
        index=False,
        encoding="utf-8-sig",
    )

    result.misclassified_comments.to_csv(
        errors_path,
        index=False,
        encoding="utf-8-sig",
    )

    result.classification_report.to_csv(
        report_path,
        index=False,
        encoding="utf-8-sig",
    )

    result.confusion_matrix.to_csv(
        confusion_path,
        encoding="utf-8-sig",
    )

    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl",
    ) as writer:

        result.predictions.to_excel(
            writer,
            sheet_name="Predictions",
            index=False,
        )

        result.misclassified_comments.to_excel(
            writer,
            sheet_name="Errors",
            index=False,
        )

        result.classification_report.to_excel(
            writer,
            sheet_name="Metrics",
            index=False,
        )

        result.confusion_matrix.to_excel(
            writer,
            sheet_name="Confusion Matrix",
        )

    return excel_path
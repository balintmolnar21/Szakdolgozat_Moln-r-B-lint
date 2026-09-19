from pathlib import Path
import sys

import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


# ============================================================
# PROJEKT ELÉRÉSI UTAK
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from data_input.csv_loader import (
    load_validation_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)

from preprocessing.text_preprocessor import clean_text


# ============================================================
# KONFIGURÁCIÓ
# ============================================================

VALIDATION_COMMENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "validation_comments.csv"
)

VALIDATION_POST_CONTEXT_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "validation_post_context.csv"
)

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "context_aware_hubert_text"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation"
    / "threshold_analysis"
)

MAX_LENGTH = 128

LABELS = [
    "negative",
    "neutral",
    "positive",
]

THRESHOLDS = [
    None,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]


# ============================================================
# MODELL PREDIKCIÓ
# ============================================================

def create_predictions(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Elkészíti a context-aware fine-tuned modell
    eredeti predikcióit a validation halmazon.

    A threshold alkalmazása később történik, így
    ugyanazokat a modellpredikciókat használjuk
    minden küszöbérték vizsgálatához.
    """

    print("\nFine-tuned modell betöltése...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_DIRECTORY
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_DIRECTORY
        )
    )

    model.eval()

    predicted_labels = []
    confidence_scores = []

    negative_probabilities = []
    neutral_probabilities = []
    positive_probabilities = []

    total = len(dataframe)

    print(
        f"Validation predikciók készítése: "
        f"{total} rekord"
    )

    for position, (_, row) in enumerate(
        dataframe.iterrows(),
        start=1,
    ):
        post_text = clean_text(
            row["post_text"],
            emoji_mode="text",
        )

        comment_text = clean_text(
            row["comment_text"],
            emoji_mode="text",
        )

        encoding = tokenizer(
            post_text,
            comment_text,
            return_tensors="pt",
            truncation="longest_first",
            max_length=MAX_LENGTH,
        )

        with torch.no_grad():
            output = model(**encoding)

        probabilities = torch.softmax(
            output.logits,
            dim=-1,
        )[0]

        predicted_id = int(
            torch.argmax(probabilities).item()
        )

        predicted_label = (
            model.config.id2label.get(
                predicted_id,
                LABELS[predicted_id],
            )
        )

        predicted_label = (
            str(predicted_label)
            .strip()
            .lower()
        )

        confidence = float(
            probabilities[predicted_id].item()
        )

        predicted_labels.append(
            predicted_label
        )

        confidence_scores.append(
            confidence
        )

        negative_probabilities.append(
            float(probabilities[0].item())
        )

        neutral_probabilities.append(
            float(probabilities[1].item())
        )

        positive_probabilities.append(
            float(probabilities[2].item())
        )

        if position % 25 == 0 or position == total:
            print(
                f"  Predikció: "
                f"{position}/{total}"
            )

    result_df = dataframe.copy()

    result_df["original_prediction"] = (
        predicted_labels
    )

    result_df["confidence"] = (
        confidence_scores
    )

    result_df["negative_probability"] = (
        negative_probabilities
    )

    result_df["neutral_probability"] = (
        neutral_probabilities
    )

    result_df["positive_probability"] = (
        positive_probabilities
    )

    return result_df


# ============================================================
# THRESHOLD ALKALMAZÁSA
# ============================================================

def apply_threshold(
    dataframe: pd.DataFrame,
    threshold: float | None,
) -> pd.Series:
    """
    Confidence threshold alkalmazása.

    Szabály:
    - ha nincs threshold, az eredeti predikció marad;
    - neutral predikció mindig neutral marad;
    - positive vagy negative predikció esetén,
      ha a confidence kisebb a küszöbnél,
      a predikció neutral lesz.
    """

    predictions = []

    for _, row in dataframe.iterrows():

        original_label = row[
            "original_prediction"
        ]

        confidence = float(
            row["confidence"]
        )

        if threshold is None:
            final_label = original_label

        elif original_label == "neutral":
            final_label = "neutral"

        elif confidence < threshold:
            final_label = "neutral"

        else:
            final_label = original_label

        predictions.append(
            final_label
        )

    return pd.Series(
        predictions,
        index=dataframe.index,
    )


# ============================================================
# KIÉRTÉKELÉS
# ============================================================

def evaluate_threshold(
    dataframe: pd.DataFrame,
    prediction_column: str,
    threshold: float | None,
):
    """
    Egy threshold-konfiguráció kiértékelése.
    """

    y_true = dataframe["manual_label"]
    y_pred = dataframe[prediction_column]

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        output_dict=True,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    threshold_name = (
        "none"
        if threshold is None
        else f"{threshold:.2f}"
    )

    result = {
        "threshold": threshold_name,
        "accuracy": accuracy,
        "macro_precision": (
            report["macro avg"]["precision"]
        ),
        "macro_recall": (
            report["macro avg"]["recall"]
        ),
        "macro_f1": (
            report["macro avg"]["f1-score"]
        ),
        "negative_precision": (
            report["negative"]["precision"]
        ),
        "negative_recall": (
            report["negative"]["recall"]
        ),
        "negative_f1": (
            report["negative"]["f1-score"]
        ),
        "neutral_precision": (
            report["neutral"]["precision"]
        ),
        "neutral_recall": (
            report["neutral"]["recall"]
        ),
        "neutral_f1": (
            report["neutral"]["f1-score"]
        ),
        "positive_precision": (
            report["positive"]["precision"]
        ),
        "positive_recall": (
            report["positive"]["recall"]
        ),
        "positive_f1": (
            report["positive"]["f1-score"]
        ),
    }

    return result, report, matrix


# ============================================================
# FŐPROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("CONFIDENCE THRESHOLD ANALYSIS")
    print("=" * 70)

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Validation adatok
    # --------------------------------------------------------

    print("\nValidation adatok betöltése...")

    comments_df = load_validation_dataset(
        VALIDATION_COMMENTS_PATH
    )

    post_context_df = load_post_context_csv(
        VALIDATION_POST_CONTEXT_PATH
    )

    validation_df = merge_comments_with_post_context(
        comments_df,
        post_context_df,
    )

    print(
        f"Validation rekordok száma: "
        f"{len(validation_df)}"
    )

    print("\nKézi címkék eloszlása:")

    print(
        validation_df["manual_label"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Modellpredikciók
    # --------------------------------------------------------

    validation_df = create_predictions(
        validation_df
    )

    # --------------------------------------------------------
    # Threshold vizsgálat
    # --------------------------------------------------------

    results = []

    print("\n" + "=" * 70)
    print("THRESHOLD EREDMÉNYEK")
    print("=" * 70)

    for threshold in THRESHOLDS:

        threshold_name = (
            "none"
            if threshold is None
            else f"{threshold:.2f}"
        )

        column_name = (
            "prediction_"
            + threshold_name.replace(".", "_")
        )

        validation_df[column_name] = (
            apply_threshold(
                validation_df,
                threshold,
            )
        )

        (
            metrics,
            report,
            matrix,
        ) = evaluate_threshold(
            validation_df,
            column_name,
            threshold,
        )

        results.append(metrics)

        print(
            f"\nThreshold: "
            f"{threshold_name}"
        )

        print(
            f"Accuracy:        "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Macro Precision: "
            f"{metrics['macro_precision']:.4f}"
        )

        print(
            f"Macro Recall:    "
            f"{metrics['macro_recall']:.4f}"
        )

        print(
            f"Macro F1:        "
            f"{metrics['macro_f1']:.4f}"
        )

        print(
            f"Neutral Recall:  "
            f"{metrics['neutral_recall']:.4f}"
        )

        print(
            f"Neutral F1:      "
            f"{metrics['neutral_f1']:.4f}"
        )

        # Confusion matrix mentése minden thresholdhoz.
        matrix_df = pd.DataFrame(
            matrix,
            index=LABELS,
            columns=LABELS,
        )

        matrix_df.to_csv(
            OUTPUT_DIRECTORY
            / (
                "confusion_matrix_"
                f"{threshold_name.replace('.', '_')}.csv"
            ),
            encoding="utf-8-sig",
        )

    # --------------------------------------------------------
    # Összesítés
    # --------------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    print("\n" + "=" * 70)
    print("ÖSSZESÍTETT THRESHOLD ÖSSZEHASONLÍTÁS")
    print("=" * 70)

    print(
        results_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Legjobb Macro F1
    # --------------------------------------------------------

    best_index = (
        results_df["macro_f1"]
        .idxmax()
    )

    best_result = (
        results_df.loc[best_index]
    )

    print("\n" + "=" * 70)
    print("LEGJOBB VALIDÁCIÓS KONFIGURÁCIÓ")
    print("=" * 70)

    print(
        f"Threshold: "
        f"{best_result['threshold']}"
    )

    print(
        f"Accuracy: "
        f"{best_result['accuracy']:.4f}"
    )

    print(
        f"Macro F1: "
        f"{best_result['macro_f1']:.4f}"
    )

    print(
        f"Neutral Recall: "
        f"{best_result['neutral_recall']:.4f}"
    )

    print(
        f"Neutral F1: "
        f"{best_result['neutral_f1']:.4f}"
    )

    # --------------------------------------------------------
    # Export
    # --------------------------------------------------------

    results_df.to_csv(
        OUTPUT_DIRECTORY
        / "threshold_comparison.csv",
        index=False,
        encoding="utf-8-sig",
    )

    validation_df.to_csv(
        OUTPUT_DIRECTORY
        / "validation_threshold_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("\nEredmények mentési helye:")
    print(OUTPUT_DIRECTORY)


if __name__ == "__main__":
    main()
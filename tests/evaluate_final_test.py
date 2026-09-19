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

from preprocessing.text_preprocessor import (
    preprocess_text_fields,
    clean_text,
)

from sentiment.hubert_sentiment_analyzer import (
    HuBERTSentimentAnalyzer,
)


# ============================================================
# KONFIGURÁCIÓ
# ============================================================

TEST_COMMENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "test_comments.csv"
)

TEST_POST_CONTEXT_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "test_post_context.csv"
)

FINE_TUNED_MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "context_aware_hubert_text"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation"
    / "final_test"
)

MAX_LENGTH = 128

# A validation halmazon kiválasztott confidence threshold.
#
# Szabály:
# - positive vagy negative predikció esetén,
# - ha a confidence kisebb 0.60-nél,
# - a végső címke neutral lesz.
CONFIDENCE_THRESHOLD = 0.60

LABELS = [
    "negative",
    "neutral",
    "positive",
]


# ============================================================
# BASELINE MODELL
# ============================================================

def predict_baseline(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Predikció a rendszer eredeti baseline huBERT modelljével.

    Fontos:
    - csak a komment szövegét használja;
    - ugyanazt az előfeldolgozást használja, mint
      az eredeti analysis pipeline;
    - ugyanazt az 5 -> 3 osztályleképezést használja,
      mint a HuBERTSentimentAnalyzer;
    - a baseline modellre nem alkalmazunk confidence
      threshold utófeldolgozást.
    """

    print("\nBaseline huBERT modell betöltése...")

    analyzer = HuBERTSentimentAnalyzer()

    # Pontosan ugyanaz az előfeldolgozás,
    # mint az eredeti analysis_pipeline.py fájlban.
    #
    # Itt szándékosan nem adjuk meg az emoji_mode
    # paramétert, így a baseline az eredeti
    # alapértelmezett feldolgozást használja.
    baseline_df = preprocess_text_fields(
        dataframe.copy()
    )

    predicted_labels = []
    confidence_scores = []

    total = len(baseline_df)

    print(
        f"Baseline predikciók készítése: "
        f"{total} rekord"
    )

    for position, (_, row) in enumerate(
        baseline_df.iterrows(),
        start=1,
    ):
        comment_text = row["cleaned_comment_text"]

        result = analyzer.predict(
            comment_text
        )

        predicted_labels.append(
            result.label
        )

        confidence_scores.append(
            result.confidence
        )

        if position % 25 == 0 or position == total:
            print(
                f"  Baseline: "
                f"{position}/{total}"
            )

    result_df = dataframe.copy()

    result_df["baseline_label"] = (
        predicted_labels
    )

    result_df["baseline_confidence"] = (
        confidence_scores
    )

    return result_df


# ============================================================
# FINE-TUNED MODELL
# ============================================================

def predict_finetuned(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Predikció a context-aware fine-tuned modellel.

    A modell bemenete:
        post_text + comment_text

    Az előfeldolgozás megegyezik a tanítás során
    használt emoji_mode='text' konfigurációval.

    A függvény az eredeti, threshold nélküli
    predikciót adja vissza. A confidence threshold
    külön utófeldolgozási lépésben kerül alkalmazásra.
    """

    print("\nFine-tuned modell betöltése...")

    tokenizer = AutoTokenizer.from_pretrained(
        FINE_TUNED_MODEL_DIRECTORY
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            FINE_TUNED_MODEL_DIRECTORY
        )
    )

    model.eval()

    predicted_labels = []
    confidence_scores = []

    total = len(dataframe)

    print(
        f"Fine-tuned predikciók készítése: "
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

        if position % 25 == 0 or position == total:
            print(
                f"  Fine-tuned: "
                f"{position}/{total}"
            )

    result_df = dataframe.copy()

    result_df["finetuned_label"] = (
        predicted_labels
    )

    result_df["finetuned_confidence"] = (
        confidence_scores
    )

    return result_df


# ============================================================
# CONFIDENCE THRESHOLD UTÓFELDOLGOZÁS
# ============================================================

def apply_confidence_threshold(
    dataframe: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """
    Confidence threshold alkalmazása a fine-tuned modell
    predikcióira.

    Döntési szabály:
    - ha a modell positive vagy negative címkét ad,
      és a hozzá tartozó confidence kisebb a megadott
      küszöbértéknél, akkor a végső címke neutral;
    - a neutral predikció változatlan marad;
    - a küszöböt elérő vagy meghaladó positive/negative
      predikció szintén változatlan marad.

    A függvény nem írja felül az eredeti finetuned_label
    oszlopot. A threshold utáni eredmény külön
    finetuned_threshold_label oszlopba kerül.
    """

    print(
        "\nConfidence threshold alkalmazása: "
        f"{threshold:.2f}"
    )

    result_df = dataframe.copy()

    threshold_labels = []
    changed_count = 0

    for _, row in result_df.iterrows():

        predicted_label = row[
            "finetuned_label"
        ]

        confidence = float(
            row["finetuned_confidence"]
        )

        if (
            predicted_label
            in {"positive", "negative"}
            and confidence < threshold
        ):
            final_label = "neutral"
            changed_count += 1

        else:
            final_label = predicted_label

        threshold_labels.append(
            final_label
        )

    result_df[
        "finetuned_threshold_label"
    ] = threshold_labels

    print(
        "Threshold miatt neutral címkére "
        f"módosított predikciók: {changed_count}"
    )

    return result_df


# ============================================================
# KIÉRTÉKELÉS
# ============================================================

def evaluate_model(
    dataframe: pd.DataFrame,
    prediction_column: str,
    model_name: str,
):
    """
    A megadott predikciós oszlop kiértékelése
    a kézi címkék alapján.

    Kiszámított metrikák:
    - accuracy
    - macro precision
    - macro recall
    - macro F1
    - osztályonkénti precision / recall / F1
    - confusion matrix
    """

    y_true = dataframe[
        "manual_label"
    ]

    y_pred = dataframe[
        prediction_column
    ]

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

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    print(
        f"Accuracy:        "
        f"{accuracy:.4f}"
    )

    print(
        f"Macro Precision: "
        f"{report['macro avg']['precision']:.4f}"
    )

    print(
        f"Macro Recall:    "
        f"{report['macro avg']['recall']:.4f}"
    )

    print(
        f"Macro F1:        "
        f"{report['macro avg']['f1-score']:.4f}"
    )

    print(
        "\nOsztályonkénti eredmények:"
    )

    for label in LABELS:

        values = report[label]

        print(
            f"{label:>8} | "
            f"P={values['precision']:.4f} | "
            f"R={values['recall']:.4f} | "
            f"F1={values['f1-score']:.4f} | "
            f"support={int(values['support'])}"
        )

    print("\nConfusion matrix:")
    print("Sorok: valós címke")
    print("Oszlopok: predikció")
    print(
        f"Label sorrend: {LABELS}"
    )
    print(matrix)

    metrics = {
        "model": model_name,
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
    }

    return metrics, report, matrix


# ============================================================
# FŐPROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("FINAL TEST EVALUATION")
    print("=" * 70)

    print(
        f"\nFine-tuned confidence threshold: "
        f"{CONFIDENCE_THRESHOLD:.2f}"
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Testhalmaz betöltése
    # --------------------------------------------------------

    print("\nTest adatok betöltése...")

    comments_df = load_validation_dataset(
        TEST_COMMENTS_PATH
    )

    post_context_df = load_post_context_csv(
        TEST_POST_CONTEXT_PATH
    )

    test_df = merge_comments_with_post_context(
        comments_df,
        post_context_df,
    )

    print(
        f"Test rekordok száma: "
        f"{len(test_df)}"
    )

    print("\nKézi címkék eloszlása:")

    print(
        test_df["manual_label"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # Baseline predikció
    # --------------------------------------------------------

    test_df = predict_baseline(
        test_df
    )

    # --------------------------------------------------------
    # Fine-tuned predikció
    # --------------------------------------------------------

    test_df = predict_finetuned(
        test_df
    )

    # --------------------------------------------------------
    # Confidence threshold alkalmazása
    # --------------------------------------------------------

    test_df = apply_confidence_threshold(
        test_df,
        threshold=CONFIDENCE_THRESHOLD,
    )

    # --------------------------------------------------------
    # Helyességi jelzők
    # --------------------------------------------------------

    test_df["baseline_correct"] = (
        test_df["baseline_label"]
        == test_df["manual_label"]
    )

    test_df["finetuned_correct"] = (
        test_df["finetuned_label"]
        == test_df["manual_label"]
    )

    test_df[
        "finetuned_threshold_correct"
    ] = (
        test_df["finetuned_threshold_label"]
        == test_df["manual_label"]
    )

    # --------------------------------------------------------
    # Fine-tuning hatása a baseline-hoz képest
    # threshold nélkül
    # --------------------------------------------------------

    test_df["finetuned_improved"] = (
        (~test_df["baseline_correct"])
        & test_df["finetuned_correct"]
    )

    test_df["finetuned_worsened"] = (
        test_df["baseline_correct"]
        & (~test_df["finetuned_correct"])
    )

    # --------------------------------------------------------
    # Thresholdos változat hatása a baseline-hoz képest
    # --------------------------------------------------------

    test_df[
        "threshold_improved_vs_baseline"
    ] = (
        (~test_df["baseline_correct"])
        & test_df["finetuned_threshold_correct"]
    )

    test_df[
        "threshold_worsened_vs_baseline"
    ] = (
        test_df["baseline_correct"]
        & (~test_df["finetuned_threshold_correct"])
    )

    # --------------------------------------------------------
    # Threshold közvetlen hatása a fine-tuned modellre
    # --------------------------------------------------------

    test_df[
        "threshold_improved_vs_finetuned"
    ] = (
        (~test_df["finetuned_correct"])
        & test_df["finetuned_threshold_correct"]
    )

    test_df[
        "threshold_worsened_vs_finetuned"
    ] = (
        test_df["finetuned_correct"]
        & (~test_df["finetuned_threshold_correct"])
    )

    # --------------------------------------------------------
    # Baseline kiértékelése
    # --------------------------------------------------------

    (
        baseline_metrics,
        baseline_report,
        baseline_matrix,
    ) = evaluate_model(
        test_df,
        prediction_column="baseline_label",
        model_name="BASELINE HUBERT",
    )

    # --------------------------------------------------------
    # Fine-tuned modell kiértékelése
    # threshold nélkül
    # --------------------------------------------------------

    (
        finetuned_metrics,
        finetuned_report,
        finetuned_matrix,
    ) = evaluate_model(
        test_df,
        prediction_column="finetuned_label",
        model_name=(
            "CONTEXT-AWARE FINE-TUNED HUBERT"
        ),
    )

    # --------------------------------------------------------
    # Fine-tuned modell + threshold kiértékelése
    # --------------------------------------------------------

    (
        finetuned_threshold_metrics,
        finetuned_threshold_report,
        finetuned_threshold_matrix,
    ) = evaluate_model(
        test_df,
        prediction_column=(
            "finetuned_threshold_label"
        ),
       model_name=(
            "CONTEXT-AWARE FINE-TUNED HUBERT "
            f"+ CONFIDENCE THRESHOLD {CONFIDENCE_THRESHOLD:.2f}"
        ),
    )

    # --------------------------------------------------------
    # Modell-összehasonlítás
    # --------------------------------------------------------

    comparison_df = pd.DataFrame(
        [
            baseline_metrics,
            finetuned_metrics,
            finetuned_threshold_metrics,
        ]
    )

    print("\n" + "=" * 70)
    print("MODELL-ÖSSZEHASONLÍTÁS")
    print("=" * 70)

    print(
        comparison_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Fine-tuning változásai a baseline-hoz képest
    # --------------------------------------------------------

    improved_count = int(
        test_df[
            "finetuned_improved"
        ].sum()
    )

    worsened_count = int(
        test_df[
            "finetuned_worsened"
        ].sum()
    )

    print("\n" + "-" * 70)

    print(
        "FINE-TUNING HATÁSA A BASELINE-HOZ KÉPEST"
    )

    print("-" * 70)

    print(
        f"Javított esetek: "
        f"{improved_count}"
    )

    print(
        f"Rontott esetek: "
        f"{worsened_count}"
    )

    print(
        f"Nettó változás: "
        f"{improved_count - worsened_count}"
    )

    # --------------------------------------------------------
    # Thresholdos rendszer változásai a baseline-hoz képest
    # --------------------------------------------------------

    threshold_improved_baseline_count = int(
        test_df[
            "threshold_improved_vs_baseline"
        ].sum()
    )

    threshold_worsened_baseline_count = int(
        test_df[
            "threshold_worsened_vs_baseline"
        ].sum()
    )

    print("\n" + "-" * 70)

    print(
        "FINE-TUNED + THRESHOLD HATÁSA "
        "A BASELINE-HOZ KÉPEST"
    )

    print("-" * 70)

    print(
        f"Javított esetek: "
        f"{threshold_improved_baseline_count}"
    )

    print(
        f"Rontott esetek: "
        f"{threshold_worsened_baseline_count}"
    )

    print(
        f"Nettó változás: "
        f"{threshold_improved_baseline_count - threshold_worsened_baseline_count}"
    )

    # --------------------------------------------------------
    # Threshold közvetlen hatása
    # --------------------------------------------------------

    threshold_improved_count = int(
        test_df[
            "threshold_improved_vs_finetuned"
        ].sum()
    )

    threshold_worsened_count = int(
        test_df[
            "threshold_worsened_vs_finetuned"
        ].sum()
    )

    changed_by_threshold_count = int(
        (
            test_df["finetuned_label"]
            != test_df["finetuned_threshold_label"]
        ).sum()
    )

    print("\n" + "-" * 70)

    print(
        "CONFIDENCE THRESHOLD KÖZVETLEN HATÁSA"
    )

    print("-" * 70)

    print(
        f"Threshold által módosított predikciók: "
        f"{changed_by_threshold_count}"
    )

    print(
        f"Threshold által javított esetek: "
        f"{threshold_improved_count}"
    )

    print(
        f"Threshold által rontott esetek: "
        f"{threshold_worsened_count}"
    )

    print(
        f"Threshold nettó változás: "
        f"{threshold_improved_count - threshold_worsened_count}"
    )

    # --------------------------------------------------------
    # Export: teljes predikciós adathalmaz
    # --------------------------------------------------------

    test_df.to_csv(
        OUTPUT_DIRECTORY
        / "test_predictions.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Export: modell-összehasonlítás
    # --------------------------------------------------------

    comparison_df.to_csv(
        OUTPUT_DIRECTORY
        / "model_comparison.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Export: classification reportok
    # --------------------------------------------------------

    pd.DataFrame(
        baseline_report
    ).transpose().to_csv(
        OUTPUT_DIRECTORY
        / "baseline_classification_report.csv",
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        finetuned_report
    ).transpose().to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_classification_report.csv",
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        finetuned_threshold_report
    ).transpose().to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_threshold_classification_report.csv",
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Export: confusion matrixok
    # --------------------------------------------------------

    pd.DataFrame(
        baseline_matrix,
        index=LABELS,
        columns=LABELS,
    ).to_csv(
        OUTPUT_DIRECTORY
        / "baseline_confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        finetuned_matrix,
        index=LABELS,
        columns=LABELS,
    ).to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    pd.DataFrame(
        finetuned_threshold_matrix,
        index=LABELS,
        columns=LABELS,
    ).to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_threshold_confusion_matrix.csv",
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Export: fine-tuning által javított / rontott esetek
    # --------------------------------------------------------

    test_df[
        test_df["finetuned_improved"]
    ].to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_improved_cases.csv",
        index=False,
        encoding="utf-8-sig",
    )

    test_df[
        test_df["finetuned_worsened"]
    ].to_csv(
        OUTPUT_DIRECTORY
        / "finetuned_worsened_cases.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Export: threshold közvetlen hatása
    # --------------------------------------------------------

    test_df[
        test_df[
            "threshold_improved_vs_finetuned"
        ]
    ].to_csv(
        OUTPUT_DIRECTORY
        / "threshold_improved_cases.csv",
        index=False,
        encoding="utf-8-sig",
    )

    test_df[
        test_df[
            "threshold_worsened_vs_finetuned"
        ]
    ].to_csv(
        OUTPUT_DIRECTORY
        / "threshold_worsened_cases.csv",
        index=False,
        encoding="utf-8-sig",
    )

    test_df[
        test_df["finetuned_label"]
        != test_df["finetuned_threshold_label"]
    ].to_csv(
        OUTPUT_DIRECTORY
        / "threshold_changed_cases.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # Befejezés
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL TEST EVALUATION BEFEJEZŐDÖTT")
    print("=" * 70)

    print("\nEredmények mentési helye:")
    print(OUTPUT_DIRECTORY)


if __name__ == "__main__":
    main()
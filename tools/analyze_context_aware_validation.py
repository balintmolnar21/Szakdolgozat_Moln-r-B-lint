import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Projekt elérési utak
# ----------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


# ----------------------------------------------------------------------
# Saját modulok
# ----------------------------------------------------------------------

from data_input.csv_loader import (
    load_labeled_comments_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)

from preprocessing.text_preprocessor import (
    preprocess_text_fields,
)

from evaluation.context_aware_error_analysis import (
    load_fine_tuned_model,
    predict_validation_dataframe,
    create_error_analysis,
    export_error_analysis,
)


# ----------------------------------------------------------------------
# Elérési utak
# ----------------------------------------------------------------------

DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validation"
)

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models\context_aware_hubert_text"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation"
    / "context_aware_validation"
)


VALIDATION_COMMENTS_PATH = (
    DATA_DIRECTORY
    / "validation_comments.csv"
)

VALIDATION_POST_CONTEXT_PATH = (
    DATA_DIRECTORY
    / "validation_post_context.csv"
)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():

    print("=" * 70)
    print("CONTEXT-AWARE HUBERT - VALIDATION HIBAANALÍZIS")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Validation adatok betöltése
    # ------------------------------------------------------------------

    print("\nValidation kommentek betöltése...")

    comments_dataframe = load_labeled_comments_dataset(
        VALIDATION_COMMENTS_PATH
    )

    print(
        f"Kommentek száma: {len(comments_dataframe)}"
    )

    print("\nPosztkontextus betöltése...")

    post_context_dataframe = load_post_context_csv(
        VALIDATION_POST_CONTEXT_PATH
    )

    # ------------------------------------------------------------------
    # 2. Komment + poszt kontextus összekapcsolása
    # ------------------------------------------------------------------

    print("\nKommentek és posztok összekapcsolása...")

    validation_dataframe = merge_comments_with_post_context(
        comments_dataframe,
        post_context_dataframe,
    )

    print(
        f"Összekapcsolt rekordok: "
        f"{len(validation_dataframe)}"
    )

    # ------------------------------------------------------------------
    # 3. Előfeldolgozás
    # ------------------------------------------------------------------

    print("\nSzövegek előfeldolgozása...")

    validation_dataframe = preprocess_text_fields(
        validation_dataframe,
        emoji_mode="text",
    )

    # A training során a modell ezeket a mezőket kapta.
    validation_dataframe["post_text"] = (
        validation_dataframe["cleaned_post_text"]
    )

    validation_dataframe["comment_text"] = (
        validation_dataframe["cleaned_comment_text"]
    )

    # ------------------------------------------------------------------
    # 4. Fine-tuned modell betöltése
    # ------------------------------------------------------------------

    print("\nFine-tuned modell betöltése...")

    print(
        f"Modell könyvtára:\n{MODEL_DIRECTORY}"
    )

    model, tokenizer, device = (
        load_fine_tuned_model(
            str(MODEL_DIRECTORY)
        )
    )

    print(f"Használt eszköz: {device}")

    # ------------------------------------------------------------------
    # 5. Predikció
    # ------------------------------------------------------------------

    print("\nValidation predikciók készítése...")

    predictions = predict_validation_dataframe(
        dataframe=validation_dataframe,
        model=model,
        tokenizer=tokenizer,
        device=device,
        max_length=128,
    )

    # ------------------------------------------------------------------
    # 6. Hibaanalízis
    # ------------------------------------------------------------------

    print("\nMetrikák számítása...")

    analysis_result = create_error_analysis(
        predictions
    )

    # ------------------------------------------------------------------
    # 7. Konzol eredmények
    # ------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("VALIDATION EREDMÉNYEK")
    print("=" * 70)

    print(
        f"\nAccuracy: "
        f"{analysis_result.accuracy:.4f}"
    )

    print(
        f"Macro F1: "
        f"{analysis_result.macro_f1:.4f}"
    )

    correct_count = int(
        analysis_result.predictions["correct"].sum()
    )

    incorrect_count = len(
        analysis_result.predictions
    ) - correct_count

    print(
        f"\nHelyes predikciók: "
        f"{correct_count}"
    )

    print(
        f"Hibás predikciók: "
        f"{incorrect_count}"
    )

    print("\nOsztályonkénti metrikák:")
    print(
        analysis_result.classification_report.to_string(
            index=False
        )
    )

    print("\nConfusion matrix:")
    print(
        analysis_result.confusion_matrix.to_string()
    )

    # ------------------------------------------------------------------
    # 8. Export
    # ------------------------------------------------------------------

    print("\nEredmények exportálása...")

    excel_path = export_error_analysis(
        result=analysis_result,
        output_directory=str(
            OUTPUT_DIRECTORY
        ),
    )

    print("\nElemzés elkészült.")

    print(
        f"\nExcel eredmény:\n{excel_path}"
    )

    print(
        f"\nHibás kommentek száma: "
        f"{len(analysis_result.misclassified_comments)}"
    )


if __name__ == "__main__":
    main()
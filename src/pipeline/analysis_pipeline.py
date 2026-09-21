from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from data_input.csv_loader import (
    load_validation_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)

from preprocessing.text_preprocessor import (
    preprocess_text_fields,
)

from sentiment.hubert_sentiment_analyzer import (
    HuBERTSentimentAnalyzer,
)

from sentiment.context_aware_sentiment_analyzer import (
    ContextAwareSentimentAnalyzer,
)

from analytics.sentiment_statistics import (
    calculate_post_statistics,
    calculate_overall_statistics,
    export_sentiment_workbook,
)

from context_analysis.context_analyzer import (
    analyze_post_contexts,
)

from visualization.sentiment_visualizer import (
    create_all_sentiment_charts,
)

from reporting.summary_report import (
    create_summary_report,
)

from evaluation.model_evaluator import (
    ModelEvaluationResult,
    evaluate_sentiment_model,
)

from evaluation.evaluation_exporter import (
    export_evaluation_results,
)

from evaluation.evaluation_visualizer import (
    create_classification_metrics_chart,
    create_confusion_matrix_chart,
)


# ---------------------------------------------------------
# Projektútvonalak és modellbeállítások
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONTEXT_AWARE_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "context_aware_hubert_text"
)

CONTEXT_AWARE_MAX_LENGTH = 128

# A végleges alkalmazásban használt operatív küszöbérték.
CONFIDENCE_THRESHOLD = 0.60

# A fine-tuning során használt emoji-reprezentáció.
EMOJI_MODE = "text"


@dataclass
class AnalysisPipelineResult:
    """
    A teljes elemzési pipeline eredményeit összefogó
    adatszerkezet.
    """

    comments_df: pd.DataFrame
    post_context_df: pd.DataFrame
    full_sentiment_df: pd.DataFrame
    post_statistics_df: pd.DataFrame
    overall_statistics_df: pd.DataFrame
    context_analysis_df: pd.DataFrame

    evaluation_result: ModelEvaluationResult
    evaluation_files: dict[str, Path]

    excel_output_file: Path
    chart_files: list[Path]
    report_file: Path


def run_analysis_pipeline(
    validation_file: str | Path,
    post_context_file: str | Path,
    excel_output_file: str | Path,
    charts_output_directory: str | Path,
    reports_output_directory: str | Path,
    evaluation_output_directory: str | Path,
    analyzer: ContextAwareSentimentAnalyzer | None = None,
    limit: int | None = None,
) -> AnalysisPipelineResult:
    """
    A teljes sentiment elemzési pipeline futtatása.

    A kommentek sentimentjét a domain-specifikusan
    finomhangolt context-aware huBERT modell határozza meg.

    A context-aware modell bemenete:

        sequence A = poszt szövege
        sequence B = komment szövege

    A modell három sentiment kategóriát használ:

        negative
        neutral
        positive

    Az alacsony konfidenciájú pozitív és negatív
    predikciókra 0.60 confidence threshold kerül
    alkalmazásra. Ezek a predikciók semleges
    kategóriába kerülnek.

    A poszt önálló sentimentjének meghatározásához
    továbbra is az eredeti baseline huBERT modellt
    használjuk, mivel a szabályalapú kontextuselemző
    modul erre az információra épül.
    """

    # ---------------------------------------------------------
    # 1. Kimeneti útvonalak normalizálása
    # ---------------------------------------------------------

    charts_output_directory = Path(
        charts_output_directory
    )

    reports_output_directory = Path(
        reports_output_directory
    )

    evaluation_output_directory = Path(
        evaluation_output_directory
    )

    # ---------------------------------------------------------
    # 2. Adatok betöltése
    # ---------------------------------------------------------

    comments_df = load_validation_dataset(
        validation_file
    )

    post_context_df = load_post_context_csv(
        post_context_file
    )

    merged_df = merge_comments_with_post_context(
        comments_df,
        post_context_df,
    )

    # ---------------------------------------------------------
    # 3. Szöveges előfeldolgozás
    # ---------------------------------------------------------
    #
    # A fine-tuning során az emojik szöveges
    # reprezentációját használtuk. Inference során
    # ugyanazt az előfeldolgozást kell alkalmazni.
    # ---------------------------------------------------------

    preprocessed_df = preprocess_text_fields(
        merged_df,
        emoji_mode=EMOJI_MODE,
    )

    # ---------------------------------------------------------
    # 4. Context-aware komment sentiment
    # ---------------------------------------------------------

    if analyzer is None:
        analyzer = ContextAwareSentimentAnalyzer(
            model_path=CONTEXT_AWARE_MODEL_PATH,
            max_length=CONTEXT_AWARE_MAX_LENGTH,
            confidence_threshold=CONFIDENCE_THRESHOLD,
        )

    full_sentiment_df = analyzer.analyze_dataframe(
        dataframe=preprocessed_df,
        post_column="cleaned_post_text",
        comment_column="cleaned_comment_text",
        limit=limit,
    )

    # ---------------------------------------------------------
    # 5. Poszt önálló sentimentjének meghatározása
    # ---------------------------------------------------------
    #
    # A komment végleges sentimentjét NEM ez a modell
    # határozza meg.
    #
    # A baseline huBERT itt kizárólag azért szükséges,
    # hogy a szabályalapú context_analyzer számára
    # rendelkezésre álljon a post_sentiment_label.
    # ---------------------------------------------------------

    post_analyzer = HuBERTSentimentAnalyzer(
        max_length=CONTEXT_AWARE_MAX_LENGTH,
    )

    full_sentiment_df = (
        post_analyzer.analyze_dataframe_column(
            df=full_sentiment_df,
            source_column="cleaned_post_text",
            label_column="post_sentiment_label",
            confidence_column="post_sentiment_confidence",
            original_label_column=(
                "post_original_model_label"
            ),
            limit=limit,
        )
    )

    # ---------------------------------------------------------
    # 6. Modellkiértékelés
    # ---------------------------------------------------------
    #
    # A context-aware analyzer az alábbi oszlopokat
    # biztosítja:
    #
    # finetuned_label
    #     A háromosztályos modell nyers predikciója.
    #
    # finetuned_confidence
    #     A nyers predikció konfidenciaértéke.
    #
    # final_sentiment_label
    #     A 0.60 threshold alkalmazása utáni címke.
    #
    # threshold_applied
    #     Jelzi, hogy történt-e átcímkézés.
    #
    # model_label
    #     Kompatibilitási oszlop, amely a végleges,
    #     threshold utáni sentiment címkét tartalmazza.
    #
    # confidence
    #     Kompatibilitási oszlop a meglévő statisztikai
    #     és kiértékelési modulok számára.
    #
    # A model_evaluator confidence_threshold paramétere
    # nem végez újabb sentiment-átcímkézést, hanem az
    # alacsony konfidenciájú esetek azonosítására szolgál.
    # ---------------------------------------------------------

    evaluation_result = evaluate_sentiment_model(
        dataframe=full_sentiment_df,
        manual_label_column="manual_label",
        model_label_column="model_label",
        confidence_column="confidence",
        confidence_threshold=CONFIDENCE_THRESHOLD,
    )

    evaluation_files = export_evaluation_results(
        evaluation_result=evaluation_result,
        output_directory=evaluation_output_directory,
    )

    # ---------------------------------------------------------
    # 7. Statisztikai összesítés
    # ---------------------------------------------------------

    post_statistics_df = calculate_post_statistics(
        full_sentiment_df
    )

    overall_statistics_df = calculate_overall_statistics(
        full_sentiment_df
    )

    # ---------------------------------------------------------
    # 8. Posztonkénti kontextuselemzés
    # ---------------------------------------------------------

    context_analysis_df = analyze_post_contexts(
        post_statistics_df
    )

    # ---------------------------------------------------------
    # 9. Excel export
    # ---------------------------------------------------------

    created_excel_file = export_sentiment_workbook(
        full_dataset_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_file=excel_output_file,
    )

    # ---------------------------------------------------------
    # 10. Sentimentgrafikonok
    # ---------------------------------------------------------

    created_chart_files = create_all_sentiment_charts(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=charts_output_directory,
    )

    # ---------------------------------------------------------
    # 11. Kiértékelési grafikonok
    # ---------------------------------------------------------

    confusion_matrix_chart_file = (
        create_confusion_matrix_chart(
            confusion_matrix_df=(
                evaluation_result.confusion_matrix
            ),
            output_file=(
                charts_output_directory
                / "confusion_matrix.png"
            ),
        )
    )

    created_chart_files.append(
        confusion_matrix_chart_file
    )

    classification_metrics_chart_file = (
        create_classification_metrics_chart(
            metrics_df=evaluation_result.metrics,
            output_file=(
                charts_output_directory
                / "classification_metrics.png"
            ),
        )
    )

    created_chart_files.append(
        classification_metrics_chart_file
    )

    # ---------------------------------------------------------
    # 12. Szöveges összefoglaló riport
    # ---------------------------------------------------------

    created_report_file = create_summary_report(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=reports_output_directory,
    )

    # ---------------------------------------------------------
    # 13. Pipeline eredmény összeállítása
    # ---------------------------------------------------------

    return AnalysisPipelineResult(
        comments_df=comments_df,
        post_context_df=post_context_df,
        full_sentiment_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        evaluation_result=evaluation_result,
        evaluation_files=evaluation_files,
        excel_output_file=created_excel_file,
        chart_files=created_chart_files,
        report_file=created_report_file,
    )
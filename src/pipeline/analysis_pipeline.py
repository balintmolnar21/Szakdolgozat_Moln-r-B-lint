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

# A fine-tuning során alkalmazott emoji-reprezentáció.
EMOJI_MODE = "text"


@dataclass
class AnalysisPipelineResult:
    """
    A teljes elemzési pipeline eredményeit tartalmazó
    adatstruktúra.

    Az evaluation_result Facebook API módban None lehet,
    mivel az API-ból érkező adatokhoz nem tartozik
    ember által megadott referencia-címke.
    """

    comments_df: pd.DataFrame
    post_context_df: pd.DataFrame
    full_sentiment_df: pd.DataFrame
    post_statistics_df: pd.DataFrame
    overall_statistics_df: pd.DataFrame
    context_analysis_df: pd.DataFrame

    evaluation_result: ModelEvaluationResult | None
    evaluation_files: dict[str, Path]

    excel_output_file: Path
    chart_files: list[Path]
    report_file: Path


def _get_labeled_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Visszaadja azokat a rekordokat, amelyekhez rendelkezésre
    áll ember által megadott manual_label.

    Facebook API módban a manual_label mező üres, ezért
    a visszaadott DataFrame is üres lesz.
    """

    if "manual_label" not in dataframe.columns:
        return dataframe.iloc[0:0].copy()

    manual_labels = dataframe[
        "manual_label"
    ]

    valid_label_mask = (
        manual_labels.notna()
        & manual_labels.astype(str).str.strip().ne("")
    )

    return dataframe.loc[
        valid_label_mask
    ].copy()


def run_analysis_pipeline_from_dataframes(
    comments_df: pd.DataFrame,
    post_context_df: pd.DataFrame,
    excel_output_file: str | Path,
    charts_output_directory: str | Path,
    reports_output_directory: str | Path,
    evaluation_output_directory: str | Path | None = None,
    analyzer: ContextAwareSentimentAnalyzer | None = None,
    limit: int | None = None,
) -> AnalysisPipelineResult:
    """
    A központi sentiment elemzési pipeline.

    A függvény már előkészített DataFrame-eket fogad,
    ezért adatforrástól függetlenül használható.

    Használható például:

    - CSV-ből betöltött validációs/test adatokkal,
    - Facebook Graph API-ból előállított adatokkal.

    A modellkiértékelés csak akkor fut le, ha legalább
    egy rekordhoz rendelkezésre áll manual_label.
    """

    # ---------------------------------------------------------
    # 1. Alapvető bemenetellenőrzés
    # ---------------------------------------------------------

    if comments_df is None:
        raise ValueError(
            "A comments_df nem lehet None."
        )

    if post_context_df is None:
        raise ValueError(
            "A post_context_df nem lehet None."
        )

    if comments_df.empty:
        raise ValueError(
            "Nincs feldolgozható komment az elemzéshez."
        )

    if post_context_df.empty:
        raise ValueError(
            "Nincs feldolgozható posztkontextus "
            "az elemzéshez."
        )

    # Másolat készítése azért, hogy a pipeline ne módosítsa
    # a hívó által átadott eredeti DataFrame-eket.
    comments_df = comments_df.copy()
    post_context_df = post_context_df.copy()

    # ---------------------------------------------------------
    # 2. Kimeneti útvonalak normalizálása
    # ---------------------------------------------------------

    excel_output_file = Path(
        excel_output_file
    )

    charts_output_directory = Path(
        charts_output_directory
    )

    reports_output_directory = Path(
        reports_output_directory
    )

    if evaluation_output_directory is not None:
        evaluation_output_directory = Path(
            evaluation_output_directory
        )

    # ---------------------------------------------------------
    # 3. Kommentek és posztkontextus összekapcsolása
    # ---------------------------------------------------------

    merged_df = merge_comments_with_post_context(
        comments_df,
        post_context_df,
    )

    if merged_df.empty:
        raise ValueError(
            "A kommentek és a posztkontextusok "
            "összekapcsolása után nem maradt "
            "feldolgozható rekord."
        )

    # ---------------------------------------------------------
    # 4. Szöveges előfeldolgozás
    # ---------------------------------------------------------
    #
    # A fine-tuning során az emojik szöveges
    # reprezentációját használtuk.
    #
    # Inference során ugyanazt az előfeldolgozást
    # alkalmazzuk.
    # ---------------------------------------------------------

    preprocessed_df = preprocess_text_fields(
        merged_df,
        emoji_mode=EMOJI_MODE,
    )

    # ---------------------------------------------------------
    # 5. Context-aware komment sentiment
    # ---------------------------------------------------------
    #
    # A modell bemenete:
    #
    # cleaned_post_text
    # +
    # cleaned_comment_text
    #
    # Ez Facebook főkommenteknél és reply kommenteknél
    # egyaránt változatlan.
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

    if full_sentiment_df.empty:
        raise ValueError(
            "A sentiment elemzés nem adott vissza "
            "feldolgozott rekordot."
        )

    # ---------------------------------------------------------
    # 6. Poszt önálló sentimentjének meghatározása
    # ---------------------------------------------------------
    #
    # Fontos:
    #
    # a baseline huBERT NEM a komment végleges
    # sentimentjét határozza meg.
    #
    # A modell kizárólag azért szükséges, hogy a
    # szabályalapú context_analyzer számára rendelkezésre
    # álljon a post_sentiment_label.
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
    # 7. Opcionális modellkiértékelés
    # ---------------------------------------------------------
    #
    # CSV validációs/test adatok:
    #
    # manual_label rendelkezésre áll
    # -> evaluation lefut
    #
    # Facebook Graph API:
    #
    # manual_label nincs
    # -> evaluation kimarad
    #
    # Facebook adatokon ezért nem számítunk Accuracy,
    # Precision, Recall, Macro F1 vagy confusion matrix
    # értékeket.
    # ---------------------------------------------------------

    evaluation_result: ModelEvaluationResult | None = None
    evaluation_files: dict[str, Path] = {}

    labeled_df = _get_labeled_dataframe(
        full_sentiment_df
    )

    if not labeled_df.empty:
        evaluation_result = evaluate_sentiment_model(
            dataframe=labeled_df,
            manual_label_column="manual_label",
            model_label_column="model_label",
            confidence_column="confidence",
            confidence_threshold=CONFIDENCE_THRESHOLD,
        )

        if evaluation_output_directory is not None:
            evaluation_files = (
                export_evaluation_results(
                    evaluation_result=evaluation_result,
                    output_directory=(
                        evaluation_output_directory
                    ),
                )
            )

    # ---------------------------------------------------------
    # 8. Statisztikai összesítés
    # ---------------------------------------------------------

    post_statistics_df = calculate_post_statistics(
        full_sentiment_df
    )

    overall_statistics_df = calculate_overall_statistics(
        full_sentiment_df
    )

    # ---------------------------------------------------------
    # 9. Posztonkénti kontextuselemzés
    # ---------------------------------------------------------

    context_analysis_df = analyze_post_contexts(
        post_statistics_df
    )

    # ---------------------------------------------------------
    # 10. Excel export
    # ---------------------------------------------------------

    created_excel_file = export_sentiment_workbook(
        full_dataset_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_file=excel_output_file,
    )

    # ---------------------------------------------------------
    # 11. Általános sentimentgrafikonok
    # ---------------------------------------------------------

    created_chart_files = create_all_sentiment_charts(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=charts_output_directory,
    )

    # ---------------------------------------------------------
    # 12. Kiértékelési grafikonok
    # ---------------------------------------------------------
    #
    # Ezek kizárólag kézzel címkézett adatok esetén
    # értelmezhetők.
    # ---------------------------------------------------------

    if evaluation_result is not None:
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
    # 13. Szöveges összefoglaló riport
    # ---------------------------------------------------------

    created_report_file = create_summary_report(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=reports_output_directory,
    )

    # ---------------------------------------------------------
    # 14. Pipeline eredmény összeállítása
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
    CSV-alapú kompatibilitási belépési pont.

    A korábbi main.py és Streamlit implementáció
    továbbra is ezt a függvényt használhatja.

    A függvény kizárólag:
    1. betölti a CSV-adatokat,
    2. átadja őket a közös DataFrame-alapú pipeline-nak.
    """

    # ---------------------------------------------------------
    # 1. CSV-adatok betöltése
    # ---------------------------------------------------------

    comments_df = load_validation_dataset(
        validation_file
    )

    post_context_df = load_post_context_csv(
        post_context_file
    )

    # ---------------------------------------------------------
    # 2. Közös elemzési pipeline meghívása
    # ---------------------------------------------------------

    return run_analysis_pipeline_from_dataframes(
        comments_df=comments_df,
        post_context_df=post_context_df,
        excel_output_file=excel_output_file,
        charts_output_directory=charts_output_directory,
        reports_output_directory=reports_output_directory,
        evaluation_output_directory=(
            evaluation_output_directory
        ),
        analyzer=analyzer,
        limit=limit,
    )
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from data_input.csv_loader import (
    load_validation_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)
from preprocessing.text_preprocessor import preprocess_text_fields
from sentiment.hubert_sentiment_analyzer import HuBERTSentimentAnalyzer
from analytics.sentiment_statistics import (
    calculate_post_statistics,
    calculate_overall_statistics,
    export_sentiment_workbook,
)
from context_analysis.context_analyzer import analyze_post_contexts
from visualization.sentiment_visualizer import (
    create_all_sentiment_charts,
)
from reporting.summary_report import create_summary_report

from evaluation.model_evaluator import (
    ModelEvaluationResult,
    evaluate_sentiment_model,
)


@dataclass
class AnalysisPipelineResult:
   

    comments_df: pd.DataFrame
    post_context_df: pd.DataFrame
    full_sentiment_df: pd.DataFrame
    post_statistics_df: pd.DataFrame
    overall_statistics_df: pd.DataFrame
    context_analysis_df: pd.DataFrame
    evaluation_result: ModelEvaluationResult
    excel_output_file: Path
    chart_files: list[Path]
    report_file: Path


def run_analysis_pipeline(
    validation_file: str | Path,
    post_context_file: str | Path,
    excel_output_file: str | Path,
    charts_output_directory: str | Path,
    reports_output_directory: str | Path,
    analyzer: HuBERTSentimentAnalyzer | None = None,
    limit: int | None = None,
) -> AnalysisPipelineResult:
    
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

    preprocessed_df = preprocess_text_fields(
        merged_df
    )

    if analyzer is None:
        analyzer = HuBERTSentimentAnalyzer()

    sentiment_analysis_configs = [
        {
            "source_column": "cleaned_comment_text",
            "label_column": "model_label",
            "confidence_column": "confidence",
            "original_label_column": "original_model_label",
        },
        {
            "source_column": "cleaned_post_text",
            "label_column": "post_sentiment_label",
            "confidence_column": "post_sentiment_confidence",
            "original_label_column": "post_original_model_label",
        },
        {
            "source_column": "cleaned_image_context_text",
            "label_column": "image_context_sentiment_label",
            "confidence_column": "image_context_sentiment_confidence",
            "original_label_column": (
                "image_context_original_model_label"
            ),
        },
        {
            "source_column": "cleaned_video_context_text",
            "label_column": "video_context_sentiment_label",
            "confidence_column": "video_context_sentiment_confidence",
            "original_label_column": (
                "video_context_original_model_label"
            ),
        },
    ]

    full_sentiment_df = analyzer.analyze_multiple_dataframe_columns(
            df=preprocessed_df,
            analysis_configs=sentiment_analysis_configs,
            limit=limit,
        )


    #print("A full_sentiment_df oszlopai:")
    #print(full_sentiment_df.columns.tolist())

    evaluation_result = evaluate_sentiment_model(
                dataframe=full_sentiment_df,
                manual_label_column="manual_label",
                model_label_column="model_label",
    )

    post_statistics_df = calculate_post_statistics(
        full_sentiment_df
    )

    overall_statistics_df = calculate_overall_statistics(
        full_sentiment_df
    )

    context_analysis_df = analyze_post_contexts(
        post_statistics_df
    )

    created_excel_file = export_sentiment_workbook(
        full_dataset_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_file=excel_output_file,
    )

    created_chart_files = create_all_sentiment_charts(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=charts_output_directory,
    )

    created_report_file = create_summary_report(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        output_directory=reports_output_directory,
    )

    return AnalysisPipelineResult(
        comments_df=comments_df,
        post_context_df=post_context_df,
        full_sentiment_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
        evaluation_result=evaluation_result,
        excel_output_file=created_excel_file,
        chart_files=created_chart_files,
        report_file=created_report_file,
    )
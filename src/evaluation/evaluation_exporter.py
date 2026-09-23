from pathlib import Path

import pandas as pd

from evaluation.model_evaluator import ModelEvaluationResult


def export_evaluation_results(
    evaluation_result: ModelEvaluationResult,
    output_directory: Path,
) -> dict[str, Path]:
    
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_file = output_directory / "model_metrics.csv"
    confusion_matrix_file = (
        output_directory / "confusion_matrix.csv"
    )
    misclassified_file = (
        output_directory / "misclassified_comments.csv"
    )
    summary_file = (
        output_directory / "evaluation_summary.txt"
    )

    low_confidence_file = (
        output_directory / "low_confidence_comments.csv"
    )

    evaluation_result.metrics.to_csv(
        metrics_file,
        index=False,
        encoding="utf-8-sig",
    )

    evaluation_result.confusion_matrix.to_csv(
        confusion_matrix_file,
        index=True,
        encoding="utf-8-sig",
    )

    evaluation_result.misclassified_comments.to_csv(
        misclassified_file,
        index=False,
        encoding="utf-8-sig",
    )

    evaluation_result.low_confidence_comments.to_csv(
        low_confidence_file,
        index=False,
        encoding="utf-8-sig",
    )

    create_evaluation_summary(
        evaluation_result=evaluation_result,
        output_file=summary_file,
    )

    return{
        "metrics": metrics_file,
        "confusion_matrix": confusion_matrix_file,
        "misclassified_comments": misclassified_file,
        "low_confidence_comments": low_confidence_file,
        "summary": summary_file,
    }


def create_evaluation_summary(
    evaluation_result: ModelEvaluationResult,
    output_file: Path,
) -> None:
    
    evaluated_count = len(
        evaluation_result.evaluated_data
    )

    misclassified_count = len(
        evaluation_result.misclassified_comments
    )

    correct_count = (
        evaluated_count - misclassified_count
    )

    

    summary_lines = [
        "SENTIMENT MODELL KIÉRTÉKELÉSI ÖSSZEFOGLALÓ",
        "=" * 48,
        "",
        f"Kiértékelt kommentek száma: {evaluated_count}",
        f"Helyes predikciók száma: {correct_count}",
        f"Hibás predikciók száma: {misclassified_count}",
        f"Accuracy: {evaluation_result.accuracy:.4f}",
        f"Accuracy százalékosan: "
        f"{evaluation_result.accuracy:.2%}",
        "",
        "OSZTÁLYONKÉNTI MUTATÓK",
        "-" * 48,
    ]

    for _, row in evaluation_result.metrics.iterrows():
        summary_lines.extend(
            [
                f"Kategória: {row['category']}",
                f"  Precision: {row['precision']:.4f}",
                f"  Recall: {row['recall']:.4f}",
                f"  F1-score: {row['f1_score']:.4f}",
                f"  Esetszám: {int(row['support'])}",
                "",
            ]
        )

    output_file.write_text(
        "\n".join(summary_lines),
        encoding="utf-8",
    )

    
from pathlib import Path

from pipeline.analysis_pipeline import run_analysis_pipeline


def main():
    """
    A teljes sentiment elemzési pipeline
    parancssori indítása.
    """

    project_root = Path(__file__).resolve().parent.parent

    test_comments_file = (
        project_root
        / "data"
        / "validation"
        / "test_comments.csv"
    )

    test_post_context_file = (
        project_root
        / "data"
        / "validation"
        / "test_post_context.csv"
    )

    excel_output_file = (
        project_root
        / "data"
        / "processed"
        / "sentiment_analysis_results.xlsx"
    )

    charts_output_directory = (
        project_root
        / "outputs"
        / "charts"
    )

    reports_output_directory = (
        project_root
        / "outputs"
        / "reports"
    )

    evaluation_output_directory = (
        project_root
        / "outputs"
        / "evaluation"
        / "pipeline_test"
    )

    print("=" * 70)
    print("CONTEXT-AWARE SENTIMENT ELEMZÉSI PIPELINE")
    print("=" * 70)

    print("\nPipeline indítása...")

    result = run_analysis_pipeline(
        validation_file=test_comments_file,
        post_context_file=test_post_context_file,
        excel_output_file=excel_output_file,
        charts_output_directory=charts_output_directory,
        reports_output_directory=reports_output_directory,
        evaluation_output_directory=evaluation_output_directory,
        limit=None,
    )

    print("\n" + "=" * 70)
    print("PIPELINE SIKERESEN LEFUTOTT")
    print("=" * 70)

    print(
        f"\nKommentek száma: "
        f"{len(result.comments_df)}"
    )

    print(
        f"Posztkontextusok száma: "
        f"{len(result.post_context_df)}"
    )

    print(
        f"Elemzett kommentek száma: "
        f"{len(result.full_sentiment_df)}"
    )

    print(
        f"Posztonkénti statisztikai sorok száma: "
        f"{len(result.post_statistics_df)}"
    )

    print(
        "\nExcel eredményfájl:"
        f"\n{result.excel_output_file}"
    )

    print(
        "\nSzöveges riport:"
        f"\n{result.report_file}"
    )

    print("\nLétrehozott grafikonok:")

    for chart_file in result.chart_files:
        print(f"- {chart_file}")

    # ---------------------------------------------------------
    # Új context-aware eredmények ellenőrzése
    # ---------------------------------------------------------

    preview_columns = [
        "post_id",
        "comment_id",
        "manual_label",
        "finetuned_label",
        "finetuned_confidence",
        "final_sentiment_label",
        "threshold_applied",
        "model_label",
        "confidence",
        "post_sentiment_label",
    ]

    available_columns = [
        column
        for column in preview_columns
        if column in result.full_sentiment_df.columns
    ]

    print(
        "\nAz új context-aware sentiment eredmények "
        "első 10 rekordja:"
    )

    print(
        result.full_sentiment_df[
            available_columns
        ].head(10).to_string(index=False)
    )

    print(
        "\nThreshold által módosított predikciók száma:"
    )

    if "threshold_applied" in result.full_sentiment_df.columns:
        threshold_count = int(
            result.full_sentiment_df[
                "threshold_applied"
            ].fillna(False).sum()
        )

        print(threshold_count)
    else:
        print(
            "A threshold_applied oszlop nem található."
        )


if __name__ == "__main__":
    main()
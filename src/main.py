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


def main():
    validation_file = "data/validation/validacios_teszthalmaz.csv"
    post_context_file = "data/validation/post_context.csv"

    output_file = "data/processed/sentiment_analysis_results.xlsx"

    print("Validációs kommentadatok beolvasása...")
    comments_df = load_validation_dataset(validation_file)

    print("Posztkontextus-adatok beolvasása...")
    post_context_df = load_post_context_csv(post_context_file)

    print("Kommentek és posztkontextus összekapcsolása...")
    merged_df = merge_comments_with_post_context(
        comments_df,
        post_context_df,
    )

    print("Szöveg-előfeldolgozás futtatása...")
    preprocessed_df = preprocess_text_fields(merged_df)

    print("huBERT sentiment modell betöltése...")
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
            "original_label_column": "image_context_original_model_label",
        },
        {
            "source_column": "cleaned_video_context_text",
            "label_column": "video_context_sentiment_label",
            "confidence_column": "video_context_sentiment_confidence",
            "original_label_column": "video_context_original_model_label",
        },
    ]

    print(
        "Kommentek, posztszövegek, képi kontextusok és videós leiratok "
        "sentiment elemzése..."
    )

    full_sentiment_df = analyzer.analyze_multiple_dataframe_columns(
        df=preprocessed_df,
        analysis_configs=sentiment_analysis_configs,
        # limit=10,  # teszteléshez használható
        limit=None,
    )

    print("Posztonkénti statisztikák számítása...")
    post_statistics_df = calculate_post_statistics(
        full_sentiment_df
    )

    print("Teljes adathalmaz statisztikáinak számítása...")
    overall_statistics_df = calculate_overall_statistics(
        full_sentiment_df
    )

    print("Három munkalapos Excel-fájl létrehozása...")
    created_output_file = export_sentiment_workbook(
        full_dataset_df=full_sentiment_df,
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        output_file=output_file,
    )

    print(
        "Kommentek és posztkontextus sikeresen beolvasva, "
        "összekapcsolva, előfeldolgozva, elemezve és összesítve."
    )
    print(f"Kommentek száma: {len(comments_df)}")
    print(f"Posztkontextusok száma: {len(post_context_df)}")
    print(f"Összekapcsolt adatsorok száma: {len(merged_df)}")
    print(f"Előfeldolgozott adatsorok száma: {len(preprocessed_df)}")
    print(f"Teljes sentiment adatsorok száma: {len(full_sentiment_df)}")
    print(
        f"Posztonkénti statisztikai sorok száma: "
        f"{len(post_statistics_df)}"
    )
    print(
        f"Teljes adathalmaz statisztikai sorainak száma: "
        f"{len(overall_statistics_df)}"
    )
    print(
        "\nAz egységes, három munkalapos sentiment eredményfájl "
        f"mentve ide: {created_output_file}"
    )

    full_dataset_preview_columns = [
        "post_id",
        "post_type",
        "post_sentiment_label",
        "post_sentiment_confidence",
        "image_context_sentiment_label",
        "image_context_sentiment_confidence",
        "video_context_sentiment_label",
        "video_context_sentiment_confidence",
        "comment_id",
        "manual_label",
        "model_label",
        "confidence",
        "original_model_label",
    ]

    available_full_dataset_preview_columns = [
        column
        for column in full_dataset_preview_columns
        if column in full_sentiment_df.columns
    ]

    post_statistics_preview_columns = [
        "post_id",
        "post_type",
        "comment_count",
        "positive_count",
        "negative_count",
        "neutral_count",
        "positive_ratio",
        "negative_ratio",
        "neutral_ratio",
        "dominant_comment_sentiment",
        "average_comment_confidence",
    ]

    available_post_statistics_preview_columns = [
        column
        for column in post_statistics_preview_columns
        if column in post_statistics_df.columns
    ]

    print("\nA teljes sentiment adathalmaz első 10 rekordja:")
    print(
        full_sentiment_df[
            available_full_dataset_preview_columns
        ].head(10)
    )

    print("\nPosztonkénti statisztikák:")
    print(
        post_statistics_df[
            available_post_statistics_preview_columns
        ]
    )

    print("\nTeljes adathalmaz statisztikája:")
    print(overall_statistics_df)


if __name__ == "__main__":
    main()
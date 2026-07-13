from data_input.csv_loader import (
    load_validation_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)

from preprocessing.text_preprocessor import preprocess_text_fields
from sentiment.hubert_sentiment_analyzer import HuBERTSentimentAnalyzer


def main():
    validation_file = "data/validation/validacios_teszthalmaz.csv"
    post_context_file = "data/validation/post_context.csv"

    output_file = "data/processed/full_sentiment_analysis.xlsx"

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
        # limit=10,  # teszteléshez használható; teljes futtatáshoz legyen None
        limit=None,
    )

    full_sentiment_df.to_excel(output_file, index=False)

    print("Kommentek és posztkontextus sikeresen beolvasva, összekapcsolva, előfeldolgozva és elemezve.")
    print(f"Kommentek száma: {len(comments_df)}")
    print(f"Posztkontextusok száma: {len(post_context_df)}")
    print(f"Összekapcsolt adatsorok száma: {len(merged_df)}")
    print(f"Előfeldolgozott adatsorok száma: {len(preprocessed_df)}")
    print(f"Teljes sentiment adatsorok száma: {len(full_sentiment_df)}")
    print(f"\nAz egységes sentiment elemzési adatbázis mentve ide: {output_file}")

    preview_columns = [
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

    available_preview_columns = [
        column for column in preview_columns
        if column in full_sentiment_df.columns
    ]

    print("\nElső 10 elemzett rekord:")
    print(full_sentiment_df[available_preview_columns].head(10))


if __name__ == "__main__":
    main()
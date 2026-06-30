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

    comments_df = load_validation_dataset(validation_file)
    post_context_df = load_post_context_csv(post_context_file)

    merged_df = merge_comments_with_post_context(comments_df, post_context_df)

    preprocessed_df = preprocess_text_fields(merged_df)
    
    analyzer = HuBERTSentimentAnalyzer()

    sentiment_df = analyzer.analyze_dataframe_column(
        df=preprocessed_df,
        source_column="cleaned_comment_text",
        label_column="model_label",
        confidence_column="confidence",
        original_label_column="original_model_label",
        #limit=10, # először csak az első 10 rekordot dolgozzuk fel a teszteléshez, később eltávolítható a limit
        limit=None,
    )

    #output_file = "data/processed/comment_sentiment_test.xlsx"
    output_file = "data/processed/comment_sentiment.xlsx"
    sentiment_df.to_excel(output_file, index=False)

    print("Kommentek és posztkontextus sikeresen beolvasva, összekapcsolva és előfeldolgozva.")
    print(f"Kommentek száma: {len(comments_df)}")
    print(f"Posztkontextusok száma: {len(post_context_df)}")
    print(f"Összekapcsolt adatsorok száma: {len(merged_df)}")
    print(f"Előfeldolgozott adatsorok száma: {len(preprocessed_df)}")
    #print(f"\nAz előfeldolgozott adathalmaz mentve ide: {output_file}")
    print(f"\nA sentiment teszteredmény mentve ide: {output_file}")

    '''
    print("\nElőfeldolgozott oszlopok:")
    print(preprocessed_df.columns.tolist())
    
    print("\nElső 5 előfeldolgozott rekord:")
    print(
        preprocessed_df[
            [
                "post_id",
                "post_type",
                "comment_text",
                "cleaned_comment_text",
                "post_text",
                "cleaned_post_text",
                "image_context_text",
                "cleaned_image_context_text",
                "video_context_text",
                "cleaned_video_context_text",
                "manual_label",
            ]
        ].head()
    )
    '''


if __name__ == "__main__":
    main()
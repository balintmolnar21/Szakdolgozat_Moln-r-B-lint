from data_input.csv_loader import (
    load_validation_dataset,
    load_post_context_csv,
    merge_comments_with_post_context,
)


def main():
    validation_file = "data/validation/validacios_teszthalmaz.csv"
    post_context_file = "data/validation/post_context.csv"

    comments_df = load_validation_dataset(validation_file)
    post_context_df = load_post_context_csv(post_context_file)

    merged_df = merge_comments_with_post_context(comments_df, post_context_df)
    '''Ellenőrzés miatt adatok exportálása'''
    output_file = "data/processed/merged_validation_dataset.xlsx"
    merged_df.to_excel(output_file, index=False)

    print("Kommentek és posztkontextus sikeresen beolvasva és összekapcsolva.")
    print(f"Kommentek száma: {len(comments_df)}")
    print(f"Posztkontextusok száma: {len(post_context_df)}")
    print(f"Összekapcsolt adatsorok száma: {len(merged_df)}")
    print(f"\nAz összekapcsolt adathalmaz mentve ide: {output_file}")

    print("\nÖsszekapcsolt oszlopok:")
    print(merged_df.columns.tolist())

    print("\nElső 5 összekapcsolt rekord:")
    print(
        merged_df[
            [
                "post_id",
                "post_type",
                "post_text",
                "image_context_text",
                "video_context_text",
                "comment_id",
                "comment_text",
                "manual_label",
            ]
        ].head()
    )


if __name__ == "__main__":
    main()
from data_input.csv_loader import load_validation_dataset


def main():
    input_file = "data/validation/validacios_teszthalmaz.csv"

    validation_df = load_validation_dataset(input_file)

    print("Validációs teszthalmaz sikeresen beolvasva.")
    print(f"Beolvasott kommentek száma: {len(validation_df)}")

    print("\nEgységesített oszlopok:")
    print(validation_df.columns.tolist())

    print("\nElső 5 komment:")
    print(validation_df[["comment_id", "comment_text", "manual_label"]].head())


if __name__ == "__main__":
    main()
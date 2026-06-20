from pathlib import Path
import pandas as pd


def main():
    input_file = Path("data/validation/validacios_teszthalmaz.xlsx")
    output_file = Path("data/validation/validacios_teszthalmaz.csv")

    df = pd.read_excel(input_file, engine="openpyxl")

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
        sep=",",
    )

    print(f"Sikeres konvertálás: {output_file}")
    print(f"Sorok száma: {len(df)}")


if __name__ == "__main__":
    main()
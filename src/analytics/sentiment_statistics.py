from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl.utils import get_column_letter


# A rendszerben használt normalizált sentiment címkék.
SENTIMENT_LABELS = (
    "positive",
    "negative",
    "neutral",
)


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
) -> None:
    """
    Ellenőrzi, hogy a DataFrame tartalmazza-e a statisztikai
    számításokhoz szükséges oszlopokat.

    Parameters
    ----------
    df:
        Az ellenőrizendő pandas DataFrame.
    required_columns:
        A kötelező oszlopok neveit tartalmazó halmaz.

    Raises
    ------
    ValueError:
        Ha egy vagy több kötelező oszlop hiányzik.
    """
    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing_columns_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            "A statisztikai számításhoz szükséges oszlopok "
            f"közül az alábbiak hiányoznak: {missing_columns_text}"
        )


def prepare_sentiment_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Előkészíti az egységes sentiment adathalmazt a statisztikai
    számításokhoz.

    A függvény:
    - másolatot készít az eredeti DataFrame-ről;
    - kisbetűssé és whitespace-mentessé alakítja a modellcímkéket;
    - numerikus típussá alakítja a konfidenciaértékeket;
    - ellenőrzi a hiányzó vagy ismeretlen sentiment címkéket.

    Parameters
    ----------
    df:
        Az egységes sentiment elemzési DataFrame.

    Returns
    -------
    pd.DataFrame
        A statisztikai számításokra előkészített DataFrame.

    Raises
    ------
    ValueError:
        Ha hiányzó vagy nem támogatott sentiment címke található.
    """
    required_columns = {
        "post_id",
        "model_label",
        "confidence",
    }

    validate_required_columns(df, required_columns)

    prepared_df = df.copy()

    prepared_df["model_label"] = (
        prepared_df["model_label"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    prepared_df["confidence"] = pd.to_numeric(
        prepared_df["confidence"],
        errors="coerce",
    )

    missing_label_mask = prepared_df["model_label"].eq("")

    if missing_label_mask.any():
        missing_count = int(missing_label_mask.sum())

        raise ValueError(
            "A statisztikai összesítés nem végezhető el, mert "
            f"{missing_count} rekordnál hiányzik a model_label értéke."
        )

    unknown_labels = sorted(
        set(prepared_df["model_label"].unique()).difference(
            SENTIMENT_LABELS
        )
    )

    if unknown_labels:
        raise ValueError(
            "Az adathalmaz nem támogatott sentiment címkéket tartalmaz: "
            + ", ".join(unknown_labels)
        )

    return prepared_df


def determine_dominant_sentiment(
    sentiment_counts: dict[str, int],
) -> str:
    """
    Meghatározza a sentiment darabszámok alapján a domináns hangulatot.

    Ha egyetlen kategória rendelkezik a legmagasabb darabszámmal,
    akkor annak neve kerül visszaadásra.

    Ha több kategória azonos legmagasabb darabszámmal rendelkezik,
    akkor az eredmény 'mixed'.

    Ha minden kategória darabszáma nulla, akkor az eredmény 'no_data'.

    Parameters
    ----------
    sentiment_counts:
        A sentiment kategóriákhoz tartozó darabszámok.

    Returns
    -------
    str
        A domináns sentiment címke, 'mixed' vagy 'no_data'.
    """
    if not sentiment_counts:
        return "no_data"

    maximum_count = max(sentiment_counts.values())

    if maximum_count == 0:
        return "no_data"

    dominant_labels = [
        label
        for label, count in sentiment_counts.items()
        if count == maximum_count
    ]

    if len(dominant_labels) > 1:
        return "mixed"

    return dominant_labels[0]


def get_first_available_value(
    group_df: pd.DataFrame,
    column_name: str,
) -> Any:
    """
    Egy csoport adott oszlopából visszaadja az első nem hiányzó értéket.

    Ez azért szükséges, mert a teljes adatbázisban ugyanaz a posztkontextus
    minden hozzá tartozó komment sorában ismétlődik.

    Parameters
    ----------
    group_df:
        Egy adott poszthoz tartozó rekordok DataFrame-je.
    column_name:
        A kiválasztandó oszlop neve.

    Returns
    -------
    Any
        Az első elérhető érték. Hiányzó oszlop vagy érték esetén None.
    """
    if column_name not in group_df.columns:
        return None

    available_values = group_df[column_name].dropna()

    if available_values.empty:
        return None

    for value in available_values:
        if not isinstance(value, str):
            return value

        stripped_value = value.strip()

        if stripped_value:
            return stripped_value

    return None


def calculate_post_statistics(
    full_dataset_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Posztonkénti sentiment statisztikákat készít.

    Egy kimeneti sor egy Facebook-posztot jelent. A számítás tartalmazza:
    - a kommentek teljes számát;
    - a pozitív, negatív és semleges kommentek számát;
    - a sentiment kategóriák százalékos arányát;
    - a domináns kommenthangulatot;
    - az átlagos kommentkonfidenciát;
    - a poszt-, kép- és videókontextus sentiment adatait.

    Parameters
    ----------
    full_dataset_df:
        Az ötödik fejlesztési fázisban létrehozott teljes sentiment
        adathalmaz.

    Returns
    -------
    pd.DataFrame
        A posztonkénti statisztikákat tartalmazó DataFrame.
    """
    prepared_df = prepare_sentiment_dataframe(full_dataset_df)

    post_statistics_records: list[dict[str, Any]] = []

    grouped_posts = prepared_df.groupby(
        "post_id",
        sort=False,
        dropna=False,
    )

    for post_id, post_group in grouped_posts:
        label_counts = post_group["model_label"].value_counts()

        positive_count = int(label_counts.get("positive", 0))
        negative_count = int(label_counts.get("negative", 0))
        neutral_count = int(label_counts.get("neutral", 0))

        comment_count = len(post_group)

        sentiment_counts = {
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
        }

        dominant_sentiment = determine_dominant_sentiment(
            sentiment_counts
        )

        if comment_count > 0:
            positive_ratio = round(
                positive_count / comment_count * 100,
                2,
            )
            negative_ratio = round(
                negative_count / comment_count * 100,
                2,
            )
            neutral_ratio = round(
                neutral_count / comment_count * 100,
                2,
            )
        else:
            positive_ratio = 0.0
            negative_ratio = 0.0
            neutral_ratio = 0.0

        average_confidence = post_group["confidence"].mean()

        if pd.isna(average_confidence):
            average_confidence = None
        else:
            average_confidence = round(
                float(average_confidence),
                4,
            )

        post_statistics_records.append(
            {
                "post_id": post_id,
                "post_type": get_first_available_value(
                    post_group,
                    "post_type",
                ),
                "post_link": get_first_available_value(
                    post_group,
                    "post_link",
                ),
                "comment_count": comment_count,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_ratio": positive_ratio,
                "negative_ratio": negative_ratio,
                "neutral_ratio": neutral_ratio,
                "dominant_comment_sentiment": dominant_sentiment,
                "average_comment_confidence": average_confidence,
                "post_sentiment_label": get_first_available_value(
                    post_group,
                    "post_sentiment_label",
                ),
                "post_sentiment_confidence": get_first_available_value(
                    post_group,
                    "post_sentiment_confidence",
                ),
                "image_context_sentiment_label":
                    get_first_available_value(
                        post_group,
                        "image_context_sentiment_label",
                    ),
                "image_context_sentiment_confidence":
                    get_first_available_value(
                        post_group,
                        "image_context_sentiment_confidence",
                    ),
                "video_context_sentiment_label":
                    get_first_available_value(
                        post_group,
                        "video_context_sentiment_label",
                    ),
                "video_context_sentiment_confidence":
                    get_first_available_value(
                        post_group,
                        "video_context_sentiment_confidence",
                    ),
            }
        )

    return pd.DataFrame(post_statistics_records)


def calculate_overall_statistics(
    full_dataset_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    A teljes sentiment adathalmazra vonatkozó összesített
    statisztikákat készít.

    A kimeneti DataFrame egyetlen sort tartalmaz.

    Parameters
    ----------
    full_dataset_df:
        A teljes, kommentenkénti sentiment adathalmaz.

    Returns
    -------
    pd.DataFrame
        A teljes adathalmaz aggregált mutatóit tartalmazó,
        egysoros DataFrame.
    """
    prepared_df = prepare_sentiment_dataframe(full_dataset_df)

    label_counts = prepared_df["model_label"].value_counts()

    total_positive_count = int(
        label_counts.get("positive", 0)
    )
    total_negative_count = int(
        label_counts.get("negative", 0)
    )
    total_neutral_count = int(
        label_counts.get("neutral", 0)
    )

    total_comment_count = len(prepared_df)
    post_count = prepared_df["post_id"].nunique(dropna=True)

    sentiment_counts = {
        "positive": total_positive_count,
        "negative": total_negative_count,
        "neutral": total_neutral_count,
    }

    overall_dominant_sentiment = determine_dominant_sentiment(
        sentiment_counts
    )

    if total_comment_count > 0:
        total_positive_ratio = round(
            total_positive_count / total_comment_count * 100,
            2,
        )
        total_negative_ratio = round(
            total_negative_count / total_comment_count * 100,
            2,
        )
        total_neutral_ratio = round(
            total_neutral_count / total_comment_count * 100,
            2,
        )
    else:
        total_positive_ratio = 0.0
        total_negative_ratio = 0.0
        total_neutral_ratio = 0.0

    overall_average_confidence = prepared_df["confidence"].mean()

    if pd.isna(overall_average_confidence):
        overall_average_confidence = None
    else:
        overall_average_confidence = round(
            float(overall_average_confidence),
            4,
        )

    overall_statistics_record = {
        "post_count": int(post_count),
        "total_comment_count": total_comment_count,
        "total_positive_count": total_positive_count,
        "total_negative_count": total_negative_count,
        "total_neutral_count": total_neutral_count,
        "total_positive_ratio": total_positive_ratio,
        "total_negative_ratio": total_negative_ratio,
        "total_neutral_ratio": total_neutral_ratio,
        "overall_dominant_sentiment":
            overall_dominant_sentiment,
        "overall_average_confidence":
            overall_average_confidence,
    }

    return pd.DataFrame([overall_statistics_record])


def format_excel_worksheet(
    worksheet,
    freeze_panes: str = "A2",
    maximum_column_width: int = 60,
) -> None:
    """
    Alapvető formázást végez egy openpyxl munkalapon.

    A függvény:
    - rögzíti a fejlécsort;
    - bekapcsolja az automatikus szűrést;
    - a tartalom alapján beállítja az oszlopszélességeket.

    Parameters
    ----------
    worksheet:
        Az openpyxl munkalap objektuma.
    freeze_panes:
        A rögzítendő cellapozíció.
    maximum_column_width:
        Az automatikusan beállítható legnagyobb oszlopszélesség.
    """
    worksheet.freeze_panes = freeze_panes

    if worksheet.max_row > 0 and worksheet.max_column > 0:
        worksheet.auto_filter.ref = worksheet.dimensions

    for column_cells in worksheet.columns:
        maximum_length = 0
        column_number = column_cells[0].column

        for cell in column_cells:
            cell_value = "" if cell.value is None else str(cell.value)
            maximum_length = max(
                maximum_length,
                len(cell_value),
            )

        adjusted_width = min(
            maximum_length + 2,
            maximum_column_width,
        )

        column_letter = get_column_letter(column_number)
        worksheet.column_dimensions[column_letter].width = adjusted_width


def export_sentiment_workbook(
    full_dataset_df: pd.DataFrame,
    post_statistics_df: pd.DataFrame,
    overall_statistics_df: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    """
    Egyetlen, három munkalapos Excel-fájlba exportálja
    a részletes és összesített sentiment adatokat.

    Munkalapok:
    - full_dataset
    - post_statistics
    - overall_statistics

    Parameters
    ----------
    full_dataset_df:
        A kommentenkénti teljes sentiment adathalmaz.
    post_statistics_df:
        A posztonkénti összesített statisztika.
    overall_statistics_df:
        A teljes adathalmaz összesített statisztikája.
    output_file:
        A létrehozandó Excel-fájl elérési útja.

    Returns
    -------
    Path
        A létrehozott Excel-fájl útvonala.
    """
    output_path = Path(output_file)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
    ) as writer:
        full_dataset_df.to_excel(
            writer,
            sheet_name="full_dataset",
            index=False,
        )

        post_statistics_df.to_excel(
            writer,
            sheet_name="post_statistics",
            index=False,
        )

        overall_statistics_df.to_excel(
            writer,
            sheet_name="overall_statistics",
            index=False,
        )

        format_excel_worksheet(
            writer.sheets["full_dataset"],
            maximum_column_width=60,
        )

        format_excel_worksheet(
            writer.sheets["post_statistics"],
            maximum_column_width=35,
        )

        format_excel_worksheet(
            writer.sheets["overall_statistics"],
            maximum_column_width=35,
        )

    return output_path

#Tesztelésre
if __name__ == "__main__":
    sample_df = pd.DataFrame(
        {
            "post_id": [
                "P1",
                "P1",
                "P1",
                "P2",
                "P2",
            ],
            "post_type": [
                "image",
                "image",
                "image",
                "video",
                "video",
            ],
            "post_link": [
                "https://example.com/p1",
                "https://example.com/p1",
                "https://example.com/p1",
                "https://example.com/p2",
                "https://example.com/p2",
            ],
            "model_label": [
                "positive",
                "positive",
                "negative",
                "negative",
                "neutral",
            ],
            "confidence": [
                0.81,
                0.72,
                0.64,
                0.78,
                0.55,
            ],
            "post_sentiment_label": [
                "positive",
                "positive",
                "positive",
                "negative",
                "negative",
            ],
            "post_sentiment_confidence": [
                0.77,
                0.77,
                0.77,
                0.73,
                0.73,
            ],
            "image_context_sentiment_label": [
                "positive",
                "positive",
                "positive",
                None,
                None,
            ],
            "image_context_sentiment_confidence": [
                0.69,
                0.69,
                0.69,
                None,
                None,
            ],
            "video_context_sentiment_label": [
                None,
                None,
                None,
                "negative",
                "negative",
            ],
            "video_context_sentiment_confidence": [
                None,
                None,
                None,
                0.75,
                0.75,
            ],
        }
    )

    sample_post_statistics_df = calculate_post_statistics(
        sample_df
    )

    sample_overall_statistics_df = calculate_overall_statistics(
        sample_df
    )

    print("Posztonkénti statisztika:")
    print(sample_post_statistics_df)

    print("\nTeljes adathalmaz statisztikája:")
    print(sample_overall_statistics_df)
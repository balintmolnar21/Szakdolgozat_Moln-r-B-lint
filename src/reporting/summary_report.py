from pathlib import Path

import pandas as pd


SENTIMENT_TRANSLATIONS = {
    "positive": "pozitív",
    "negative": "negatív",
    "neutral": "semleges",
    "mixed": "vegyes",
    "no_data": "nincs adat",
}

ALIGNMENT_TRANSLATIONS = {
    "aligned": "azonos irányú",
    "opposite": "ellentétes",
    "mixed": "vegyes",
    "different": "eltérő",
    "unclear": "nem egyértelmű",
}


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    dataframe_name: str,
) -> None:
    
    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing_columns_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"A(z) {dataframe_name} DataFrame-ből hiányoznak "
            f"az alábbi oszlopok: {missing_columns_text}"
        )


def create_output_directory(
    output_directory: str | Path,
) -> Path:
    
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def normalize_label(
    value,
) -> str:
    
    if value is None or pd.isna(value):
        return ""

    return str(value).strip().lower()


def translate_sentiment(
    value,
) -> str:
    
    normalized_value = normalize_label(value)

    return SENTIMENT_TRANSLATIONS.get(
        normalized_value,
        normalized_value or "ismeretlen",
    )


def translate_alignment(
    value,
) -> str:
    
    normalized_value = normalize_label(value)

    return ALIGNMENT_TRANSLATIONS.get(
        normalized_value,
        normalized_value or "ismeretlen",
    )


def get_overall_statistics_row(
    overall_statistics_df: pd.DataFrame,
) -> pd.Series:
    
    if overall_statistics_df.empty:
        raise ValueError(
            "Az overall_statistics_df nem tartalmaz adatot."
        )

    return overall_statistics_df.iloc[0]


def get_most_positive_post(
    post_statistics_df: pd.DataFrame,
) -> pd.Series:
    
    return post_statistics_df.loc[
        post_statistics_df["positive_ratio"].idxmax()
    ]


def get_most_negative_post(
    post_statistics_df: pd.DataFrame,
) -> pd.Series:
    
    return post_statistics_df.loc[
        post_statistics_df["negative_ratio"].idxmax()
    ]


def get_most_common_context_alignment(
    context_analysis_df: pd.DataFrame,
) -> tuple[str, int]:
    
    normalized_alignments = (
        context_analysis_df["context_alignment"]
        .fillna("unclear")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    alignment_counts = normalized_alignments.value_counts()

    if alignment_counts.empty:
        return "unclear", 0

    most_common_alignment = str(alignment_counts.index[0])
    occurrence_count = int(alignment_counts.iloc[0])

    return most_common_alignment, occurrence_count


def calculate_average_model_confidence(
    post_statistics_df: pd.DataFrame,
) -> float:
    
    confidence_values = pd.to_numeric(
        post_statistics_df["average_comment_confidence"],
        errors="coerce",
    )

    if confidence_values.dropna().empty:
        return 0.0

    return float(confidence_values.mean())


def build_summary_report_text(
    post_statistics_df: pd.DataFrame,
    overall_statistics_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
) -> str:
    
    validate_required_columns(
        post_statistics_df,
        {
            "post_id",
            "positive_ratio",
            "negative_ratio",
            "neutral_ratio",
            "average_comment_confidence",
        },
        "post_statistics_df",
    )

    validate_required_columns(
        overall_statistics_df,
        {
            "post_count",
            "comment_count",
            "positive_count",
            "negative_count",
            "neutral_count",
            "positive_ratio",
            "negative_ratio",
            "neutral_ratio",
            "dominant_sentiment",
        },
        "overall_statistics_df",
    )

    validate_required_columns(
        context_analysis_df,
        {
            "post_id",
            "context_alignment",
            "context_reaction_type",
            "context_interpretation",
        },
        "context_analysis_df",
    )

    if post_statistics_df.empty:
        raise ValueError(
            "A post_statistics_df nem tartalmaz adatot."
        )

    if context_analysis_df.empty:
        raise ValueError(
            "A context_analysis_df nem tartalmaz adatot."
        )

    overall_row = get_overall_statistics_row(
        overall_statistics_df
    )

    most_positive_post = get_most_positive_post(
        post_statistics_df
    )

    most_negative_post = get_most_negative_post(
        post_statistics_df
    )

    most_common_alignment, alignment_count = (
        get_most_common_context_alignment(
            context_analysis_df
        )
    )

    average_confidence = calculate_average_model_confidence(
        post_statistics_df
    )

    post_count = int(overall_row["post_count"])
    comment_count = int(overall_row["comment_count"])

    positive_count = int(overall_row["positive_count"])
    negative_count = int(overall_row["negative_count"])
    neutral_count = int(overall_row["neutral_count"])

    positive_ratio = float(overall_row["positive_ratio"])
    negative_ratio = float(overall_row["negative_ratio"])
    neutral_ratio = float(overall_row["neutral_ratio"])

    dominant_sentiment = translate_sentiment(
        overall_row["dominant_sentiment"]
    )

    translated_alignment = translate_alignment(
        most_common_alignment
    )

    most_positive_post_id = str(
        most_positive_post["post_id"]
    )

    most_negative_post_id = str(
        most_negative_post["post_id"]
    )

    most_positive_ratio = float(
        most_positive_post["positive_ratio"]
    )

    most_negative_ratio = float(
        most_negative_post["negative_ratio"]
    )

    report_lines = [
        "SENTIMENTELEMZÉSI ÖSSZEFOGLALÓ RIPORT",
        "=" * 42,
        "",
        "1. Feldolgozott adatok",
        f"Feldolgozott posztok száma: {post_count}",
        f"Feldolgozott kommentek száma: {comment_count}",
        "",
        "2. Összesített sentimentmegoszlás",
        f"Pozitív kommentek: {positive_count} db "
        f"({positive_ratio:.2f}%)",
        f"Negatív kommentek: {negative_count} db "
        f"({negative_ratio:.2f}%)",
        f"Semleges kommentek: {neutral_count} db "
        f"({neutral_ratio:.2f}%)",
        f"Domináns összesített sentiment: {dominant_sentiment}",
        "",
        "3. Posztonkénti kiemelt eredmények",
        f"Legpozitívabb fogadtatású poszt: "
        f"{most_positive_post_id} "
        f"({most_positive_ratio:.2f}% pozitív komment)",
        f"Legnegatívabb fogadtatású poszt: "
        f"{most_negative_post_id} "
        f"({most_negative_ratio:.2f}% negatív komment)",
        "",
        "4. Modellbizonyosság",
        f"A kommentpredikciók átlagos konfidenciaértéke: "
        f"{average_confidence:.3f}",
        "",
        "5. Kontextuselemzés",
        f"Leggyakoribb kontextusilleszkedés: "
        f"{translated_alignment}",
        f"Előfordulások száma: {alignment_count}",
        "",
        "6. Posztonkénti kontextuális értelmezések",
    ]

    for _, row in context_analysis_df.iterrows():
        post_id = str(row["post_id"])
        interpretation = str(
            row["context_interpretation"]
        ).strip()

        report_lines.append(
            f"- {post_id}: {interpretation}"
        )

    report_lines.extend(
        [
            "",
            "7. Értelmezési korlát",
            (
                "A riport sentiment címkékből, statisztikai "
                "mutatókból és szabályalapú kontextuselemzésből "
                "készül. Az eredmények nem tekinthetők teljes "
                "álláspont-felismerésnek, ezért a posztok és "
                "kommentek közötti kapcsolat csak óvatosan "
                "értelmezhető."
            ),
        ]
    )

    return "\n".join(report_lines)


def save_summary_report(
    report_text: str,
    output_directory: str | Path = "outputs/reports",
    file_name: str = "sentiment_summary.txt",
) -> Path:
    
    output_path = create_output_directory(
        output_directory
    )

    output_file = output_path / file_name

    output_file.write_text(
        report_text,
        encoding="utf-8",
    )

    return output_file


def create_summary_report(
    post_statistics_df: pd.DataFrame,
    overall_statistics_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    output_directory: str | Path = "outputs/reports",
) -> Path:
    
    report_text = build_summary_report_text(
        post_statistics_df=post_statistics_df,
        overall_statistics_df=overall_statistics_df,
        context_analysis_df=context_analysis_df,
    )

    return save_summary_report(
        report_text=report_text,
        output_directory=output_directory,
    )

#Tesztelésre
if __name__ == "__main__":
    sample_post_statistics_df = pd.DataFrame(
        {
            "post_id": ["P1", "P2", "P3", "P4", "P5"],
            "positive_ratio": [
                65.0,
                20.0,
                15.0,
                60.0,
                40.0,
            ],
            "negative_ratio": [
                20.0,
                65.0,
                70.0,
                25.0,
                40.0,
            ],
            "neutral_ratio": [
                15.0,
                15.0,
                15.0,
                15.0,
                20.0,
            ],
            "average_comment_confidence": [
                0.89,
                0.84,
                0.91,
                0.86,
                0.78,
            ],
        }
    )

    sample_overall_statistics_df = pd.DataFrame(
        {
            "post_count": [5],
            "comment_count": [100],
            "positive_count": [40],
            "negative_count": [44],
            "neutral_count": [16],
            "positive_ratio": [40.0],
            "negative_ratio": [44.0],
            "neutral_ratio": [16.0],
            "dominant_sentiment": ["negative"],
        }
    )

    sample_context_analysis_df = pd.DataFrame(
        {
            "post_id": ["P1", "P2", "P3", "P4", "P5"],
            "context_alignment": [
                "aligned",
                "opposite",
                "aligned",
                "opposite",
                "mixed",
            ],
            "context_reaction_type": [
                "aligned_positive",
                "critical_response",
                "aligned_negative",
                "supportive_response",
                "mixed_response",
            ],
            "context_interpretation": [
                (
                    "A poszt és a kommentek hangulata "
                    "azonos pozitív irányú."
                ),
                (
                    "A pozitív poszt alatt a negatív "
                    "kommentek dominálnak."
                ),
                (
                    "A poszt és a kommentek hangulata "
                    "azonos negatív irányú."
                ),
                (
                    "A negatív poszt alatt a pozitív "
                    "kommentek dominálnak."
                ),
                (
                    "A kommentek fogadtatása vegyes."
                ),
            ],
        }
    )

    created_report_file = create_summary_report(
        post_statistics_df=sample_post_statistics_df,
        overall_statistics_df=sample_overall_statistics_df,
        context_analysis_df=sample_context_analysis_df,
    )

    print(
        "A tesztriport sikeresen létrejött:"
    )
    print(created_report_file)
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


SENTIMENT_LABEL_TRANSLATIONS = {
    "positive": "Pozitív",
    "negative": "Negatív",
    "neutral": "Semleges",
}

CONTEXT_ALIGNMENT_TRANSLATIONS = {
    "aligned": "Azonos irányú",
    "opposite": "Ellentétes",
    "mixed": "Vegyes",
    "different": "Eltérő",
    "unclear": "Nem egyértelmű",
}


def create_output_directory(
    output_directory: str | Path,
) -> Path:
    
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


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


def save_and_close_figure(
    output_file: Path,
) -> Path:
    
    plt.tight_layout()
    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    return output_file


def plot_overall_sentiment_distribution(
    overall_statistics_df: pd.DataFrame,
    output_directory: str | Path = "outputs/charts",
) -> Path:
    
    required_columns = {
        "positive_count",
        "negative_count",
        "neutral_count",
    }

    validate_required_columns(
        overall_statistics_df,
        required_columns,
        "overall_statistics_df",
    )

    if overall_statistics_df.empty:
        raise ValueError(
            "Az overall_statistics_df nem tartalmaz adatot."
        )

    output_path = create_output_directory(output_directory)

    statistics_row = overall_statistics_df.iloc[0]

    labels = [
        "Pozitív",
        "Negatív",
        "Semleges",
    ]

    values = [
        float(statistics_row["positive_count"]),
        float(statistics_row["negative_count"]),
        float(statistics_row["neutral_count"]),
    ]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)

    plt.title("A kommentek összesített sentimenteloszlása")
    plt.xlabel("Sentiment kategória")
    plt.ylabel("Kommentek száma")
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(value)}",
            ha="center",
            va="bottom",
        )

    output_file = output_path / "overall_sentiment_distribution.png"

    return save_and_close_figure(output_file)


def plot_post_sentiment_distribution(
    post_statistics_df: pd.DataFrame,
    output_directory: str | Path = "outputs/charts",
) -> Path:
    
    required_columns = {
        "post_id",
        "positive_ratio",
        "negative_ratio",
        "neutral_ratio",
    }

    validate_required_columns(
        post_statistics_df,
        required_columns,
        "post_statistics_df",
    )

    if post_statistics_df.empty:
        raise ValueError(
            "A post_statistics_df nem tartalmaz adatot."
        )

    output_path = create_output_directory(output_directory)

    chart_df = post_statistics_df[
        [
            "post_id",
            "positive_ratio",
            "negative_ratio",
            "neutral_ratio",
        ]
    ].copy()

    chart_df = chart_df.set_index("post_id")

    chart_df = chart_df.rename(
        columns={
            "positive_ratio": "Pozitív",
            "negative_ratio": "Negatív",
            "neutral_ratio": "Semleges",
        }
    )

    axis = chart_df.plot(
        kind="bar",
        figsize=(11, 6),
    )

    axis.set_title("A kommentek sentimentmegoszlása posztonként")
    axis.set_xlabel("Posztazonosító")
    axis.set_ylabel("Kommentek aránya (%)")
    axis.set_ylim(0, 100)
    axis.legend(title="Sentiment kategória")
    axis.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=0)

    output_file = output_path / "post_sentiment_distribution.png"

    return save_and_close_figure(output_file)


def plot_average_confidence_by_post(
    post_statistics_df: pd.DataFrame,
    output_directory: str | Path = "outputs/charts",
) -> Path:
   
    required_columns = {
        "post_id",
        "average_comment_confidence",
    }

    validate_required_columns(
        post_statistics_df,
        required_columns,
        "post_statistics_df",
    )

    if post_statistics_df.empty:
        raise ValueError(
            "A post_statistics_df nem tartalmaz adatot."
        )

    output_path = create_output_directory(output_directory)

    chart_df = post_statistics_df[
        [
            "post_id",
            "average_comment_confidence",
        ]
    ].copy()

    chart_df["average_comment_confidence"] = pd.to_numeric(
        chart_df["average_comment_confidence"],
        errors="coerce",
    ).fillna(0.0)

    plt.figure(figsize=(10, 5))

    bars = plt.bar(
        chart_df["post_id"].astype(str),
        chart_df["average_comment_confidence"],
    )

    plt.title("A modell átlagos bizonyossága posztonként")
    plt.xlabel("Posztazonosító")
    plt.ylabel("Átlagos konfidencia")
    plt.ylim(0, 1)
    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(
        bars,
        chart_df["average_comment_confidence"],
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    output_file = output_path / "average_confidence_by_post.png"

    return save_and_close_figure(output_file)


def plot_context_alignment_distribution(
    context_analysis_df: pd.DataFrame,
    output_directory: str | Path = "outputs/charts",
) -> Path:
    
    required_columns = {
        "context_alignment",
    }

    validate_required_columns(
        context_analysis_df,
        required_columns,
        "context_analysis_df",
    )

    if context_analysis_df.empty:
        raise ValueError(
            "A context_analysis_df nem tartalmaz adatot."
        )

    output_path = create_output_directory(output_directory)

    normalized_alignment = (
        context_analysis_df["context_alignment"]
        .fillna("unclear")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    alignment_counts = normalized_alignment.value_counts()

    translated_labels = [
        CONTEXT_ALIGNMENT_TRANSLATIONS.get(
            alignment,
            alignment,
        )
        for alignment in alignment_counts.index
    ]

    values = alignment_counts.values

    plt.figure(figsize=(9, 5))
    bars = plt.bar(translated_labels, values)

    plt.title("A kontextusilleszkedési kategóriák megoszlása")
    plt.xlabel("Kontextusilleszkedés")
    plt.ylabel("Posztok száma")
    plt.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=20, ha="right")

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(value)}",
            ha="center",
            va="bottom",
        )

    output_file = output_path / "context_alignment_distribution.png"

    return save_and_close_figure(output_file)


def create_all_sentiment_charts(
    post_statistics_df: pd.DataFrame,
    overall_statistics_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    output_directory: str | Path = "outputs/charts",
) -> list[Path]:
    
    created_chart_files = [
        plot_overall_sentiment_distribution(
            overall_statistics_df=overall_statistics_df,
            output_directory=output_directory,
        ),
        plot_post_sentiment_distribution(
            post_statistics_df=post_statistics_df,
            output_directory=output_directory,
        ),
        plot_average_confidence_by_post(
            post_statistics_df=post_statistics_df,
            output_directory=output_directory,
        ),
        plot_context_alignment_distribution(
            context_analysis_df=context_analysis_df,
            output_directory=output_directory,
        ),
    ]

    return created_chart_files

#Tesztelésre
if __name__ == "__main__":
    sample_post_statistics_df = pd.DataFrame(
        {
            "post_id": ["P1", "P2", "P3", "P4", "P5"],
            "positive_count": [13, 4, 3, 12, 8],
            "negative_count": [4, 13, 14, 5, 8],
            "neutral_count": [3, 3, 3, 3, 4],
            "positive_ratio": [65.0, 20.0, 15.0, 60.0, 40.0],
            "negative_ratio": [20.0, 65.0, 70.0, 25.0, 40.0],
            "neutral_ratio": [15.0, 15.0, 15.0, 15.0, 20.0],
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
            "positive_count": [40],
            "negative_count": [44],
            "neutral_count": [16],
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
        }
    )

    created_files = create_all_sentiment_charts(
        post_statistics_df=sample_post_statistics_df,
        overall_statistics_df=sample_overall_statistics_df,
        context_analysis_df=sample_context_analysis_df,
    )

    print("Létrehozott tesztgrafikonok:")

    for created_file in created_files:
        print(f"- {created_file}")
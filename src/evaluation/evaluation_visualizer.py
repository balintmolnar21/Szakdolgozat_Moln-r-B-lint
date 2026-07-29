from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


LABEL_TRANSLATIONS = {
    "negative": "Negatív",
    "neutral": "Semleges",
    "positive": "Pozitív",
}


def create_confusion_matrix_chart(
    confusion_matrix_df: pd.DataFrame,
    output_file: Path,
) -> Path:
    
    if confusion_matrix_df.empty:
        raise ValueError(
            "A confusion matrix üres, ezért a grafikon "
            "nem készíthető el."
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    matrix_values = confusion_matrix_df.to_numpy()

    row_labels = [
        translate_matrix_label(label)
        for label in confusion_matrix_df.index
    ]

    column_labels = [
        translate_matrix_label(label)
        for label in confusion_matrix_df.columns
    ]

    figure, axis = plt.subplots(
        figsize=(8, 6)
    )

    image = axis.imshow(matrix_values)

    axis.set_title(
        "A sentimentmodell confusion matrixa"
    )

    axis.set_xlabel(
        "Modell által előre jelzett címke"
    )

    axis.set_ylabel(
        "Ember által megadott címke"
    )

    axis.set_xticks(
        range(len(column_labels))
    )

    axis.set_xticklabels(
        column_labels
    )

    axis.set_yticks(
        range(len(row_labels))
    )

    axis.set_yticklabels(
        row_labels
    )

    maximum_value = matrix_values.max()

    threshold = maximum_value / 2 if maximum_value else 0

    for row_index in range(matrix_values.shape[0]):
        for column_index in range(matrix_values.shape[1]):
            cell_value = int(
                matrix_values[
                    row_index,
                    column_index,
                ]
            )

            text_color = (
                "white"
                if cell_value > threshold
                else "black"
            )

            axis.text(
                column_index,
                row_index,
                str(cell_value),
                horizontalalignment="center",
                verticalalignment="center",
                color=text_color,
                fontsize=12,
            )

    figure.colorbar(
        image,
        ax=axis,
        label="Kommentek száma",
    )

    figure.tight_layout()

    figure.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_file


def create_classification_metrics_chart(
    metrics_df: pd.DataFrame,
    output_file: Path,
) -> Path:
    
    if metrics_df.empty:
        raise ValueError(
            "A metrikákat tartalmazó DataFrame üres, "
            "ezért a grafikon nem készíthető el."
        )

    required_columns = {
        "category",
        "precision",
        "recall",
        "f1_score",
    }

    missing_columns = required_columns.difference(
        metrics_df.columns
    )

    if missing_columns:
        raise ValueError(
            "A metrikadiagramhoz szükséges oszlopok "
            f"közül hiányzik: {', '.join(sorted(missing_columns))}."
        )

    class_metrics_df = metrics_df[
        metrics_df["category"].isin(
            ["negative", "neutral", "positive"]
        )
    ].copy()

    if class_metrics_df.empty:
        raise ValueError(
            "Nem találhatók osztályonkénti metrikák."
        )

    category_translations = {
        "negative": "Negatív",
        "neutral": "Semleges",
        "positive": "Pozitív",
    }

    class_metrics_df["category_hu"] = (
        class_metrics_df["category"].map(
            category_translations
        )
    )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    chart_data = class_metrics_df.set_index(
        "category_hu"
    )[
        [
            "precision",
            "recall",
            "f1_score",
        ]
    ]

    axis = chart_data.plot(
        kind="bar",
        figsize=(9, 6),
    )

    axis.set_title(
        "A sentimentmodell osztályonkénti teljesítménye"
    )

    axis.set_xlabel(
        "Sentimentkategória"
    )

    axis.set_ylabel(
        "Metrika értéke"
    )

    axis.set_ylim(
        0,
        1,
    )

    axis.legend(
        [
            "Precision",
            "Recall",
            "F1-score",
        ]
    )

    axis.tick_params(
        axis="x",
        rotation=0,
    )

    axis.grid(
        axis="y",
        alpha=0.3,
    )

    figure = axis.get_figure()

    figure.tight_layout()

    figure.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(figure)

    return output_file


def translate_matrix_label(label: object) -> str:
    
    normalized_label = (
        str(label)
        .replace("actual_", "")
        .replace("predicted_", "")
        .strip()
        .lower()
    )

    return LABEL_TRANSLATIONS.get(
        normalized_label,
        normalized_label.capitalize(),
    )
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
    """
    Grafikus confusion matrixot készít és PNG-fájlba menti.

    A sorok az ember által megadott címkéket, az oszlopok
    pedig a modell által előre jelzett címkéket jelentik.

    Args:
        confusion_matrix_df:
            A confusion matrix DataFrame formátumban.
        output_file:
            A létrehozandó PNG-fájl elérési útja.

    Returns:
        A létrehozott grafikon elérési útja.

    Raises:
        ValueError:
            Ha a confusion matrix üres.
    """
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


def translate_matrix_label(label: object) -> str:
    """
    A confusion matrix technikai címkéit magyar
    megjelenítési formára alakítja.
    """
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
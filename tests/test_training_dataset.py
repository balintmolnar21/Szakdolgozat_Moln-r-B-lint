import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from training.training_dataset import (
    create_training_dataset_bundle,
    print_dataset_summary,
)


TRAIN_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "train_comments.csv"
)

VALIDATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "validation_comments.csv"
)


def main() -> None:
    print(
        "Fine-tuning adathalmazok előkészítése..."
    )

    dataset_bundle = create_training_dataset_bundle(
        train_file=TRAIN_FILE,
        validation_file=VALIDATION_FILE,
        emoji_mode="raw",
    )

    print_dataset_summary(
        dataframe=dataset_bundle.train_dataframe,
        dataset_name="TRAIN HALMAZ",
    )

    print_dataset_summary(
        dataframe=dataset_bundle.validation_dataframe,
        dataset_name="VALIDATION HALMAZ",
    )

    print(
        "\nEmoji mód:"
    )

    print(
        dataset_bundle.emoji_mode
    )

    print(
        "\nTrain minta:"
    )

    print(
        dataset_bundle.train_dataframe[
            [
                "comment_text",
                "processed_text",
                "manual_label",
                "label",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    print(
        "\nValidation minta:"
    )

    print(
        dataset_bundle.validation_dataframe[
            [
                "comment_text",
                "processed_text",
                "manual_label",
                "label",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
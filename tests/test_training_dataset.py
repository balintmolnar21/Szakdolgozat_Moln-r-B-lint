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


DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validation"
)


TRAIN_COMMENTS_FILE = (
    DATA_DIRECTORY
    / "train_comments.csv"
)

TRAIN_POST_CONTEXT_FILE = (
    DATA_DIRECTORY
    / "train_post_context.csv"
)

VALIDATION_COMMENTS_FILE = (
    DATA_DIRECTORY
    / "validation_comments.csv"
)

VALIDATION_POST_CONTEXT_FILE = (
    DATA_DIRECTORY
    / "validation_post_context.csv"
)


def main() -> None:
    print(
        "Context-aware fine-tuning "
        "adathalmazok előkészítése..."
    )

    bundle = create_training_dataset_bundle(
        train_comments_file=TRAIN_COMMENTS_FILE,
        train_post_context_file=TRAIN_POST_CONTEXT_FILE,
        validation_comments_file=VALIDATION_COMMENTS_FILE,
        validation_post_context_file=(
            VALIDATION_POST_CONTEXT_FILE
        ),
        emoji_mode="raw",
    )

    print_dataset_summary(
        dataframe=bundle.train_dataframe,
        dataset_name="TRAIN HALMAZ",
    )

    print_dataset_summary(
        dataframe=bundle.validation_dataframe,
        dataset_name="VALIDATION HALMAZ",
    )

    print(
        f"\nEmoji mód: {bundle.emoji_mode}"
    )

    preview_columns = [
        "post_id",
        "processed_post_text",
        "processed_comment_text",
        "manual_label",
        "label",
    ]

    print(
        "\nTRAIN MINTA:"
    )

    print(
        bundle.train_dataframe[
            preview_columns
        ]
        .head(10)
        .to_string(
            index=False
        )
    )

    print(
        "\nVALIDATION MINTA:"
    )

    print(
        bundle.validation_dataframe[
            preview_columns
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
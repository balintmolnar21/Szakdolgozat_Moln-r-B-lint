import sys
from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

SRC_DIRECTORY = (
    PROJECT_ROOT
    / "src"
)

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from training.context_aware_dataset import (
    ContextAwareSentimentDataset,
)
from training.context_aware_model import (
    load_context_aware_tokenizer,
)
from training.training_config import (
    ContextAwareTrainingConfig,
)
from training.training_dataset import (
    create_training_dataset_bundle,
)


DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validation"
)


def main() -> None:
    config = (
        ContextAwareTrainingConfig()
    )

    print(
        "Context-aware tokenizálási teszt..."
    )

    print(
        f"Modell: {config.model_name}"
    )

    print(
        f"Maximális hossz: {config.max_length}"
    )

    print(
        f"Emoji mód: {config.emoji_mode}"
    )

    bundle = (
        create_training_dataset_bundle(
            train_comments_file=(
                DATA_DIRECTORY
                / "train_comments.csv"
            ),
            train_post_context_file=(
                DATA_DIRECTORY
                / "train_post_context.csv"
            ),
            validation_comments_file=(
                DATA_DIRECTORY
                / "validation_comments.csv"
            ),
            validation_post_context_file=(
                DATA_DIRECTORY
                / "validation_post_context.csv"
            ),
            emoji_mode=config.emoji_mode,
        )
    )

    tokenizer = (
        load_context_aware_tokenizer(
            config.model_name
        )
    )

    train_dataset = (
        ContextAwareSentimentDataset(
            dataframe=(
                bundle.train_dataframe
            ),
            tokenizer=tokenizer,
            max_length=config.max_length,
        )
    )

    validation_dataset = (
        ContextAwareSentimentDataset(
            dataframe=(
                bundle.validation_dataframe
            ),
            tokenizer=tokenizer,
            max_length=config.max_length,
        )
    )

    print(
        f"\nTrain elemszám: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation elemszám: "
        f"{len(validation_dataset)}"
    )

    sample = train_dataset[0]

    print(
        "\nElső tokenizált rekord kulcsai:"
    )

    print(
        sample.keys()
    )

    print(
        "\nTokenek száma:"
    )

    print(
        len(sample["input_ids"])
    )

    print(
        "\nNumerikus címke:"
    )

    print(
        sample["labels"]
    )

    print(
        "\nDekódolt poszt + komment bemenet:"
    )

    print(
        tokenizer.decode(
            sample["input_ids"],
            skip_special_tokens=False,
        )
    )

    assert (
        len(sample["input_ids"])
        <= config.max_length
    )

    assert (
        sample["labels"]
        in {0, 1, 2}
    )

    print(
        "\nA context-aware tokenizálási "
        "teszt sikeresen lefutott."
    )


if __name__ == "__main__":
    main()
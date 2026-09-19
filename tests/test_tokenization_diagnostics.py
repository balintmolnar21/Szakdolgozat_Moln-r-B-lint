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


from training.context_aware_model import (
    load_context_aware_tokenizer,
)
from training.training_config import (
    ContextAwareTrainingConfig,
)
from training.training_dataset import (
    create_training_dataset_bundle,
)
from training.tokenization_diagnostics import (
    analyze_tokenization,
    create_diagnostics_dataframe,
)


DATA_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "validation"
)

OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "training"
)

OUTPUT_FILE = (
    OUTPUT_DIRECTORY
    / "tokenization_diagnostics.csv"
)


EMOJI_MODES = [
    "raw",
    "text",
    "bracketed",
]


def main() -> None:
    config = (
        ContextAwareTrainingConfig()
    )

    print(
        "Tokenizálási diagnosztika indítása..."
    )

    print(
        f"Modell: {config.model_name}"
    )

    print(
        f"Maximális hossz: {config.max_length}"
    )

    tokenizer = (
        load_context_aware_tokenizer(
            config.model_name
        )
    )

    print(
        f"UNK token: {tokenizer.unk_token}"
    )

    print(
        f"UNK token ID: {tokenizer.unk_token_id}"
    )

    diagnostic_results = []

    for emoji_mode in EMOJI_MODES:
        print(
            "\n"
            + "=" * 70
        )

        print(
            f"Emoji mód vizsgálata: {emoji_mode}"
        )

        print(
            "=" * 70
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
                emoji_mode=emoji_mode,
            )
        )

        train_result = analyze_tokenization(
            dataframe=bundle.train_dataframe,
            tokenizer=tokenizer,
            dataset_name="train",
            emoji_mode=emoji_mode,
            max_length=config.max_length,
        )

        validation_result = analyze_tokenization(
            dataframe=bundle.validation_dataframe,
            tokenizer=tokenizer,
            dataset_name="validation",
            emoji_mode=emoji_mode,
            max_length=config.max_length,
        )

        diagnostic_results.extend(
            [
                train_result,
                validation_result,
            ]
        )

        print(
            "\nTRAIN:"
        )

        print(
            f"Rekordok: "
            f"{train_result.record_count}"
        )

        print(
            f"[UNK]-ot tartalmazó rekordok: "
            f"{train_result.records_with_unk} "
            f"({train_result.records_with_unk_ratio:.2f}%)"
        )

        print(
            f"Összes [UNK] token: "
            f"{train_result.total_unk_tokens}"
        )

        print(
            f"Átlagos tokenhossz: "
            f"{train_result.average_token_length:.2f}"
        )

        print(
            f"Maximális tokenhossz: "
            f"{train_result.maximum_token_length}"
        )

        print(
            f"{config.max_length} tokent meghaladó rekordok: "
            f"{train_result.records_over_max_length} "
            f"({train_result.records_over_max_length_ratio:.2f}%)"
        )

        print(
            "\nVALIDATION:"
        )

        print(
            f"Rekordok: "
            f"{validation_result.record_count}"
        )

        print(
            f"[UNK]-ot tartalmazó rekordok: "
            f"{validation_result.records_with_unk} "
            f"({validation_result.records_with_unk_ratio:.2f}%)"
        )

        print(
            f"Összes [UNK] token: "
            f"{validation_result.total_unk_tokens}"
        )

        print(
            f"Átlagos tokenhossz: "
            f"{validation_result.average_token_length:.2f}"
        )

        print(
            f"Maximális tokenhossz: "
            f"{validation_result.maximum_token_length}"
        )

        print(
            f"{config.max_length} tokent meghaladó rekordok: "
            f"{validation_result.records_over_max_length} "
            f"({validation_result.records_over_max_length_ratio:.2f}%)"
        )

    diagnostics_dataframe = (
        create_diagnostics_dataframe(
            diagnostic_results
        )
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    diagnostics_dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ÖSSZESÍTETT EREDMÉNY"
    )

    print(
        "=" * 70
    )

    print(
        diagnostics_dataframe.to_string(
            index=False
        )
    )

    print(
        "\nDiagnosztikai CSV mentve ide:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()
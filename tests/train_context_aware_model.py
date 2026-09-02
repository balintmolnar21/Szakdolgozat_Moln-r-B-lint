import json
import sys
from pathlib import Path

import torch


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


from training.context_aware_trainer import (
    create_context_aware_trainer,
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

TRAINING_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "training"
    / "context_aware_text"
)

FINAL_MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "models"
    / "context_aware_hubert_text"
)


def main() -> None:
    config = (
        ContextAwareTrainingConfig()
    )

    print(
        "=" * 70
    )

    print(
        "CONTEXT-AWARE HUBERT FINE-TUNING"
    )

    print(
        "=" * 70
    )

    print(
        f"\nModell: {config.model_name}"
    )

    print(
        f"Emoji mód: {config.emoji_mode}"
    )

    print(
        f"Epochok száma: "
        f"{config.num_train_epochs}"
    )

    print(
        f"Learning rate: "
        f"{config.learning_rate}"
    )

    print(
        f"Train batch size: "
        f"{config.per_device_train_batch_size}"
    )

    print(
        f"Validation batch size: "
        f"{config.per_device_eval_batch_size}"
    )

    print(
        f"Max tokenhossz: "
        f"{config.max_length}"
    )

    print(
        "\nHardver:"
    )

    if torch.cuda.is_available():
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )
    else:
        print(
            "CUDA GPU nem érhető el, "
            "a tanítás CPU-n fut."
        )

    print(
        "\nTrain és validation "
        "adathalmazok előkészítése..."
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

    print(
        f"Train rekordok: "
        f"{len(bundle.train_dataframe)}"
    )

    print(
        f"Validation rekordok: "
        f"{len(bundle.validation_dataframe)}"
    )

    print(
        "\nTrainer létrehozása..."
    )

    trainer, tokenizer = (
        create_context_aware_trainer(
            dataset_bundle=bundle,
            config=config,
            output_directory=(
                TRAINING_OUTPUT_DIRECTORY
            ),
        )
    )

    print(
        "\nFine-tuning indítása..."
    )

    train_result = trainer.train()

    print(
        "\nTanítás befejeződött."
    )

    print(
        "\nLegjobb modell validation "
        "kiértékelése..."
    )

    validation_metrics = trainer.evaluate()

    FINAL_MODEL_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "\nLegjobb modell mentése..."
    )

    trainer.save_model(
        str(FINAL_MODEL_DIRECTORY)
    )

    tokenizer.save_pretrained(
        str(FINAL_MODEL_DIRECTORY)
    )

    metrics_file = (
        FINAL_MODEL_DIRECTORY
        / "validation_metrics.json"
    )

    with metrics_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            validation_metrics,
            file,
            indent=4,
            ensure_ascii=False,
        )

    training_metrics_file = (
        FINAL_MODEL_DIRECTORY
        / "training_metrics.json"
    )

    with training_metrics_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            train_result.metrics,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(
        "\nVALIDATION EREDMÉNYEK"
    )

    print(
        "-" * 70
    )

    for metric_name, metric_value in (
        validation_metrics.items()
    ):
        print(
            f"{metric_name}: "
            f"{metric_value}"
        )

    print(
        "\nA fine-tuned modell mentési helye:"
    )

    print(
        FINAL_MODEL_DIRECTORY
    )


if __name__ == "__main__":
    main()
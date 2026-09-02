import inspect
from pathlib import Path

import torch
from transformers import (
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

from training.context_aware_dataset import (
    ContextAwareSentimentDataset,
)
from training.context_aware_model import (
    load_context_aware_model,
    load_context_aware_tokenizer,
)
from training.training_config import (
    ContextAwareTrainingConfig,
)
from training.training_dataset import (
    TrainingDatasetBundle,
)
from training.training_metrics import (
    compute_training_metrics,
)


def create_training_arguments(
    config: ContextAwareTrainingConfig,
    output_directory: str | Path,
) -> TrainingArguments:
    """
    Létrehozza a Hugging Face TrainingArguments
    konfigurációját.

    A kód kezeli az eltérő Transformers-verziók
    eval_strategy / evaluation_strategy elnevezését.
    """

    output_directory = Path(
        output_directory
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    arguments = {
        "output_dir": str(output_directory),

        "learning_rate": config.learning_rate,

        "num_train_epochs": (
            config.num_train_epochs
        ),

        "per_device_train_batch_size": (
            config.per_device_train_batch_size
        ),

        "per_device_eval_batch_size": (
            config.per_device_eval_batch_size
        ),

        "weight_decay": config.weight_decay,
        "warmup_ratio": config.warmup_ratio,

        "save_strategy": "epoch",
        "logging_strategy": "epoch",

        "load_best_model_at_end": True,

        "metric_for_best_model": (
            "eval_macro_f1"
        ),

        "greater_is_better": True,

        "save_total_limit": 2,

        "seed": config.seed,
        "data_seed": config.seed,

        # Windows alatt stabilabb.
        "dataloader_num_workers": 0,

        # Külső experiment tracker kikapcsolása.
        "report_to": [],

        # GPU esetén gyorsabb tanítás.
        "fp16": torch.cuda.is_available(),
    }

    training_argument_parameters = (
        inspect.signature(
            TrainingArguments.__init__
        ).parameters
    )

    if (
        "eval_strategy"
        in training_argument_parameters
    ):
        arguments["eval_strategy"] = "epoch"

    else:
        arguments[
            "evaluation_strategy"
        ] = "epoch"

    return TrainingArguments(
        **arguments
    )


def create_context_aware_trainer(
    dataset_bundle: TrainingDatasetBundle,
    config: ContextAwareTrainingConfig,
    output_directory: str | Path,
) -> tuple[
    Trainer,
    object,
]:
    """
    Létrehozza a context-aware fine-tuninghoz
    szükséges modellt, dataseteket és Trainert.
    """

    tokenizer = (
        load_context_aware_tokenizer(
            config.model_name
        )
    )

    model = (
        load_context_aware_model(
            config.model_name
        )
    )

    train_dataset = (
        ContextAwareSentimentDataset(
            dataframe=(
                dataset_bundle.train_dataframe
            ),
            tokenizer=tokenizer,
            max_length=config.max_length,
        )
    )

    validation_dataset = (
        ContextAwareSentimentDataset(
            dataframe=(
                dataset_bundle.validation_dataframe
            ),
            tokenizer=tokenizer,
            max_length=config.max_length,
        )
    )

    data_collator = (
        DataCollatorWithPadding(
            tokenizer=tokenizer,
            return_tensors="pt",
        )
    )

    training_arguments = (
        create_training_arguments(
            config=config,
            output_directory=output_directory,
        )
    )

    trainer = Trainer(
        model=model,
        args=training_arguments,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_training_metrics,
    )

    return trainer, tokenizer
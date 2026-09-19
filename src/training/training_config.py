from dataclasses import dataclass


@dataclass(frozen=True)
class ContextAwareTrainingConfig:
    """
    A context-aware huBERT fine-tuning konfigurációja.
    """

    model_name: str = "NYTK/sentiment-hts5-hubert-hungarian"

    max_length: int = 128
    num_labels: int = 3

    # A tokenizálási diagnosztika alapján
    # az emojik szöveges reprezentációját használjuk.
    emoji_mode: str = "text"

    # A validációs kísérletek alapján kiválasztott
    # végleges fine-tuning paraméterek.
    learning_rate: float = 2e-5
    num_train_epochs: int = 4

    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 8

    weight_decay: float = 0.01
    warmup_ratio: float = 0.10

    seed: int = 42
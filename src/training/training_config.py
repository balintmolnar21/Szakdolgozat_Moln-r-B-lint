from dataclasses import dataclass


@dataclass(frozen=True)
class ContextAwareTrainingConfig:
    """
    A context-aware huBERT fine-tuning
    alapvető konfigurációja.
    """

    model_name: str = "NYTK/sentiment-hts5-hubert-hungarian"

    # Első kísérletben az eredeti sentimentmodell
    # dokumentált szekvenciahosszát tartjuk meg.
    max_length: int = 128

    num_labels: int = 3

    # Első kísérlet: nyers Unicode emojik.
    emoji_mode: str = "raw"
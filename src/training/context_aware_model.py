from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from training.training_dataset import (
    ID_TO_LABEL,
    LABEL_TO_ID,
)


def load_context_aware_tokenizer(
    model_name: str,
):
    """
    Betölti a context-aware modellhez használt
    huBERT tokenizert.
    """

    return AutoTokenizer.from_pretrained(
        model_name
    )


def load_context_aware_model(
    model_name: str,
):
    """
    Betölti a jelenlegi huBERT sentimentmodellt,
    de új háromosztályos classification head-del.

    Az encoder előtanított/sentimentre finomhangolt
    súlyai megmaradnak, a háromosztályos kimeneti
    réteg újrainicializálódik.
    """

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            model_name,
            num_labels=3,
            id2label=ID_TO_LABEL,
            label2id=LABEL_TO_ID,
            problem_type="single_label_classification",
            ignore_mismatched_sizes=True,
        )
    )

    return model
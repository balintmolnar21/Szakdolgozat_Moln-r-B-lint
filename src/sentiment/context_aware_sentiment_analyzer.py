from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


LABELS = {
    0: "negative",
    1: "neutral",
    2: "positive",
}


@dataclass
class ContextAwareSentimentResult:
    """
    Egyetlen poszt-komment pár sentiment eredménye.
    """

    raw_label: str
    final_label: str
    confidence: float
    threshold_applied: bool


class ContextAwareSentimentAnalyzer:
    def __init__(
        self,
        model_path: str | Path = "models/context_aware_hubert_text",
        max_length: int = 128,
        confidence_threshold: float = 0.60,
    ):
        self.model_path = Path(model_path)
        self.max_length = max_length
        self.confidence_threshold = confidence_threshold

        self.device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # Ugyanazt a tokenizert használjuk,
        # amelyet a fine-tuning során is alkalmaztunk.
        self.tokenizer = AutoTokenizer.from_pretrained(
            "NYTK/sentiment-hts5-hubert-hungarian"
        )

        # A fine-tuning során létrehozott
        # 3-osztályos modell lokális betöltése.
        self.model = (
            AutoModelForSequenceClassification.from_pretrained(
                self.model_path
            )
        )

        self.model.to(self.device)
        self.model.eval()

    @staticmethod
    def _prepare_text(
        text: str | None,
    ) -> str:
        """
        Biztonságosan szöveggé alakítja a bemenetet.
        """

        if text is None:
            return ""

        return str(text).strip()

    def _get_label(
        self,
        label_id: int,
    ) -> str:
        """
        A numerikus modellkimenetet sentiment címkévé alakítja.
        """

        model_label = self.model.config.id2label.get(
            label_id
        )

        if model_label is not None:
            normalized_label = (
                str(model_label)
                .strip()
                .lower()
            )

            if normalized_label in {
                "negative",
                "neutral",
                "positive",
            }:
                return normalized_label

        if label_id in LABELS:
            return LABELS[label_id]

        raise ValueError(
            "Ismeretlen sentiment label ID: "
            f"{label_id}"
        )

    def _apply_confidence_threshold(
        self,
        label: str,
        confidence: float,
    ) -> tuple[str, bool]:
        """
        A confidence threshold alkalmazása.

        A positive vagy negative predikció neutral lesz,
        ha a confidence kisebb a beállított küszöbnél.
        """

        should_change = (
            label in {"positive", "negative"}
            and confidence < self.confidence_threshold
        )

        if should_change:
            return "neutral", True

        return label, False

    def predict(
        self,
        post_text: str | None,
        comment_text: str | None,
    ) -> ContextAwareSentimentResult:
        """
        Egyetlen poszt-komment pár sentiment elemzése.
        """

        post_text = self._prepare_text(
            post_text
        )

        comment_text = self._prepare_text(
            comment_text
        )

        if not comment_text:
            return ContextAwareSentimentResult(
                raw_label="neutral",
                final_label="neutral",
                confidence=0.0,
                threshold_applied=False,
            )

        inputs = self.tokenizer(
            post_text,
            comment_text,
            return_tensors="pt",
            truncation="longest_first",
            max_length=self.max_length,
            padding=True,
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(
                **inputs
            )

            probabilities = torch.softmax(
                outputs.logits,
                dim=1,
            )

            confidence, predicted_class_id = (
                torch.max(
                    probabilities,
                    dim=1,
                )
            )

        label_id = int(
            predicted_class_id.item()
        )

        confidence_value = float(
            confidence.item()
        )

        raw_label = self._get_label(
            label_id
        )

        final_label, threshold_applied = (
            self._apply_confidence_threshold(
                label=raw_label,
                confidence=confidence_value,
            )
        )

        return ContextAwareSentimentResult(
            raw_label=raw_label,
            final_label=final_label,
            confidence=confidence_value,
            threshold_applied=threshold_applied,
        )

    def analyze_dataframe(
        self,
        dataframe: pd.DataFrame,
        post_column: str = "cleaned_post_text",
        comment_column: str = "cleaned_comment_text",
        limit: int | None = None,
    ) -> pd.DataFrame:
        """
        Egy teljes DataFrame poszt-komment párjain
        futtatja a context-aware sentiment modellt.
        """

        required_columns = {
            post_column,
            comment_column,
        }

        missing_columns = (
            required_columns
            .difference(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "A context-aware sentiment elemzéshez "
                "szükséges oszlopok közül hiányzik: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        result_df = dataframe.copy()

        result_df["finetuned_label"] = None
        result_df["finetuned_confidence"] = None
        result_df["final_sentiment_label"] = None
        result_df["threshold_applied"] = False

        # Kompatibilitási oszlopok a meglévő
        # statisztikai és kiértékelési modulokhoz.
        result_df["model_label"] = None
        result_df["confidence"] = None

        rows_to_process = result_df.index

        if limit is not None:
            rows_to_process = result_df.index[:limit]

        for index in rows_to_process:
            result = self.predict(
                post_text=result_df.at[
                    index,
                    post_column,
                ],
                comment_text=result_df.at[
                    index,
                    comment_column,
                ],
            )

            result_df.at[
                index,
                "finetuned_label",
            ] = result.raw_label

            result_df.at[
                index,
                "finetuned_confidence",
            ] = result.confidence

            result_df.at[
                index,
                "final_sentiment_label",
            ] = result.final_label

            result_df.at[
                index,
                "threshold_applied",
            ] = result.threshold_applied

            result_df.at[
                index,
                "model_label",
            ] = result.final_label

            result_df.at[
                index,
                "confidence",
            ] = result.confidence

        return result_df
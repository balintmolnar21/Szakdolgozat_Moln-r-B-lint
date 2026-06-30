from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


@dataclass
class SentimentResult:
    label: str
    confidence: float
    original_label: str


class HuBERTSentimentAnalyzer:
    def __init__(
        self,
        model_name: str = "NYTK/sentiment-hts5-hubert-hungarian",
        max_length: int = 128,
    ):
        self.model_name = model_name
        self.max_length = max_length

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )

        self.model.to(self.device)
        self.model.eval()
        
    

    def _normalize_label(self, label_id: int) -> str:
        label_mapping = {
            0: "negative",
            1: "negative",
            2: "neutral",
            3: "positive",
            4: "positive",
        }

        return label_mapping.get(label_id, "unknown")

    def predict(self, text: str | None) -> SentimentResult:
        if text is None or str(text).strip() == "":
            return SentimentResult(
                label="neutral",
                confidence=0.0,
                original_label="empty_text",
            )

        text = str(text)

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.max_length,
        )

        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            confidence, predicted_class_id = torch.max(probabilities, dim=1)

        label_id = int(predicted_class_id.item())
        normalized_label = self._normalize_label(label_id)

        original_label = self.model.config.id2label.get(
            label_id,
            f"LABEL_{label_id}",
        )

        return SentimentResult(
            label=normalized_label,
            confidence=float(confidence.item()),
            original_label=original_label,
        )
        
    def analyze_dataframe_column(
        self,
        df,
        source_column: str,
        label_column: str,
        confidence_column: str,
        original_label_column: str | None = None,
        limit: int | None = None,
        ):
        df = df.copy()

        if source_column not in df.columns:
            raise ValueError(
                f"A megadott forrásoszlop nem található az adathalmazban: {source_column}"
            )

        df[label_column] = None
        df[confidence_column] = None

        if original_label_column is not None:
            df[original_label_column] = None

        rows_to_process = df.index

        if limit is not None:
            rows_to_process = df.index[:limit]

        for index in rows_to_process:
            text = df.at[index, source_column]
            result = self.predict(text)

            df.at[index, label_column] = result.label
            df.at[index, confidence_column] = result.confidence

            if original_label_column is not None:
                df.at[index, original_label_column] = result.original_label

        return df

if __name__ == "__main__":
    analyzer = HuBERTSentimentAnalyzer()

    sample_texts = [
        "Nagyon örülök ennek az eredménynek!",
        "Ez borzalmas döntés volt.",
        "Rendben, tudomásul vettem.",
        "Köszönöm! [kék szív emoji]",
        "Ez elfogadhatatlan és felháborító.",
    ]

    for text in sample_texts:
        result = analyzer.predict(text)

        print("\nSzöveg:")
        print(text)
        print("Normalizált címke:", result.label)
        print("Eredeti modellcímke:", result.original_label)
        print("Konfidencia:", round(result.confidence, 4))
import pandas as pd
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerBase


REQUIRED_CONTEXT_COLUMNS = {
    "processed_post_text",
    "processed_comment_text",
    "label",
}


class ContextAwareSentimentDataset(Dataset):
    """
    PyTorch Dataset a poszt + komment alapú
    sentiment fine-tuninghoz.

    A tokenizer a posztot és a kommentet
    két külön szövegszekvenciaként kapja meg.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        tokenizer: PreTrainedTokenizerBase,
        max_length: int = 128,
    ):
        self._validate_dataframe(
            dataframe
        )

        if max_length <= 0:
            raise ValueError(
                "A max_length értékének pozitívnak kell lennie."
            )

        self.dataframe = (
            dataframe
            .reset_index(drop=True)
            .copy()
        )

        self.tokenizer = tokenizer
        self.max_length = max_length

    @staticmethod
    def _validate_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Ellenőrzi a tokenizáláshoz szükséges
        oszlopokat és adatokat.
        """

        if dataframe.empty:
            raise ValueError(
                "A tokenizáláshoz kapott adathalmaz üres."
            )

        missing_columns = (
            REQUIRED_CONTEXT_COLUMNS
            .difference(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "A context-aware tokenizáláshoz "
                "szükséges oszlopok közül hiányzik: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        for column_name in [
            "processed_post_text",
            "processed_comment_text",
        ]:
            empty_mask = (
                dataframe[column_name]
                .fillna("")
                .astype(str)
                .str.strip()
                .eq("")
            )

            if empty_mask.any():
                raise ValueError(
                    f"A(z) {column_name} oszlop "
                    f"{int(empty_mask.sum())} üres értéket tartalmaz."
                )

        invalid_label_mask = (
            ~dataframe["label"].isin(
                [0, 1, 2]
            )
        )

        if invalid_label_mask.any():
            invalid_labels = (
                dataframe.loc[
                    invalid_label_mask,
                    "label",
                ]
                .unique()
                .tolist()
            )

            raise ValueError(
                "Nem támogatott numerikus sentimentcímke: "
                + ", ".join(
                    str(value)
                    for value in invalid_labels
                )
            )

    def __len__(self) -> int:
        return len(
            self.dataframe
        )

    def __getitem__(
        self,
        index: int,
    ) -> dict:
        """
        Egyetlen poszt-komment pár tokenizálása.

        A tokenizer két szövegszekvenciát kap:

        sequence A = poszt
        sequence B = komment
        """

        row = self.dataframe.iloc[
            index
        ]

        post_text = str(
            row["processed_post_text"]
        )

        comment_text = str(
            row["processed_comment_text"]
        )

        encoding = self.tokenizer(
            post_text,
            comment_text,
            truncation="longest_first",
            max_length=self.max_length,
            padding=False,
        )

        encoding["labels"] = int(
            row["label"]
        )

        return encoding
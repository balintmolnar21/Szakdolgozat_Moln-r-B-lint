from dataclasses import dataclass

import pandas as pd
from transformers import PreTrainedTokenizerBase


@dataclass
class TokenizationDiagnosticResult:
    dataset_name: str
    emoji_mode: str
    record_count: int
    records_with_unk: int
    records_with_unk_ratio: float
    total_unk_tokens: int
    average_token_length: float
    maximum_token_length: int
    records_over_max_length: int
    records_over_max_length_ratio: float


def analyze_tokenization(
    dataframe: pd.DataFrame,
    tokenizer: PreTrainedTokenizerBase,
    dataset_name: str,
    emoji_mode: str,
    max_length: int,
) -> TokenizationDiagnosticResult:
    """
    Egy előkészített context-aware adathalmaz
    tokenizálási tulajdonságait vizsgálja.

    Megméri:
    - hány rekordban jelenik meg [UNK],
    - összesen hány [UNK] token keletkezik,
    - a poszt + komment párok tokenhosszát,
    - hány rekord lenne hosszabb a megadott max_length értéknél.
    """

    required_columns = {
        "processed_post_text",
        "processed_comment_text",
    }

    missing_columns = required_columns.difference(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "A tokenizálási diagnosztikához hiányzó oszlopok: "
            + ", ".join(sorted(missing_columns))
        )

    if dataframe.empty:
        raise ValueError(
            f"A(z) {dataset_name} adathalmaz üres."
        )

    unk_token_id = tokenizer.unk_token_id

    records_with_unk = 0
    total_unk_tokens = 0

    token_lengths: list[int] = []
    records_over_max_length = 0

    for _, row in dataframe.iterrows():
        post_text = str(
            row["processed_post_text"]
        )

        comment_text = str(
            row["processed_comment_text"]
        )

        # Fontos: itt még NEM csonkolunk.
        # Így meg tudjuk mérni az eredeti tokenhosszt.
        encoding = tokenizer(
            post_text,
            comment_text,
            truncation=False,
            padding=False,
            add_special_tokens=True,
        )

        input_ids = encoding["input_ids"]

        token_length = len(input_ids)

        token_lengths.append(
            token_length
        )

        if token_length > max_length:
            records_over_max_length += 1

        if unk_token_id is not None:
            unk_count = input_ids.count(
                unk_token_id
            )

            total_unk_tokens += unk_count

            if unk_count > 0:
                records_with_unk += 1

    record_count = len(
        dataframe
    )

    average_token_length = (
        sum(token_lengths) / record_count
    )

    maximum_token_length = max(
        token_lengths
    )

    records_with_unk_ratio = (
        records_with_unk
        / record_count
        * 100
    )

    records_over_max_length_ratio = (
        records_over_max_length
        / record_count
        * 100
    )

    return TokenizationDiagnosticResult(
        dataset_name=dataset_name,
        emoji_mode=emoji_mode,
        record_count=record_count,
        records_with_unk=records_with_unk,
        records_with_unk_ratio=round(
            records_with_unk_ratio,
            2,
        ),
        total_unk_tokens=total_unk_tokens,
        average_token_length=round(
            average_token_length,
            2,
        ),
        maximum_token_length=maximum_token_length,
        records_over_max_length=records_over_max_length,
        records_over_max_length_ratio=round(
            records_over_max_length_ratio,
            2,
        ),
    )


def diagnostic_result_to_dict(
    result: TokenizationDiagnosticResult,
) -> dict:
    """
    A diagnosztikai eredményt DataFrame-be
    könnyen illeszthető szótárrá alakítja.
    """

    return {
        "dataset": result.dataset_name,
        "emoji_mode": result.emoji_mode,
        "record_count": result.record_count,
        "records_with_unk": result.records_with_unk,
        "records_with_unk_ratio": result.records_with_unk_ratio,
        "total_unk_tokens": result.total_unk_tokens,
        "average_token_length": result.average_token_length,
        "maximum_token_length": result.maximum_token_length,
        "records_over_max_length": (
            result.records_over_max_length
        ),
        "records_over_max_length_ratio": (
            result.records_over_max_length_ratio
        ),
    }


def create_diagnostics_dataframe(
    results: list[TokenizationDiagnosticResult],
) -> pd.DataFrame:
    """
    Több diagnosztikai eredményből
    összesítő DataFrame-et készít.
    """

    return pd.DataFrame(
        [
            diagnostic_result_to_dict(result)
            for result in results
        ]
    )
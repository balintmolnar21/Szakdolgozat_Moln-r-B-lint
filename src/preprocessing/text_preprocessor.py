import re

import pandas as pd

from preprocessing.emoji_lib import (
    replace_emojis,
    validate_emoji_mode,
)


def normalize_whitespace(
    text: str,
) -> str:
    """
    Az egymást követő whitespace karaktereket
    egyetlen szóközre normalizálja.
    """

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def replace_urls(
    text: str,
) -> str:
    """
    Az URL-eket egységes [URL] tokenre cseréli.
    """

    url_pattern = (
        r"https?://\S+|www\.\S+"
    )

    return re.sub(
        url_pattern,
        "[URL]",
        text,
    )


def clean_text(
    text: str | None,
    emoji_mode: str = "bracketed",
) -> str:
    """
    Egy szöveg általános előfeldolgozását végzi.

    emoji_mode:
        raw
            Az Unicode emojik változatlanul maradnak.

        text
            Az emojik zárójelek nélküli
            szöveges leírásra cserélődnek.

        bracketed
            Az emojik szögletes zárójeles
            tokenre cserélődnek.
    """

    if text is None:
        return ""

    validate_emoji_mode(
        emoji_mode
    )

    text = str(text)

    text = replace_urls(
        text
    )

    text = normalize_whitespace(
        text
    )

    text = replace_emojis(
        text,
        mode=emoji_mode,
    )

    # Az emoji-helyettesítés során bekerülő
    # extra szóközök normalizálása.
    text = normalize_whitespace(
        text
    )

    return text


def preprocess_text_column(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
    emoji_mode: str = "bracketed",
) -> pd.DataFrame:
    """
    Egy DataFrame-oszlop szövegeit dolgozza fel.
    """

    df = df.copy()

    if source_column not in df.columns:
        df[target_column] = ""
        return df

    df[target_column] = df[
        source_column
    ].apply(
        lambda text: clean_text(
            text,
            emoji_mode=emoji_mode,
        )
    )

    return df


def preprocess_text_fields(
    df: pd.DataFrame,
    emoji_mode: str = "bracketed",
) -> pd.DataFrame:
    """
    A rendszer összes releváns szöveges
    mezőjét előfeldolgozza.
    """

    validate_emoji_mode(
        emoji_mode
    )

    df = df.copy()

    column_pairs = {
        "comment_text": "cleaned_comment_text",
        "post_text": "cleaned_post_text",
        "image_context_text": "cleaned_image_context_text",
        "video_context_text": "cleaned_video_context_text",
    }

    for source_column, target_column in column_pairs.items():
        df = preprocess_text_column(
            df=df,
            source_column=source_column,
            target_column=target_column,
            emoji_mode=emoji_mode,
        )

    return df
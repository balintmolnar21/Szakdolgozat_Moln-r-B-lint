import re
import pandas as pd


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def replace_urls(text: str) -> str:
    url_pattern = r"https?://\S+|www\.\S+"
    return re.sub(url_pattern, "[URL]", text)


def clean_text(text: str | None) -> str:
    if text is None:
        return ""

    text = str(text)
    text = replace_urls(text)
    text = normalize_whitespace(text)

    return text


def preprocess_text_column(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
) -> pd.DataFrame:
    df = df.copy()

    if source_column not in df.columns:
        df[target_column] = ""
        return df

    df[target_column] = df[source_column].apply(clean_text)

    return df


def preprocess_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    column_pairs = {
        "comment_text": "cleaned_comment_text",
        "post_text": "cleaned_post_text",
        "image_context_text": "cleaned_image_context_text",
        "video_context_text": "cleaned_video_context_text",
    }

    for source_column, target_column in column_pairs.items():
        df = preprocess_text_column(df, source_column, target_column)

    return df

## tesztelési lehetőség
'''
if __name__ == "__main__":
    sample_text = """
    Ez egy komment.


    https://example.com
    """

    cleaned_sample_text = clean_text(sample_text)

    print("Eredeti szöveg:")
    print(sample_text)

    print("Tisztított szöveg:")
    print(cleaned_sample_text)
'''
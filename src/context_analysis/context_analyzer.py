from dataclasses import dataclass

import pandas as pd


SUPPORTED_POST_SENTIMENTS = {
    "positive",
    "negative",
    "neutral",
}

SUPPORTED_COMMENT_SENTIMENTS = {
    "positive",
    "negative",
    "neutral",
    "mixed",
    "no_data",
}


@dataclass
class ContextAnalysisResult:
    

    reaction_type: str
    alignment: str
    interpretation: str


def validate_context_columns(
    df: pd.DataFrame,
) -> None:
    
    required_columns = {
        "post_id",
        "post_sentiment_label",
        "dominant_comment_sentiment",
        "positive_ratio",
        "negative_ratio",
        "neutral_ratio",
    }

    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing_columns_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            "A kontextuselemzéshez szükséges oszlopok közül "
            f"az alábbiak hiányoznak: {missing_columns_text}"
        )


def normalize_sentiment_label(
    value,
) -> str:
    
    if value is None or pd.isna(value):
        return ""

    return str(value).strip().lower()


def normalize_ratio(
    value,
) -> float:
    
    if value is None or pd.isna(value):
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def determine_context_analysis(
    post_sentiment: str,
    dominant_comment_sentiment: str,
    positive_ratio: float,
    negative_ratio: float,
    neutral_ratio: float,
) -> ContextAnalysisResult:
    
    post_sentiment = normalize_sentiment_label(post_sentiment)
    dominant_comment_sentiment = normalize_sentiment_label(
        dominant_comment_sentiment
    )

    positive_ratio = normalize_ratio(positive_ratio)
    negative_ratio = normalize_ratio(negative_ratio)
    neutral_ratio = normalize_ratio(neutral_ratio)

    ratio_summary = (
        f"A kommentek megoszlása: {positive_ratio:.2f}% pozitív, "
        f"{negative_ratio:.2f}% negatív és "
        f"{neutral_ratio:.2f}% semleges."
    )

    if post_sentiment not in SUPPORTED_POST_SENTIMENTS:
        return ContextAnalysisResult(
            reaction_type="uncertain",
            alignment="unclear",
            interpretation=(
                "A poszt sentiment címkéje nem áll rendelkezésre vagy "
                "nem támogatott, ezért a kommentek és a poszt közötti "
                f"kapcsolat nem értelmezhető megbízhatóan. {ratio_summary}"
            ),
        )

    if dominant_comment_sentiment not in SUPPORTED_COMMENT_SENTIMENTS:
        return ContextAnalysisResult(
            reaction_type="uncertain",
            alignment="unclear",
            interpretation=(
                "A kommentek domináns sentiment címkéje nem áll "
                "rendelkezésre vagy nem támogatott, ezért a kontextuális "
                f"kapcsolat nem határozható meg. {ratio_summary}"
            ),
        )

    if dominant_comment_sentiment == "no_data":
        return ContextAnalysisResult(
            reaction_type="uncertain",
            alignment="unclear",
            interpretation=(
                "A poszthoz nem áll rendelkezésre elegendő feldolgozható "
                "komment, ezért a fogadtatás nem értelmezhető."
            ),
        )

    if dominant_comment_sentiment == "mixed":
        return ContextAnalysisResult(
            reaction_type="mixed_response",
            alignment="mixed",
            interpretation=(
                "A kommentek között nem alakult ki egyértelműen domináns "
                "hangulati irány, ezért a poszt fogadtatása vegyesnek "
                f"tekinthető. {ratio_summary}"
            ),
        )

    if dominant_comment_sentiment == "neutral":
        return ContextAnalysisResult(
            reaction_type="neutral_response",
            alignment="unclear",
            interpretation=(
                f"A poszt {post_sentiment} hangvételű, miközben a "
                "kommentek között a semleges kategória dominál. Ez "
                "visszafogott, információközpontú vagy érzelmileg nem "
                f"egyértelmű reakciókra utalhat. {ratio_summary}"
            ),
        )

    if post_sentiment == "positive":
        if dominant_comment_sentiment == "positive":
            return ContextAnalysisResult(
                reaction_type="aligned_positive",
                alignment="aligned",
                interpretation=(
                    "A poszt pozitív hangvételű, és a kommentek között "
                    "is a pozitív kategória dominál. Ez azonos irányú, "
                    f"támogató reakcióra utalhat. {ratio_summary}"
                ),
            )

        if dominant_comment_sentiment == "negative":
            return ContextAnalysisResult(
                reaction_type="critical_response",
                alignment="opposite",
                interpretation=(
                    "A poszt pozitív hangvételű, de a kommentek között "
                    "a negatív kategória dominál. Ez kritikus vagy "
                    f"elutasító fogadtatásra utalhat. {ratio_summary}"
                ),
            )

    if post_sentiment == "negative":
        if dominant_comment_sentiment == "negative":
            return ContextAnalysisResult(
                reaction_type="aligned_negative",
                alignment="aligned",
                interpretation=(
                    "A poszt negatív hangvételű, és a kommentek között "
                    "is a negatív kategória dominál. Ez azonos irányú "
                    "kritikus reakciót vagy problémaérzékelést jelezhet, "
                    "de önmagában nem bizonyítja, hogy a kommentelők "
                    f"egyetértenek a poszt állításával. {ratio_summary}"
                ),
            )

        if dominant_comment_sentiment == "positive":
            return ContextAnalysisResult(
                reaction_type="supportive_response",
                alignment="opposite",
                interpretation=(
                    "A poszt negatív hangvételű, miközben a kommentek "
                    "között a pozitív kategória dominál. Ez támogató vagy "
                    "pozitív visszacsatolásra utalhat egy kritikus témával "
                    f"kapcsolatban. {ratio_summary}"
                ),
            )

    if post_sentiment == "neutral":
        if dominant_comment_sentiment == "positive":
            return ContextAnalysisResult(
                reaction_type="positive_response_to_neutral",
                alignment="different",
                interpretation=(
                    "A poszt semleges hangvételű, miközben a kommentek "
                    "között a pozitív kategória dominál. Ez kedvező "
                    f"közönségreakcióra utalhat. {ratio_summary}"
                ),
            )

        if dominant_comment_sentiment == "negative":
            return ContextAnalysisResult(
                reaction_type="negative_response_to_neutral",
                alignment="different",
                interpretation=(
                    "A poszt semleges hangvételű, miközben a kommentek "
                    "között a negatív kategória dominál. Ez kritikus vagy "
                    f"kedvezőtlen közönségreakcióra utalhat. {ratio_summary}"
                ),
            )

    return ContextAnalysisResult(
        reaction_type="uncertain",
        alignment="unclear",
        interpretation=(
            "A rendelkezésre álló sentiment eredmények alapján nem "
            "határozható meg egyértelmű kontextuális kapcsolat. "
            f"{ratio_summary}"
        ),
    )


def analyze_post_contexts(
    post_statistics_df: pd.DataFrame,
) -> pd.DataFrame:
    
    validate_context_columns(post_statistics_df)

    analyzed_df = post_statistics_df.copy()

    reaction_types: list[str] = []
    alignments: list[str] = []
    interpretations: list[str] = []

    for _, row in analyzed_df.iterrows():
        result = determine_context_analysis(
            post_sentiment=row["post_sentiment_label"],
            dominant_comment_sentiment=row[
                "dominant_comment_sentiment"
            ],
            positive_ratio=row["positive_ratio"],
            negative_ratio=row["negative_ratio"],
            neutral_ratio=row["neutral_ratio"],
        )

        reaction_types.append(result.reaction_type)
        alignments.append(result.alignment)
        interpretations.append(result.interpretation)

    analyzed_df["context_reaction_type"] = reaction_types
    analyzed_df["context_alignment"] = alignments
    analyzed_df["context_interpretation"] = interpretations

    return analyzed_df

#tesztelésre
if __name__ == "__main__":
    sample_post_statistics_df = pd.DataFrame(
        {
            "post_id": [
                "P1",
                "P2",
                "P3",
                "P4",
                "P5",
            ],
            "post_type": [
                "image",
                "video",
                "image",
                "image",
                "video",
            ],
            "post_sentiment_label": [
                "positive",
                "positive",
                "negative",
                "negative",
                "neutral",
            ],
            "dominant_comment_sentiment": [
                "positive",
                "negative",
                "negative",
                "positive",
                "mixed",
            ],
            "positive_ratio": [
                65.0,
                20.0,
                15.0,
                60.0,
                40.0,
            ],
            "negative_ratio": [
                20.0,
                65.0,
                70.0,
                25.0,
                40.0,
            ],
            "neutral_ratio": [
                15.0,
                15.0,
                15.0,
                15.0,
                20.0,
            ],
        }
    )

    sample_context_analysis_df = analyze_post_contexts(
        sample_post_statistics_df
    )

    preview_columns = [
        "post_id",
        "post_sentiment_label",
        "dominant_comment_sentiment",
        "context_reaction_type",
        "context_alignment",
        "context_interpretation",
    ]

    print("Kontextuselemzés teszteredménye:")
    print(sample_context_analysis_df[preview_columns])
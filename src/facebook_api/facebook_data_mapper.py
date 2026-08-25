from typing import Any

import pandas as pd


def create_post_context_dataframe(
    post_data: dict[str, Any],
) -> pd.DataFrame:
    """
    Egy Facebook-poszt adataiból létrehozza
    a pipeline számára használható posztkontextus DataFrame-et.

    Args:
        post_data:
            A FacebookPostFetcher által normalizált posztadat.

    Returns:
        Egyetlen sort tartalmazó DataFrame.
    """
    post_id = post_data.get("post_id")

    if not post_id:
        raise ValueError(
            "A Facebook-poszt nem tartalmaz post_id értéket."
        )

    return pd.DataFrame(
        [
            {
                "post_id": post_id,
                "post_type": "facebook_post",
                "post_link": post_data.get(
                    "post_link",
                    "",
                ),
                "post_text": post_data.get(
                    "post_text",
                    "",
                ),
                "image_context_text": "",
                "video_context_text": "",
                "post_context_note": (
                    "Facebook Graph API-ból lekért bejegyzés."
                ),
            }
        ]
    )


def create_comments_dataframe(
    comments: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    A FacebookCommentFetcher által visszaadott kommentlistát
    a validációs adatszerkezethez illeszkedő DataFrame-mé alakítja.

    A valós Facebook-kommentekhez nincs kézi címke,
    ezért a manual_label mező üres marad.

    Args:
        comments:
            Normalizált Facebook-kommentek listája.

    Returns:
        Kommentadatokat tartalmazó DataFrame.
    """
    columns = [
        "post_id",
        "post_type",
        "post_link",
        "comment_id",
        "comment_text",
        "manual_label",
        "model_label",
        "note",
        "confidence",
        "original_model_label",
    ]

    if not comments:
        return pd.DataFrame(
            columns=columns
        )

    rows: list[dict[str, Any]] = []

    for comment in comments:
        comment_id = comment.get(
            "comment_id"
        )

        post_id = comment.get(
            "post_id"
        )

        if not post_id:
            raise ValueError(
                "Az egyik Facebook-kommenthez nem tartozik post_id."
            )

        if not comment_id:
            raise ValueError(
                "Az egyik Facebook-komment nem tartalmaz comment_id-t."
            )

        rows.append(
            {
                "post_id": post_id,
                "post_type": "facebook_post",
                "post_link": "",
                "comment_id": comment_id,
                "comment_text": comment.get(
                    "comment_text",
                    "",
                ),
                "manual_label": None,
                "model_label": None,
                "note": (
                    "Facebook Graph API-ból lekért komment."
                ),
                "confidence": None,
                "original_model_label": None,
            }
        )

    return pd.DataFrame(
        rows,
        columns=columns,
    )
from typing import Any

import pandas as pd


def create_post_context_dataframe(
    post_data: dict[str, Any],
) -> pd.DataFrame:
    """
    Egyetlen Facebook-posztból létrehozza
    a pipeline által használt posztkontextus DataFrame-et.

    A függvény kompatibilitási okból megmarad,
    például egy konkrét poszt külön elemzéséhez.
    """

    return create_posts_context_dataframe(
        [post_data]
    )


def create_posts_context_dataframe(
    posts: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Több Facebook-posztból létrehozza a pipeline
    által használt posztkontextus DataFrame-et.
    """

    columns = [
        "post_id",
        "post_type",
        "post_link",
        "post_text",
        "image_context_text",
        "video_context_text",
        "note",
    ]

    if not posts:
        return pd.DataFrame(
            columns=columns
        )

    rows: list[dict[str, Any]] = []

    for post_data in posts:
        post_id = post_data.get(
            "post_id"
        )

        if not post_id:
            raise ValueError(
                "Az egyik Facebook-poszt nem tartalmaz "
                "post_id értéket."
            )

        rows.append(
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
                "note": (
                    "Facebook Graph API-ból "
                    "lekért bejegyzés."
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=columns,
    )


def create_comments_dataframe(
    comments: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Facebook-kommentekből létrehozza a pipeline
    által használt komment DataFrame-et.
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
                "Az egyik Facebook-kommenthez "
                "nem tartozik post_id."
            )

        if not comment_id:
            raise ValueError(
                "Az egyik Facebook-komment nem "
                "tartalmaz comment_id-t."
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
                # Facebook API módban nincs
                # ember által megadott sentimentcímke.
                "manual_label": None,
                "model_label": None,
                "note": (
                    "Facebook Graph API-ból "
                    "lekért komment."
                ),
                "confidence": None,
                "original_model_label": None,
            }
        )

    return pd.DataFrame(
        rows,
        columns=columns,
    )
from typing import Any

from facebook_api.graph_api_client import FacebookGraphAPIClient


class FacebookCommentFetcher:
    """
    Facebook-posztokhoz tartozó kommentek és
    kommentválaszok lekéréséért felelős osztály.

    A főkommentek és a válaszkommentek a feldolgozás
    során egységes kommentlistába kerülnek.
    """

    DEFAULT_FIELDS = [
        "id",
        "message",
        "created_time",
    ]

    def __init__(
        self,
        client: FacebookGraphAPIClient,
    ) -> None:
        self.client = client

    def _fetch_paginated_comments(
        self,
        endpoint: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Egy /comments végpont összes lapozott
        eredményét lekéri.

        Használható:
        - poszt főkommentjeinek lekérésére,
        - kommentekre adott válaszok lekérésére.
        """

        response = self.client.get(
            endpoint=endpoint,
            params={
                "fields": ",".join(
                    self.DEFAULT_FIELDS
                ),
                "limit": limit,
            },
        )

        comments: list[dict[str, Any]] = []

        while True:
            comments.extend(
                response.get(
                    "data",
                    [],
                )
            )

            next_url = (
                response
                .get("paging", {})
                .get("next")
            )

            if not next_url:
                break

            response = self.client.get_from_url(
                next_url
            )

        return comments

    @staticmethod
    def _normalize_comment(
        comment_data: dict[str, Any],
        post_id: str,
    ) -> dict[str, Any]:
        """
        Egy Facebook-kommentet a projekt belső
        adatformátumára alakít.
        """

        return {
            "post_id": post_id,
            "comment_id": comment_data.get(
                "id"
            ),
            "comment_text": comment_data.get(
                "message",
                "",
            ),
            "created_time": comment_data.get(
                "created_time"
            ),
        }

    def fetch_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Lekéri egy Facebook-poszt összes elérhető
        főkommentjét és az azokra adott válaszokat.

        A főkommentek és válaszok ugyanabba a listába
        kerülnek, mert a sentiment pipeline mindegyiket
        a hozzájuk tartozó poszt kontextusában elemzi.

        Minden rekord ugyanazt az eredeti post_id-t kapja.
        """

        normalized_post_id = post_id.strip()

        if not normalized_post_id:
            raise ValueError(
                "A Facebook post_id nem lehet üres."
            )

        if limit < 1:
            raise ValueError(
                "A kommentlekérési limitnek "
                "legalább 1-nek kell lennie."
            )

        # -----------------------------------------------------
        # 1. Főkommentek lekérése
        # -----------------------------------------------------

        root_comments = self._fetch_paginated_comments(
            endpoint=f"{normalized_post_id}/comments",
            limit=limit,
        )

        all_comments: list[dict[str, Any]] = []

        # A duplikációk kiszűrésére.
        seen_comment_ids: set[str] = set()

        # -----------------------------------------------------
        # 2. Főkommentek feldolgozása
        # -----------------------------------------------------

        for root_comment in root_comments:
            root_comment_id = root_comment.get(
                "id"
            )

            if not root_comment_id:
                continue

            if root_comment_id not in seen_comment_ids:
                all_comments.append(
                    self._normalize_comment(
                        comment_data=root_comment,
                        post_id=normalized_post_id,
                    )
                )

                seen_comment_ids.add(
                    root_comment_id
                )

            # -------------------------------------------------
            # 3. Az adott főkomment válaszainak lekérése
            # -------------------------------------------------

            replies = self._fetch_paginated_comments(
                endpoint=f"{root_comment_id}/comments",
                limit=limit,
            )

            for reply in replies:
                reply_id = reply.get(
                    "id"
                )

                if not reply_id:
                    continue

                if reply_id in seen_comment_ids:
                    continue

                all_comments.append(
                    self._normalize_comment(
                        comment_data=reply,
                        post_id=normalized_post_id,
                    )
                )

                seen_comment_ids.add(
                    reply_id
                )

        return all_comments
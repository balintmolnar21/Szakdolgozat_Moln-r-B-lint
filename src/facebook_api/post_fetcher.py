from typing import Any

from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)


class FacebookPostFetcher:
    """
    Facebook-oldal bejegyzéseinek lekéréséért felelős komponens.

    A komponens támogatja:
    - egy konkrét Facebook-bejegyzés lekérését;
    - egy Facebook-oldal legutóbbi N bejegyzésének lekérését;
    - a Graph API lapozásának kezelését.
    """

    DEFAULT_FIELDS = [
        "id",
        "message",
        "created_time",
        "permalink_url",
    ]

    def __init__(
        self,
        client: FacebookGraphAPIClient,
    ) -> None:
        self.client = client

    def fetch_post(
        self,
        post_id: str,
    ) -> dict[str, Any]:
        """
        Egy konkrét Facebook-bejegyzés lekérése
        annak azonosítója alapján.
        """

        normalized_post_id = post_id.strip()

        if not normalized_post_id:
            raise ValueError(
                "A Facebook-bejegyzés azonosítója nem lehet üres."
            )

        response = self.client.get(
            endpoint=normalized_post_id,
            params={
                "fields": ",".join(
                    self.DEFAULT_FIELDS
                ),
            },
        )

        return self.normalize_post(
            response
        )

    def fetch_latest_posts(
        self,
        page_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Lekéri egy Facebook-oldal legutóbbi N bejegyzését.

        Parameters
        ----------
        page_id:
            A Facebook-oldal azonosítója.

        limit:
            A visszaadandó bejegyzések maximális száma.

        Returns
        -------
        list[dict[str, Any]]
            A normalizált Facebook-bejegyzések listája.
        """

        normalized_page_id = page_id.strip()

        if not normalized_page_id:
            raise ValueError(
                "A Facebook-oldal azonosítója nem lehet üres."
            )

        if limit < 1:
            raise ValueError(
                "A lekérendő bejegyzések számának "
                "legalább 1-nek kell lennie."
            )

        posts: list[dict[str, Any]] = []

        # Nem kérünk egyszerre indokolatlanul sok rekordot.
        # Ha később 100-nál nagyobb limitet engednénk,
        # a lapozási logika akkor is működőképes marad.
        request_limit = min(
            limit,
            100,
        )

        response = self.client.get(
            endpoint=f"{normalized_page_id}/posts",
            params={
                "fields": ",".join(
                    self.DEFAULT_FIELDS
                ),
                "limit": request_limit,
            },
        )

        while True:
            page_posts = response.get(
                "data",
                [],
            )

            for post_data in page_posts:
                posts.append(
                    self.normalize_post(
                        post_data
                    )
                )

                if len(posts) >= limit:
                    return posts

            paging = response.get(
                "paging",
                {},
            )

            next_url = paging.get(
                "next"
            )

            if not next_url:
                break

            response = self.client.get_from_url(
                next_url
            )

        return posts

    @staticmethod
    def normalize_post(
        post_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        A Graph API válaszát a projekt belső
        adatformátumára alakítja.
        """

        return {
            "post_id": post_data.get(
                "id"
            ),
            "post_text": post_data.get(
                "message",
                "",
            ),
            "post_link": post_data.get(
                "permalink_url",
                "",
            ),
            "created_time": post_data.get(
                "created_time"
            ),
        }
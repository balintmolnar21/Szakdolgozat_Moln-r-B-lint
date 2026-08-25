from typing import Any

from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)


class FacebookPostFetcher:
    """
    Facebook-bejegyzések adatainak lekéréséért felelős osztály.
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
        Lekéri egy Facebook-bejegyzés alapadatait.

        Args:
            post_id:
                A Facebook-bejegyzés egyedi azonosítója.

        Returns:
            A normalizált posztadatok.
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

    @staticmethod
    def normalize_post(
        post_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        A Graph API válaszát a projekt belső
        adatszerkezetére alakítja.
        """
        return {
            "post_id": post_data.get("id"),
            "post_text": post_data.get(
                "message",
                "",
            ),
            "post_link": post_data.get(
                "permalink_url",
                "",
            ),
            "created_time": post_data.get(
                "created_time",
            ),
        }
from typing import Any

from facebook_api.graph_api_client import FacebookGraphAPIClient


class FacebookCommentFetcher:
   

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

    def fetch_comments(
        self,
        post_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        
        normalized_post_id = post_id.strip()

        if not normalized_post_id:
            raise ValueError(
                "A Facebook-bejegyzés azonosítója nem lehet üres."
            )

        response = self.client.get(
            endpoint=f"{normalized_post_id}/comments",
            params={
                "fields": ",".join(
                    self.DEFAULT_FIELDS
                ),
                "limit": limit,
            },
        )

        comments = []

        while True:
            page_comments = response.get(
                "data",
                [],
            )

            for comment in page_comments:
                comments.append(
                    self.normalize_comment(
                        comment,
                        post_id=normalized_post_id,
                    )
                )

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

        return comments

    @staticmethod
    def normalize_comment(
        comment_data: dict[str, Any],
        post_id: str,
    ) -> dict[str, Any]:
        
        return {
            "post_id": post_id,
            "comment_id": comment_data.get("id"),
            "comment_text": comment_data.get(
                "message",
                "",
            ),
            "created_time": comment_data.get(
                "created_time",
            ),
        }
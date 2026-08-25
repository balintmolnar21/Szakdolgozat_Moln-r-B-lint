import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from facebook_api.comment_fetcher import (
    FacebookCommentFetcher,
)
from facebook_api.facebook_data_mapper import (
    create_comments_dataframe,
    create_post_context_dataframe,
)
from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)
from facebook_api.post_fetcher import (
    FacebookPostFetcher,
)


def main() -> None:
    print(
        "Facebook-adatok DataFrame átalakításának tesztelése..."
    )

    post_id = input(
        "Add meg a tesztelendő Facebook Post ID-t: "
    ).strip()

    if not post_id:
        print(
            "HIBA: A Post ID nem lehet üres."
        )
        return

    client = FacebookGraphAPIClient()

    post_fetcher = FacebookPostFetcher(
        client=client,
    )

    comment_fetcher = FacebookCommentFetcher(
        client=client,
    )

    try:
        post = post_fetcher.fetch_post(
            post_id=post_id,
        )

        comments = comment_fetcher.fetch_comments(
            post_id=post_id,
            limit=100,
        )

        post_context_df = create_post_context_dataframe(
            post
        )

        comments_df = create_comments_dataframe(
            comments
        )

    except Exception as error:
        print()
        print(
            f"HIBA: {type(error).__name__}: {error}"
        )
        return

    print()
    print("Poszt DataFrame:")
    print(
        post_context_df.to_string(
            index=False
        )
    )

    print()
    print(
        f"Komment DataFrame sorainak száma: "
        f"{len(comments_df)}"
    )

    if not comments_df.empty:
        print()
        print(
            comments_df.head(
                10
            ).to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()
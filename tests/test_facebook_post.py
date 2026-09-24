import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from facebook_api.config import (
    get_facebook_page_id,
)

from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)

from facebook_api.post_fetcher import (
    FacebookPostFetcher,
)


def main() -> None:
    print("Facebook-posztok lekérése...")

    try:
        # Facebook Graph API kliens létrehozása
        client = FacebookGraphAPIClient()

        # Posztlekérő komponens létrehozása
        post_fetcher = FacebookPostFetcher(
            client=client
        )

        # Facebook-oldal azonosítójának betöltése
        page_id = get_facebook_page_id()

        # A legutóbbi 10 poszt lekérése
        posts = post_fetcher.fetch_latest_posts(
            page_id=page_id,
            limit=10,
        )

    except (ValueError, RuntimeError) as error:
        print()
        print("HIBA:")
        print(error)
        return

    print()
    print(
        f"Lekért posztok száma: {len(posts)}"
    )

    if not posts:
        print(
            "Az API nem adott vissza bejegyzéseket."
        )
        return

    for index, post in enumerate(
        posts,
        start=1,
    ):
        print()
        print("=" * 60)
        print(f"{index}. poszt")
        print("=" * 60)

        print(
            "Post ID:",
            post.get("post_id"),
        )

        print(
            "Létrehozás:",
            post.get("created_time"),
        )

        print(
            "Link:",
            post.get("post_link"),
        )

        message = (
            post.get(
                "post_text",
                "",
            )
            or ""
        )

        print(
            "Szöveg:",
            message[:500],
        )


if __name__ == "__main__":
    main()
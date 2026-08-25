import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)
from facebook_api.comment_fetcher import (
    FacebookCommentFetcher,
)


def main() -> None:
    """
    Egy konkrét Facebook-poszt kommentjeinek
    lekérését teszteli.
    """

    print("Facebook-kommentek lekérése...")
    print()

    post_id = input(
        "Add meg a tesztelendő Facebook Post ID-t: "
    ).strip()

    if not post_id:
        print(
            "HIBA: A Post ID nem lehet üres."
        )
        return

    client = FacebookGraphAPIClient()

    comment_fetcher = FacebookCommentFetcher(
        client=client,
    )

    try:
        comments = comment_fetcher.fetch_comments(
            post_id=post_id,
            limit=100,
        )

    except ValueError as error:
        print()
        print("Adathiba történt:")
        print(error)
        return

    except RuntimeError as error:
        print()
        print("Facebook Graph API hiba történt:")
        print(error)
        return

    except Exception as error:
        print()
        print("Nem várt hiba történt:")
        print(
            f"{type(error).__name__}: {error}"
        )
        return

    print()
    print(
        f"Lekért kommentek száma: {len(comments)}"
    )

    if not comments:
        print(
            "A kiválasztott poszthoz nem érkezett "
            "lekérhető komment."
        )
        return

    for index, comment in enumerate(
        comments,
        start=1,
    ):
        print()
        print("=" * 60)
        print(f"{index}. komment")
        print("=" * 60)

        print(
            "Comment ID:",
            comment.get("comment_id"),
        )

        print(
            "Létrehozás:",
            comment.get("created_time"),
        )

        print(
            "Szöveg:",
            comment.get("comment_text"),
        )


if __name__ == "__main__":
    main()
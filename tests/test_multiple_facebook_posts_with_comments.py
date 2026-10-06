import sys
from pathlib import Path

import pandas as pd


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

from facebook_api.comment_fetcher import (
    FacebookCommentFetcher,
)

from facebook_api.facebook_data_mapper import (
    create_posts_context_dataframe,
    create_comments_dataframe,
)


def main() -> None:
    print("=" * 70)
    print("FACEBOOK POSZTOK ÉS KOMMENTEK TESZTJE")
    print("=" * 70)

    try:
        # -----------------------------------------------------
        # 1. Facebook API komponensek létrehozása
        # -----------------------------------------------------

        client = FacebookGraphAPIClient()

        post_fetcher = FacebookPostFetcher(
            client=client
        )

        comment_fetcher = FacebookCommentFetcher(
            client=client
        )

        page_id = get_facebook_page_id()

        # -----------------------------------------------------
        # 2. Legutóbbi 10 Facebook-poszt lekérése
        # -----------------------------------------------------

        print(
            "\nA legutóbbi 10 Facebook-poszt "
            "lekérése..."
        )

        posts = post_fetcher.fetch_latest_posts(
            page_id=page_id,
            limit=10,
        )

        print(
            f"Lekért posztok száma: {len(posts)}"
        )

        if not posts:
            print(
                "Az API nem adott vissza "
                "feldolgozható posztot."
            )
            return

        # -----------------------------------------------------
        # 3. Kommentek lekérése minden poszthoz
        # -----------------------------------------------------

        all_comments: list[dict] = []

        print(
            "\nKommentek lekérése..."
        )

        for index, post in enumerate(
            posts,
            start=1,
        ):
            post_id = post.get(
                "post_id"
            )

            if not post_id:
                print(
                    f"{index}. poszt kihagyva: "
                    "hiányzó post_id."
                )
                continue

            comments = (
                comment_fetcher.fetch_comments(
                    post_id=post_id,
                )
            )

            all_comments.extend(
                comments
            )

            print(
                f"{index}. poszt: "
                f"{len(comments)} komment"
            )

        print(
            "\nÖsszes lekért komment: "
            f"{len(all_comments)}"
        )

        # -----------------------------------------------------
        # 4. DataFrame-ek létrehozása
        # -----------------------------------------------------

        post_context_df = (
            create_posts_context_dataframe(
                posts
            )
        )

        comments_df = (
            create_comments_dataframe(
                all_comments
            )
        )

        # -----------------------------------------------------
        # 5. Alapvető ellenőrzések
        # -----------------------------------------------------

        print()
        print("=" * 70)
        print("DATAFRAME ELLENŐRZÉS")
        print("=" * 70)

        print(
            "\npost_context_df mérete:",
            post_context_df.shape,
        )

        print(
            "comments_df mérete:",
            comments_df.shape,
        )

        print(
            "\npost_context_df oszlopai:"
        )

        print(
            list(
                post_context_df.columns
            )
        )

        print(
            "\ncomments_df oszlopai:"
        )

        print(
            list(
                comments_df.columns
            )
        )

        # -----------------------------------------------------
        # 6. Kommentek száma posztonként
        # -----------------------------------------------------

        if not comments_df.empty:
            comment_counts = (
                comments_df
                .groupby("post_id")
                .size()
                .reset_index(
                    name="comment_count"
                )
            )

            print()
            print(
                "Kommentek száma posztonként:"
            )

            print(
                comment_counts.to_string(
                    index=False
                )
            )

        else:
            print()
            print(
                "A lekért posztokhoz nem érkezett "
                "feldolgozható komment."
            )

        # -----------------------------------------------------
        # 7. Minta megjelenítése
        # -----------------------------------------------------

        print()
        print("=" * 70)
        print("POSZTKONTEXTUS MINTA")
        print("=" * 70)

        print(
            post_context_df[
                [
                    "post_id",
                    "post_type",
                    "post_text",
                ]
            ]
            .head()
            .to_string(
                index=False
            )
        )

        if not comments_df.empty:
            print()
            print("=" * 70)
            print("KOMMENT MINTA")
            print("=" * 70)

            print(
                comments_df[
                    [
                        "post_id",
                        "comment_id",
                        "comment_text",
                    ]
                ]
                .head(10)
                .to_string(
                    index=False
                )
            )

        # -----------------------------------------------------
        # 8. Kapcsolati integritás ellenőrzése
        # -----------------------------------------------------

        if not comments_df.empty:
            known_post_ids = set(
                post_context_df[
                    "post_id"
                ]
                .astype(str)
            )

            comment_post_ids = set(
                comments_df[
                    "post_id"
                ]
                .astype(str)
            )

            unknown_post_ids = (
                comment_post_ids
                - known_post_ids
            )

            if unknown_post_ids:
                print()
                print(
                    "HIBA: Van olyan komment, "
                    "amelyhez nem található posztkontextus:"
                )

                print(
                    unknown_post_ids
                )

            else:
                print()
                print(
                    "Kapcsolati ellenőrzés: RENDBEN"
                )

                print(
                    "Minden kommenthez található "
                    "megfelelő posztkontextus."
                )

        print()
        print("=" * 70)
        print("TESZT BEFEJEZVE")
        print("=" * 70)

    except (
        ValueError,
        RuntimeError,
    ) as error:
        print()
        print("HIBA:")
        print(error)


if __name__ == "__main__":
    main()
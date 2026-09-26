import sys
from pathlib import Path


# ---------------------------------------------------------
# Projektútvonal beállítása
# ---------------------------------------------------------

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

from pipeline.analysis_pipeline import (
    run_analysis_pipeline_from_dataframes,
)


# ---------------------------------------------------------
# Tesztbeállítások
# ---------------------------------------------------------

POST_LIMIT = 10


def main() -> None:
    print("=" * 70)
    print("FACEBOOK END-TO-END SENTIMENT PIPELINE TESZT")
    print("=" * 70)

    try:
        # -----------------------------------------------------
        # 1. Facebook API kliens létrehozása
        # -----------------------------------------------------

        client = FacebookGraphAPIClient()

        post_fetcher = FacebookPostFetcher(
            client=client,
        )

        comment_fetcher = FacebookCommentFetcher(
            client=client,
        )

        page_id = get_facebook_page_id()

        # -----------------------------------------------------
        # 2. Legutóbbi Facebook-posztok lekérése
        # -----------------------------------------------------

        print(
            f"\nA legutóbbi {POST_LIMIT} "
            "Facebook-poszt lekérése..."
        )

        posts = post_fetcher.fetch_latest_posts(
            page_id=page_id,
            limit=POST_LIMIT,
        )

        print(
            f"Lekért posztok száma: {len(posts)}"
        )

        if not posts:
            raise ValueError(
                "Az API nem adott vissza "
                "feldolgozható Facebook-posztot."
            )

        # -----------------------------------------------------
        # 3. Kommentek + reply-k lekérése
        # -----------------------------------------------------

        all_comments: list[dict] = []

        print(
            "\nKommentek és válaszkommentek lekérése..."
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
                f"{len(comments)} hozzászólás"
            )

        print(
            "\nÖsszes lekért hozzászólás: "
            f"{len(all_comments)}"
        )

        if not all_comments:
            raise ValueError(
                "A lekért Facebook-posztokhoz "
                "nem található feldolgozható hozzászólás."
            )

        # -----------------------------------------------------
        # 4. Belső DataFrame-ek létrehozása
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

        print()
        print("=" * 70)
        print("ADATKERETEK")
        print("=" * 70)

        print(
            f"post_context_df: "
            f"{post_context_df.shape}"
        )

        print(
            f"comments_df: "
            f"{comments_df.shape}"
        )

        # -----------------------------------------------------
        # 5. Kimeneti útvonalak
        # -----------------------------------------------------

        excel_output_file = (
            PROJECT_ROOT
            / "data"
            / "processed"
            / "facebook_sentiment_analysis_results.xlsx"
        )

        charts_output_directory = (
            PROJECT_ROOT
            / "outputs"
            / "charts"
            / "facebook"
        )

        reports_output_directory = (
            PROJECT_ROOT
            / "outputs"
            / "reports"
            / "facebook"
        )

        # -----------------------------------------------------
        # 6. Központi sentiment pipeline
        # -----------------------------------------------------

        print()
        print("=" * 70)
        print("SENTIMENT ELEMZÉS INDÍTÁSA")
        print("=" * 70)

        result = run_analysis_pipeline_from_dataframes(
            comments_df=comments_df,
            post_context_df=post_context_df,
            excel_output_file=excel_output_file,
            charts_output_directory=charts_output_directory,
            reports_output_directory=reports_output_directory,

            # Facebook-adatokhoz nincs emberi címke,
            # ezért nincs modellkiértékelés.
            evaluation_output_directory=None,

            limit=None,
        )

        # -----------------------------------------------------
        # 7. Eredmények
        # -----------------------------------------------------

        print()
        print("=" * 70)
        print("FACEBOOK PIPELINE SIKERESEN LEFUTOTT")
        print("=" * 70)

        print(
            f"\nLekért posztok: "
            f"{len(result.post_context_df)}"
        )

        print(
            f"Lekért hozzászólások: "
            f"{len(result.comments_df)}"
        )

        print(
            f"Elemzett hozzászólások: "
            f"{len(result.full_sentiment_df)}"
        )

        print(
            f"Posztonkénti statisztikai sorok: "
            f"{len(result.post_statistics_df)}"
        )

        # -----------------------------------------------------
        # 8. Evaluation ellenőrzése
        # -----------------------------------------------------

        print(
            "\nModellkiértékelés:"
        )

        if result.evaluation_result is None:
            print(
                "Nincs - Facebook API-adatokhoz "
                "nem tartozik manual_label. "
                "Ez a várt működés."
            )
        else:
            print(
                "FIGYELEM: Facebook módban nem "
                "vártunk modellkiértékelést."
            )

        # -----------------------------------------------------
        # 9. Threshold statisztika
        # -----------------------------------------------------

        if (
            "threshold_applied"
            in result.full_sentiment_df.columns
        ):
            threshold_count = int(
                result.full_sentiment_df[
                    "threshold_applied"
                ]
                .fillna(False)
                .sum()
            )

            print(
                "\nThreshold által módosított "
                f"predikciók: {threshold_count}"
            )

        # -----------------------------------------------------
        # 10. Sentiment eredmények mintája
        # -----------------------------------------------------

        preview_columns = [
            "post_id",
            "comment_id",
            "comment_text",
            "finetuned_label",
            "finetuned_confidence",
            "final_sentiment_label",
            "threshold_applied",
            "model_label",
        ]

        available_columns = [
            column
            for column in preview_columns
            if column in result.full_sentiment_df.columns
        ]

        print()
        print("=" * 70)
        print("ELSŐ 20 SENTIMENT EREDMÉNY")
        print("=" * 70)

        print(
            result.full_sentiment_df[
                available_columns
            ]
            .head(20)
            .to_string(
                index=False
            )
        )

        # -----------------------------------------------------
        # 11. Kimeneti fájlok
        # -----------------------------------------------------

        print()
        print("Excel eredményfájl:")
        print(
            result.excel_output_file
        )

        print()
        print("Szöveges riport:")
        print(
            result.report_file
        )

        print()
        print("Létrehozott grafikonok:")

        for chart_file in result.chart_files:
            print(
                f"- {chart_file}"
            )

    except (
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as error:
        print()
        print("=" * 70)
        print("HIBA")
        print("=" * 70)
        print(error)


if __name__ == "__main__":
    main()
import sys
from pathlib import Path

import streamlit as st
from pandas.errors import EmptyDataError, ParserError


# ============================================================
# Projektútvonalak
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


# ============================================================
# Projektmodulok importálása
# ============================================================

from sentiment.context_aware_sentiment_analyzer import (
    ContextAwareSentimentAnalyzer,
)

from pipeline.analysis_pipeline import (
    AnalysisPipelineResult,
    run_analysis_pipeline,
    run_analysis_pipeline_from_dataframes,
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


# ============================================================
# CSV tesztadatok
# ============================================================

DEFAULT_TEST_COMMENTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "test_comments.csv"
)

DEFAULT_TEST_POST_CONTEXT_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "test_post_context.csv"
)


# ============================================================
# CSV mód kimenetei
# ============================================================

CSV_EXCEL_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_analysis_results.xlsx"
)

CSV_CHARTS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "charts"
)

CSV_REPORTS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
)

CSV_EVALUATION_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation"
)


# ============================================================
# Facebook mód kimenetei
# ============================================================

FACEBOOK_EXCEL_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "facebook_sentiment_analysis_results.xlsx"
)

FACEBOOK_CHARTS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "charts"
    / "facebook"
)

FACEBOOK_REPORTS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "facebook"
)


# ============================================================
# Context-aware modell beállításai
# ============================================================

CONTEXT_AWARE_MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "context_aware_hubert_text"
)

CONTEXT_AWARE_MAX_LENGTH = 128

CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# Modell betöltése
# ============================================================

@st.cache_resource(show_spinner=False)
def load_sentiment_analyzer() -> ContextAwareSentimentAnalyzer:
    """
    A finomhangolt context-aware huBERT modell betöltése.

    A Streamlit resource cache használatával a modell
    nem töltődik újra minden felületi interakció során.
    """

    print(
        "CONTEXT-AWARE FINE-TUNED HUBERT "
        "MODELL TÉNYLEGES BETÖLTÉSE"
    )

    return ContextAwareSentimentAnalyzer(
        model_path=CONTEXT_AWARE_MODEL_PATH,
        max_length=CONTEXT_AWARE_MAX_LENGTH,
        confidence_threshold=CONFIDENCE_THRESHOLD,
    )


# ============================================================
# Streamlit oldal konfigurációja
# ============================================================

def configure_page() -> None:
    """
    Beállítja a Streamlit oldal alapvető tulajdonságait.
    """

    st.set_page_config(
        page_title="Social media hangulatelemző",
        page_icon="📊",
        layout="wide",
    )


# ============================================================
# Fejléc
# ============================================================

def display_header() -> None:
    """
    Megjeleníti az alkalmazás fejlécét és rövid leírását.
    """

    st.title(
        "Social media hangulatelemző szoftver"
    )

    st.write(
        "Magyar nyelvű Facebook-kommentek context-aware, "
        "finomhangolt huBERT-alapú sentimentelemzése, "
        "statisztikai összesítése és kontextuális értelmezése."
    )

    st.info(
        "Az alkalmazás két adatforrást támogat. "
        "A kézzel címkézett CSV-teszthalmaz a modell "
        "kiértékelésére használható, míg a Facebook API mód "
        "az adminisztrált oldal legutóbbi bejegyzéseinek és "
        "az azokhoz tartozó kommenteknek, illetve "
        "válaszkommenteknek az elemzését teszi lehetővé."
    )


# ============================================================
# Session state kezelése
# ============================================================

def clear_previous_analysis() -> None:
    """
    Törli a korábbi elemzéshez kapcsolódó
    Streamlit session state értékeket.
    """

    session_keys_to_delete = [
        "analysis_result",
        "analysis_success",
        "analysis_source",
        "facebook_fetch_summary",
    ]

    for key in session_keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]


# ============================================================
# CSV bemeneti fájlok megjelenítése
# ============================================================

def display_input_files() -> None:
    """
    Megjeleníti a CSV tesztmódban használt
    bemeneti fájlokat.
    """

    st.subheader(
        "Bemeneti fájlok"
    )

    test_comments_exists = (
        DEFAULT_TEST_COMMENTS_FILE.exists()
    )

    test_context_exists = (
        DEFAULT_TEST_POST_CONTEXT_FILE.exists()
    )

    first_column, second_column = st.columns(2)

    with first_column:
        st.write(
            "Teszt kommentadatok"
        )

        st.code(
            str(
                DEFAULT_TEST_COMMENTS_FILE
            )
        )

        if test_comments_exists:
            st.success(
                "A teszt kommentfájl elérhető."
            )
        else:
            st.error(
                "A teszt kommentfájl nem található."
            )

    with second_column:
        st.write(
            "Teszt posztkontextus-adatok"
        )

        st.code(
            str(
                DEFAULT_TEST_POST_CONTEXT_FILE
            )
        )

        if test_context_exists:
            st.success(
                "A teszt posztkontextus-fájl elérhető."
            )
        else:
            st.error(
                "A teszt posztkontextus-fájl nem található."
            )


# ============================================================
# Adatforrás kiválasztása
# ============================================================

def display_data_source_selection() -> tuple[str, int]:
    """
    Megjeleníti az adatforrás kiválasztását.

    CSV módban a kézzel címkézett teszthalmaz,
    Facebook módban az adminisztrált oldal legutóbbi
    N bejegyzése kerül feldolgozásra.
    """

    st.subheader(
        "Adatforrás"
    )

    source_mode = st.radio(
        "Válaszd ki az elemzés adatforrását:",
        options=[
            "CSV tesztadatok",
            "Facebook API",
        ],
        horizontal=True,
        key="data_source_mode",
        on_change=clear_previous_analysis,
    )

    facebook_post_limit = 10

    if source_mode == "CSV tesztadatok":
        display_input_files()

    else:
        st.write(
            "A Facebook API mód az adminisztrált oldal "
            "legutóbbi bejegyzéseit, valamint az azokhoz "
            "tartozó kommenteket és válaszkommenteket "
            "dolgozza fel."
        )

        facebook_post_limit = int(
            st.number_input(
                "Elemzendő legutóbbi Facebook-posztok száma",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key="facebook_post_limit",
                on_change=clear_previous_analysis,
            )
        )

        try:
            page_id = get_facebook_page_id()

            if page_id:
                st.success(
                    "A Facebook Page ID konfigurációja elérhető."
                )

        except ValueError:
            st.warning(
                "A Facebook Page ID nincs megfelelően "
                "beállítva a .env fájlban."
            )

    return (
        source_mode,
        facebook_post_limit,
    )


# ============================================================
# Kimeneti információk
# ============================================================

def display_output_information(
    source_mode: str,
) -> None:
    """
    Megjeleníti az aktuális adatforráshoz tartozó
    fő kimeneti helyeket.
    """

    st.subheader(
        "Kimenetek"
    )

    if source_mode == "CSV tesztadatok":
        output_paths = [
            CSV_EXCEL_OUTPUT_FILE,
            CSV_CHARTS_OUTPUT_DIRECTORY,
            CSV_REPORTS_OUTPUT_DIRECTORY,
            CSV_EVALUATION_OUTPUT_DIRECTORY,
        ]

        st.write(
            "A CSV-alapú feldolgozás fő kimenetei:"
        )

    else:
        output_paths = [
            FACEBOOK_EXCEL_OUTPUT_FILE,
            FACEBOOK_CHARTS_OUTPUT_DIRECTORY,
            FACEBOOK_REPORTS_OUTPUT_DIRECTORY,
        ]

        st.write(
            "A Facebook API-alapú feldolgozás fő kimenetei:"
        )

        st.caption(
            "Facebook API módban nem készül "
            "modellkiértékelés, mert a lekért adatokhoz "
            "nem tartozik ember által megadott referencia-címke."
        )

    st.code(
        "\n".join(
            str(path)
            for path in output_paths
        )
    )


# ============================================================
# Hibakezelés
# ============================================================

def display_analysis_error(
    error: Exception,
) -> None:
    """
    Felhasználóbarát hibaüzenetet jelenít meg,
    miközben a technikai részletek külön
    lenyitható panelen elérhetők.
    """

    if isinstance(
        error,
        FileNotFoundError,
    ):
        st.error(
            "A feldolgozáshoz szükséges egyik bemeneti fájl "
            "vagy modellfájl nem található. Ellenőrizd a "
            "CSV-fájlok és a finomhangolt modell helyét."
        )

    elif isinstance(
        error,
        EmptyDataError,
    ):
        st.error(
            "Az egyik bemeneti CSV-fájl üres, ezért az elemzés "
            "nem indítható el."
        )

    elif isinstance(
        error,
        ParserError,
    ):
        st.error(
            "A CSV-fájl szerkezete nem értelmezhető. "
            "Ellenőrizd az elválasztó karaktereket, az "
            "oszlopokat és az idézőjelek használatát."
        )

    elif isinstance(
        error,
        UnicodeDecodeError,
    ):
        st.error(
            "A bemeneti fájl karakterkódolása nem megfelelő. "
            "A CSV-fájlt célszerű UTF-8 kódolással menteni."
        )

    elif isinstance(
        error,
        PermissionError,
    ):
        st.error(
            "A program nem tudta megnyitni vagy felülírni "
            "az egyik kimeneti fájlt. Ellenőrizd, hogy az "
            "Excel-fájl vagy más kimenet nincs-e megnyitva "
            "egy másik programban."
        )

    elif isinstance(
        error,
        ValueError,
    ):
        st.error(
            "A bemeneti adatok vagy a konfiguráció tartalma "
            "nem megfelelő. Ellenőrizd a szükséges adatokat, "
            "a Facebook-beállításokat és azt, hogy található-e "
            "feldolgozható rekord."
        )

    elif isinstance(
        error,
        RuntimeError,
    ):
        st.error(
            "Technikai hiba történt a modell futtatása vagy "
            "a Facebook Graph API-val történő kommunikáció "
            "közben. Ellenőrizd a modellt, az API tokent, "
            "a Page ID-t és az internetkapcsolatot."
        )

    elif isinstance(
        error,
        OSError,
    ):
        st.error(
            "Fájl- vagy mappakezelési hiba történt. "
            "Ellenőrizd, hogy a kimeneti könyvtárak "
            "elérhetők és írhatók-e."
        )

    else:
        st.error(
            "Az elemzés futtatása közben "
            "nem várt hiba történt."
        )

    with st.expander(
        "Technikai részletek"
    ):
        st.exception(
            error
        )


# ============================================================
# Facebook adatok lekérése
# ============================================================

def load_facebook_analysis_data(
    post_limit: int,
):
    """
    Lekéri a Facebook oldal legutóbbi N posztját,
    valamint az azokhoz tartozó kommenteket és
    válaszkommenteket.

    A visszaadott DataFrame-ek közvetlenül átadhatók
    a közös sentiment pipeline-nak.
    """

    if post_limit < 1:
        raise ValueError(
            "Legalább egy Facebook-posztot "
            "ki kell választani."
        )

    client = FacebookGraphAPIClient()

    post_fetcher = FacebookPostFetcher(
        client=client,
    )

    comment_fetcher = FacebookCommentFetcher(
        client=client,
    )

    page_id = get_facebook_page_id()

    posts = post_fetcher.fetch_latest_posts(
        page_id=page_id,
        limit=post_limit,
    )

    if not posts:
        raise ValueError(
            "A Facebook API nem adott vissza "
            "feldolgozható posztot."
        )

    all_comments: list[dict] = []

    for post in posts:
        post_id = post.get(
            "post_id"
        )

        if not post_id:
            continue

        comments = (
            comment_fetcher.fetch_comments(
                post_id=post_id,
            )
        )

        all_comments.extend(
            comments
        )

    if not all_comments:
        raise ValueError(
            "A kiválasztott Facebook-posztokhoz "
            "nem található feldolgozható komment "
            "vagy válaszkomment."
        )

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

    return (
        comments_df,
        post_context_df,
        len(posts),
        len(all_comments),
    )


# ============================================================
# Elemzés indítása
# ============================================================

def display_analysis_button(
    source_mode: str,
    facebook_post_limit: int,
) -> None:
    """
    Megjeleníti az elemzés indítására és a korábbi
    eredmények törlésére szolgáló vezérlőket.

    CSV és Facebook API adatforrással egyaránt működik.
    """

    st.subheader(
        "Elemzés vezérlése"
    )

    if source_mode == "CSV tesztadatok":
        analysis_available = (
            DEFAULT_TEST_COMMENTS_FILE.exists()
            and DEFAULT_TEST_POST_CONTEXT_FILE.exists()
        )

    else:
        analysis_available = True

    start_column, clear_column = st.columns(2)

    with start_column:
        analysis_button_clicked = st.button(
            "Elemzés indítása",
            type="primary",
            disabled=not analysis_available,
            use_container_width=True,
        )

    with clear_column:
        clear_button_clicked = st.button(
            "Korábbi eredmények törlése",
            disabled=(
                "analysis_result"
                not in st.session_state
            ),
            use_container_width=True,
        )

    if st.session_state.get(
        "analysis_success",
        False,
    ):
        st.success(
            "Az elemzés sikeresen befejeződött."
        )

        st.session_state[
            "analysis_success"
        ] = False

    if (
        source_mode == "CSV tesztadatok"
        and not analysis_available
    ):
        st.warning(
            "Az elemzés indításához mindkét bemeneti "
            "CSV-fájlnak rendelkezésre kell állnia."
        )

    if clear_button_clicked:
        clear_previous_analysis()

        st.session_state[
            "clear_success"
        ] = True

        st.rerun()

    if st.session_state.get(
        "clear_success",
        False,
    ):
        st.success(
            "A korábbi elemzési eredmények "
            "törlésre kerültek."
        )

        st.session_state[
            "clear_success"
        ] = False

    if analysis_button_clicked:
        try:
            # Korábbi eredmény eltávolítása,
            # hogy hiba esetén ne maradjon régi adat.
            clear_previous_analysis()

            with st.spinner(
                "Az adatok betöltése, a finomhangolt "
                "context-aware huBERT modell futtatása "
                "és az eredmények előállítása folyamatban..."
            ):
                analyzer = (
                    load_sentiment_analyzer()
                )

                # =================================================
                # CSV TESZTMÓD
                # =================================================

                if source_mode == "CSV tesztadatok":
                    result = run_analysis_pipeline(
                        validation_file=(
                            DEFAULT_TEST_COMMENTS_FILE
                        ),
                        post_context_file=(
                            DEFAULT_TEST_POST_CONTEXT_FILE
                        ),
                        excel_output_file=(
                            CSV_EXCEL_OUTPUT_FILE
                        ),
                        charts_output_directory=(
                            CSV_CHARTS_OUTPUT_DIRECTORY
                        ),
                        reports_output_directory=(
                            CSV_REPORTS_OUTPUT_DIRECTORY
                        ),
                        evaluation_output_directory=(
                            CSV_EVALUATION_OUTPUT_DIRECTORY
                        ),
                        analyzer=analyzer,
                        limit=None,
                    )

                    analysis_source = "csv"
                    facebook_fetch_summary = None

                # =================================================
                # FACEBOOK API MÓD
                # =================================================

                else:
                    (
                        comments_df,
                        post_context_df,
                        fetched_post_count,
                        fetched_comment_count,
                    ) = load_facebook_analysis_data(
                        post_limit=facebook_post_limit
                    )

                    result = (
                        run_analysis_pipeline_from_dataframes(
                            comments_df=comments_df,
                            post_context_df=post_context_df,
                            excel_output_file=(
                                FACEBOOK_EXCEL_OUTPUT_FILE
                            ),
                            charts_output_directory=(
                                FACEBOOK_CHARTS_OUTPUT_DIRECTORY
                            ),
                            reports_output_directory=(
                                FACEBOOK_REPORTS_OUTPUT_DIRECTORY
                            ),
                            evaluation_output_directory=None,
                            analyzer=analyzer,
                            limit=None,
                        )
                    )

                    analysis_source = "facebook"

                    facebook_fetch_summary = {
                        "posts": fetched_post_count,
                        "comments": fetched_comment_count,
                    }

                # =================================================
                # Eredmények session state-be mentése
                # =================================================

                st.session_state[
                    "analysis_result"
                ] = result

                st.session_state[
                    "analysis_source"
                ] = analysis_source

                if facebook_fetch_summary is not None:
                    st.session_state[
                        "facebook_fetch_summary"
                    ] = facebook_fetch_summary

                st.session_state[
                    "analysis_success"
                ] = True

            st.rerun()

        except Exception as error:
            display_analysis_error(
                error
            )


# ============================================================
# Fordítási segédfüggvények
# ============================================================

def translate_sentiment_label(
    value,
) -> str:
    """
    A belső angol sentiment címkéket magyar
    megjelenítési értékekre alakítja.
    """

    if value is None:
        return ""

    translations = {
        "positive": "Pozitív",
        "negative": "Negatív",
        "neutral": "Semleges",
        "mixed": "Vegyes",
        "no_data": "Nincs adat",
    }

    normalized_value = (
        str(value)
        .strip()
        .lower()
    )

    if normalized_value in {
        "",
        "nan",
        "none",
    }:
        return ""

    return translations.get(
        normalized_value,
        str(value),
    )


def translate_context_alignment(
    value,
) -> str:
    """
    A kontextusilleszkedés belső címkéit
    magyar megjelenítési értékekre alakítja.
    """

    translations = {
        "aligned": "Azonos irányú",
        "opposite": "Ellentétes",
        "mixed": "Vegyes",
        "different": "Eltérő",
        "unclear": "Nem egyértelmű",
    }

    normalized_value = (
        str(value)
        .strip()
        .lower()
    )

    return translations.get(
        normalized_value,
        str(value),
    )


def create_display_dataframe(
    dataframe,
    column_translations: dict[str, str],
):
    """
    A belső oszlopneveket a felhasználói
    felület számára magyar elnevezésekre alakítja.
    """

    display_df = dataframe.copy()

    available_translations = {
        column_name: translated_name
        for column_name, translated_name
        in column_translations.items()
        if column_name in display_df.columns
    }

    return display_df.rename(
        columns=available_translations
    )


# ============================================================
# Mérőszámok magyarázata
# ============================================================

def display_metric_explanations() -> None:
    """
    Röviden bemutatja a modellkiértékelés során
    alkalmazott fő mérőszámokat.
    """

    st.markdown(
        """
        **Accuracy:** Megmutatja, hogy az összes kiértékelt komment
        mekkora részét osztályozta helyesen a modell.

        **Precision:** Azt fejezi ki, hogy egy adott kategóriába sorolt
        kommentek közül ténylegesen hány tartozott oda.

        **Recall:** Azt mutatja meg, hogy az adott kategóriába ténylegesen
        tartozó kommentek mekkora részét találta meg a modell.

        **F1-score:** A precision és a recall harmonikus átlaga, ezért
        egyetlen értékben egyesíti a két mérőszámot.

        **Konfidencia:** A modell becsült bizonyossága arra vonatkozóan,
        hogy az adott kommenthez kiválasztott sentimentcímke helyes.
        A magasabb érték nagyobb modellbizonyosságot jelez, de nem
        garantálja a predikció tényleges helyességét.

        **Confidence threshold:** A rendszer a 0,60 alatti
        konfidenciájú pozitív vagy negatív predikciókat semleges
        kategóriába sorolja át. A semleges predikciókat a küszöbérték
        nem módosítja.
        """
    )


# ============================================================
# Grafikonmagyarázatok
# ============================================================

def display_chart_explanation(
    chart_file: Path,
) -> None:
    """
    Rövid magyarázatot jelenít meg az egyes
    generált grafikonokhoz.
    """

    chart_explanations = {
        "overall_sentiment_distribution.png": (
            "A diagram az összes vizsgált komment pozitív, "
            "negatív és semleges megoszlását mutatja."
        ),
        "post_sentiment_distribution.png": (
            "A diagram posztonként hasonlítja össze a pozitív, "
            "negatív és semleges kommentek arányát."
        ),
        "average_confidence_by_post.png": (
            "A diagram azt mutatja meg, hogy a modell átlagosan "
            "mennyire volt biztos az egyes posztok kommentjeinek "
            "besorolásában."
        ),
        "context_alignment_distribution.png": (
            "A diagram a poszt tartalma és a kommentek domináns "
            "hangulata közötti illeszkedés megoszlását "
            "szemlélteti."
        ),
        "confusion_matrix.png": (
            "A confusion matrix sorai a kézi címkéket, oszlopai "
            "a modell végleges predikcióit mutatják. A főátlóban "
            "találhatók a helyes találatok."
        ),
        "classification_metrics.png": (
            "A diagram sentimentkategóriánként hasonlítja össze "
            "a precision, recall és F1-score értékeket."
        ),
    }

    explanation = chart_explanations.get(
        chart_file.name,
        (
            "A grafikon az elemzés egyik összesített "
            "eredményét szemlélteti."
        ),
    )

    st.caption(
        explanation
    )


# ============================================================
# Modellkiértékelés megjelenítése
# ============================================================

def display_model_evaluation(
    result: AnalysisPipelineResult,
) -> None:
    """
    Megjeleníti a kézzel címkézett teszthalmazon
    végzett modellkiértékelés eredményeit.

    Facebook API módban nincs kézi referencia-címke,
    ezért ott modellkiértékelés nem történik.
    """

    st.subheader(
        "Modellkiértékelés"
    )

    evaluation_result = (
        result.evaluation_result
    )

    if evaluation_result is None:
        st.info(
            "A Facebook API-ból származó adatokhoz nem "
            "tartozik ember által megadott referencia-címke, "
            "ezért ezen az adathalmazon Accuracy, Precision, "
            "Recall, F1-score és confusion matrix nem "
            "számítható."
        )

        st.caption(
            "A modell objektív teljesítményértékelése "
            "a külön, kézzel címkézett teszthalmazon történik."
        )

        return

    evaluated_count = len(
        evaluation_result.evaluated_data
    )

    misclassified_count = len(
        evaluation_result.misclassified_comments
    )

    low_confidence_count = len(
        evaluation_result.low_confidence_comments
    )

    (
        metric_column_1,
        metric_column_2,
        metric_column_3,
    ) = st.columns(3)

    with metric_column_1:
        st.metric(
            label="Accuracy",
            value=(
                f"{evaluation_result.accuracy:.2%}"
            ),
        )

    with metric_column_2:
        st.metric(
            label="Hibás predikciók",
            value=misclassified_count,
        )

    with metric_column_3:
        st.metric(
            label="0,60 alatti konfidenciájú esetek",
            value=low_confidence_count,
        )

    st.caption(
        f"Összesen {evaluated_count} kézzel címkézett komment "
        "került bevonásra a modell kiértékelésébe."
    )

    with st.expander(
        "A mérőszámok rövid magyarázata"
    ):
        display_metric_explanations()

    # --------------------------------------------------------
    # Osztályonkénti eredmények
    # --------------------------------------------------------

    st.subheader(
        "Osztályonkénti eredmények"
    )

    metrics_display_df = (
        evaluation_result.metrics.copy()
    )

    metrics_display_df = (
        metrics_display_df.rename(
            columns={
                "category": "Kategória",
                "precision": "Precision",
                "recall": "Recall",
                "f1_score": "F1-score",
                "support": "Esetszám",
            }
        )
    )

    category_translations = {
        "negative": "Negatív",
        "neutral": "Semleges",
        "positive": "Pozitív",
        "macro_avg": "Makróátlag",
        "weighted_avg": "Súlyozott átlag",
    }

    if "Kategória" in metrics_display_df.columns:
        metrics_display_df[
            "Kategória"
        ] = metrics_display_df[
            "Kategória"
        ].replace(
            category_translations
        )

    st.dataframe(
        metrics_display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Precision": (
                st.column_config.NumberColumn(
                    format="%.3f"
                )
            ),
            "Recall": (
                st.column_config.NumberColumn(
                    format="%.3f"
                )
            ),
            "F1-score": (
                st.column_config.NumberColumn(
                    format="%.3f"
                )
            ),
        },
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    st.subheader(
        "Confusion matrix"
    )

    st.caption(
        "A sorok az ember által megadott címkéket, "
        "az oszlopok a modell végleges, threshold "
        "alkalmazása utáni predikcióit jelentik."
    )

    st.dataframe(
        evaluation_result.confusion_matrix,
        use_container_width=True,
    )

    # --------------------------------------------------------
    # Hibás predikciók
    # --------------------------------------------------------

    st.subheader(
        "Hibás predikciók"
    )

    if (
        evaluation_result
        .misclassified_comments
        .empty
    ):
        st.success(
            "A kiértékelt adatok között nem található "
            "hibás predikció."
        )

    else:
        misclassified_columns = [
            column
            for column in [
                "comment_text",
                "manual_label",
                "finetuned_label",
                "finetuned_confidence",
                "final_sentiment_label",
                "threshold_applied",
                "model_label",
                "confidence",
            ]
            if column
            in (
                evaluation_result
                .misclassified_comments
                .columns
            )
        ]

        st.dataframe(
            evaluation_result
            .misclassified_comments[
                misclassified_columns
            ],
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # Alacsony konfidenciájú esetek
    # --------------------------------------------------------

    st.subheader(
        "Alacsony konfidenciájú predikciók"
    )

    st.caption(
        "Ide azok a kommentek kerülnek, amelyeknél "
        "a modell nyers predikciójának konfidenciaértéke "
        "0,60 alatti. A pozitív vagy negatív nyers "
        "predikciók ilyen esetben semleges végleges "
        "címkére módosulhatnak."
    )

    if (
        evaluation_result
        .low_confidence_comments
        .empty
    ):
        st.info(
            "Nem található 0,60 alatti "
            "konfidenciájú predikció."
        )

    else:
        low_confidence_columns = [
            column
            for column in [
                "comment_text",
                "manual_label",
                "finetuned_label",
                "finetuned_confidence",
                "final_sentiment_label",
                "threshold_applied",
                "confidence",
            ]
            if column
            in (
                evaluation_result
                .low_confidence_comments
                .columns
            )
        ]

        st.dataframe(
            evaluation_result
            .low_confidence_comments[
                low_confidence_columns
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# Elemzési eredmények
# ============================================================

def display_analysis_results(
    result: AnalysisPipelineResult,
) -> None:
    """
    Megjeleníti a teljes elemzési pipeline eredményeit.
    """

    st.header(
        "Elemzési eredmények"
    )

    # --------------------------------------------------------
    # Facebook lekérés összefoglalása
    # --------------------------------------------------------

    analysis_source = st.session_state.get(
        "analysis_source"
    )

    if analysis_source == "facebook":
        fetch_summary = st.session_state.get(
            "facebook_fetch_summary"
        )

        if fetch_summary:
            st.info(
                "Facebook API-adatlekérés: "
                f"{fetch_summary['posts']} poszt és "
                f"{fetch_summary['comments']} komment, illetve "
                "válaszkomment került lekérésre."
            )

    # --------------------------------------------------------
    # Alapstatisztikák
    # --------------------------------------------------------

    if result.overall_statistics_df.empty:
        st.warning(
            "Az összesített statisztikai eredmények nem "
            "tartalmaznak megjeleníthető adatot."
        )
        return

    overall_row = (
        result.overall_statistics_df.iloc[0]
    )

    post_count = int(
        overall_row["post_count"]
    )

    comment_count = int(
        overall_row["total_comment_count"]
    )

    dominant_sentiment = (
        translate_sentiment_label(
            overall_row[
                "overall_dominant_sentiment"
            ]
        )
    )

    average_confidence = float(
        overall_row[
            "overall_average_confidence"
        ]
    )

    (
        first_column,
        second_column,
        third_column,
        fourth_column,
    ) = st.columns(4)

    with first_column:
        st.metric(
            "Feldolgozott posztok",
            post_count,
        )

    with second_column:
        st.metric(
            "Feldolgozott hozzászólások",
            comment_count,
        )

    with third_column:
        st.metric(
            "Domináns sentiment",
            dominant_sentiment,
        )

    with fourth_column:
        st.metric(
            "Átlagos modellbizonyosság",
            f"{average_confidence:.3f}",
        )

    st.divider()

    (
        summary_tab,
        post_statistics_tab,
        context_tab,
        evaluation_tab,
        charts_tab,
        report_tab,
        comments_tab,
    ) = st.tabs(
        [
            "Összegzés",
            "Posztonkénti statisztikák",
            "Kontextuselemzés",
            "Modellkiértékelés",
            "Grafikonok",
            "Szöveges riport",
            "Részletes kommentek",
        ]
    )

    # ========================================================
    # Összegzés
    # ========================================================

    with summary_tab:
        st.subheader(
            "Összesített sentimenteredmények"
        )

        positive_count = int(
            overall_row[
                "total_positive_count"
            ]
        )

        negative_count = int(
            overall_row[
                "total_negative_count"
            ]
        )

        neutral_count = int(
            overall_row[
                "total_neutral_count"
            ]
        )

        positive_ratio = float(
            overall_row[
                "total_positive_ratio"
            ]
        )

        negative_ratio = float(
            overall_row[
                "total_negative_ratio"
            ]
        )

        neutral_ratio = float(
            overall_row[
                "total_neutral_ratio"
            ]
        )

        (
            positive_column,
            negative_column,
            neutral_column,
        ) = st.columns(3)

        with positive_column:
            st.metric(
                "Pozitív kommentek",
                f"{positive_count} db",
                f"{positive_ratio:.2f}%",
            )

        with negative_column:
            st.metric(
                "Negatív kommentek",
                f"{negative_count} db",
                f"{negative_ratio:.2f}%",
            )

        with neutral_column:
            st.metric(
                "Semleges kommentek",
                f"{neutral_count} db",
                f"{neutral_ratio:.2f}%",
            )

        # ----------------------------------------------------
        # Kimeneti fájlok
        # ----------------------------------------------------

        st.subheader(
            "Kimeneti fájlok"
        )

        if result.excel_output_file.exists():
            excel_file_bytes = (
                result
                .excel_output_file
                .read_bytes()
            )

            st.download_button(
                label=(
                    "Excel-eredményfájl letöltése"
                ),
                data=excel_file_bytes,
                file_name=(
                    result.excel_output_file.name
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True,
            )

        else:
            st.warning(
                "Az Excel-eredményfájl nem található."
            )

        if result.report_file.exists():
            report_file_bytes = (
                result.report_file.read_bytes()
            )

            st.download_button(
                label=(
                    "Szöveges riport letöltése"
                ),
                data=report_file_bytes,
                file_name=(
                    result.report_file.name
                ),
                mime="text/plain",
                use_container_width=True,
            )

        else:
            st.warning(
                "A szöveges riport nem található."
            )

    # ========================================================
    # Posztonkénti statisztikák
    # ========================================================

    with post_statistics_tab:
        st.subheader(
            "Posztonkénti statisztikák"
        )

        post_statistics_column_translations = {
            "post_id": "Posztazonosító",
            "post_type": "Poszttípus",
            "comment_count": "Kommentek száma",
            "positive_count": "Pozitív kommentek",
            "negative_count": "Negatív kommentek",
            "neutral_count": "Semleges kommentek",
            "positive_ratio": "Pozitív arány (%)",
            "negative_ratio": "Negatív arány (%)",
            "neutral_ratio": "Semleges arány (%)",
            "dominant_comment_sentiment": (
                "Domináns kommentsentiment"
            ),
            "average_comment_confidence": (
                "Átlagos modellbizonyosság"
            ),
            "post_sentiment_label": (
                "Poszt sentimentje"
            ),
        }

        post_statistics_display_df = (
            create_display_dataframe(
                result.post_statistics_df,
                post_statistics_column_translations,
            )
        )

        if (
            "Domináns kommentsentiment"
            in post_statistics_display_df.columns
        ):
            post_statistics_display_df[
                "Domináns kommentsentiment"
            ] = post_statistics_display_df[
                "Domináns kommentsentiment"
            ].apply(
                translate_sentiment_label
            )

        if (
            "Poszt sentimentje"
            in post_statistics_display_df.columns
        ):
            post_statistics_display_df[
                "Poszt sentimentje"
            ] = post_statistics_display_df[
                "Poszt sentimentje"
            ].apply(
                translate_sentiment_label
            )

        st.dataframe(
            post_statistics_display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # Kontextuselemzés
    # ========================================================

    with context_tab:
        st.subheader(
            "Kontextuselemzési eredmények"
        )

        context_column_translations = {
            "post_id": "Posztazonosító",
            "post_type": "Poszttípus",
            "post_sentiment_label": (
                "Poszt sentimentje"
            ),
            "dominant_comment_sentiment": (
                "Domináns kommentsentiment"
            ),
            "positive_ratio": (
                "Pozitív arány (%)"
            ),
            "negative_ratio": (
                "Negatív arány (%)"
            ),
            "neutral_ratio": (
                "Semleges arány (%)"
            ),
            "context_reaction_type": (
                "Reakciótípus"
            ),
            "context_alignment": (
                "Kontextusilleszkedés"
            ),
            "context_interpretation": (
                "Értelmezés"
            ),
        }

        context_display_df = (
            create_display_dataframe(
                result.context_analysis_df,
                context_column_translations,
            )
        )

        if (
            "Poszt sentimentje"
            in context_display_df.columns
        ):
            context_display_df[
                "Poszt sentimentje"
            ] = context_display_df[
                "Poszt sentimentje"
            ].apply(
                translate_sentiment_label
            )

        if (
            "Domináns kommentsentiment"
            in context_display_df.columns
        ):
            context_display_df[
                "Domináns kommentsentiment"
            ] = context_display_df[
                "Domináns kommentsentiment"
            ].apply(
                translate_sentiment_label
            )

        if (
            "Kontextusilleszkedés"
            in context_display_df.columns
        ):
            context_display_df[
                "Kontextusilleszkedés"
            ] = context_display_df[
                "Kontextusilleszkedés"
            ].apply(
                translate_context_alignment
            )

        st.dataframe(
            context_display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # Modellkiértékelés
    # ========================================================

    with evaluation_tab:
        display_model_evaluation(
            result
        )

    # ========================================================
    # Grafikonok
    # ========================================================

    with charts_tab:
        st.subheader(
            "Létrehozott grafikonok"
        )

        existing_chart_files = [
            chart_file
            for chart_file
            in result.chart_files
            if chart_file.exists()
        ]

        if not existing_chart_files:
            st.warning(
                "Nem találhatók megjeleníthető grafikonok."
            )

        else:
            for chart_file in existing_chart_files:
                st.markdown(
                    "#### "
                    + chart_file
                    .stem
                    .replace("_", " ")
                    .title()
                )

                display_chart_explanation(
                    chart_file
                )

                st.image(
                    str(chart_file),
                    use_container_width=True,
                )

                st.divider()

    # ========================================================
    # Szöveges riport
    # ========================================================

    with report_tab:
        st.subheader(
            "Automatikusan létrehozott riport"
        )

        if result.report_file.exists():
            report_text = (
                result.report_file.read_text(
                    encoding="utf-8"
                )
            )

            st.text_area(
                "Szöveges összefoglaló",
                value=report_text,
                height=500,
                disabled=True,
            )

            st.download_button(
                label=(
                    "Riport letöltése TXT-formátumban"
                ),
                data=report_text.encode(
                    "utf-8"
                ),
                file_name=(
                    result.report_file.name
                ),
                mime="text/plain",
                use_container_width=True,
            )

        else:
            st.warning(
                "A szöveges riport nem található."
            )

    # ========================================================
    # Részletes kommentek
    # ========================================================

    with comments_tab:
        st.subheader(
            "Kommentenkénti sentimenteredmények"
        )

        st.caption(
            "A nyers modellcímke a finomhangolt context-aware "
            "modell közvetlen predikciója. A végleges sentiment "
            "a 0,60-as confidence threshold alkalmazása utáni "
            "eredményt mutatja."
        )

        comment_column_translations = {
            "post_id": (
                "Posztazonosító"
            ),
            "comment_id": (
                "Kommentazonosító"
            ),
            "comment_text": (
                "Eredeti komment"
            ),
            "cleaned_comment_text": (
                "Tisztított komment"
            ),
            "manual_label": (
                "Kézi címke"
            ),
            "finetuned_label": (
                "Nyers modellcímke"
            ),
            "finetuned_confidence": (
                "Modellbizonyosság"
            ),
            "final_sentiment_label": (
                "Végleges sentiment"
            ),
            "threshold_applied": (
                "Threshold alkalmazva"
            ),
        }

        comments_display_df = (
            create_display_dataframe(
                result.full_sentiment_df,
                comment_column_translations,
            )
        )

        # ----------------------------------------------------
        # Facebook módban nincs kézi címke, ezért az üres
        # oszlopot nem jelenítjük meg.
        # ----------------------------------------------------

        if (
            "Kézi címke"
            in comments_display_df.columns
        ):
            manual_label_series = (
                comments_display_df[
                    "Kézi címke"
                ]
            )

            has_manual_labels = (
                manual_label_series.notna()
                & manual_label_series
                .astype(str)
                .str.strip()
                .ne("")
            ).any()

            if not has_manual_labels:
                comments_display_df = (
                    comments_display_df.drop(
                        columns=[
                            "Kézi címke"
                        ]
                    )
                )

        preferred_comment_columns = [
            "Posztazonosító",
            "Kommentazonosító",
            "Eredeti komment",
            "Tisztított komment",
            "Kézi címke",
            "Nyers modellcímke",
            "Modellbizonyosság",
            "Végleges sentiment",
            "Threshold alkalmazva",
        ]

        available_comment_columns = [
            column
            for column
            in preferred_comment_columns
            if column
            in comments_display_df.columns
        ]

        comments_display_df = (
            comments_display_df[
                available_comment_columns
            ]
        )

        if (
            "Kézi címke"
            in comments_display_df.columns
        ):
            comments_display_df[
                "Kézi címke"
            ] = comments_display_df[
                "Kézi címke"
            ].apply(
                translate_sentiment_label
            )

        if (
            "Nyers modellcímke"
            in comments_display_df.columns
        ):
            comments_display_df[
                "Nyers modellcímke"
            ] = comments_display_df[
                "Nyers modellcímke"
            ].apply(
                translate_sentiment_label
            )

        if (
            "Végleges sentiment"
            in comments_display_df.columns
        ):
            comments_display_df[
                "Végleges sentiment"
            ] = comments_display_df[
                "Végleges sentiment"
            ].apply(
                translate_sentiment_label
            )

        st.dataframe(
            comments_display_df,
            use_container_width=True,
            hide_index=True,
            height=550,
            column_config={
                "Modellbizonyosság": (
                    st.column_config.NumberColumn(
                        format="%.3f"
                    )
                ),
                "Threshold alkalmazva": (
                    st.column_config.CheckboxColumn()
                ),
            },
        )


# ============================================================
# Alkalmazás belépési pontja
# ============================================================

def main() -> None:
    """
    A Streamlit alkalmazás fő belépési pontja.
    """

    configure_page()

    display_header()

    (
        source_mode,
        facebook_post_limit,
    ) = display_data_source_selection()

    display_output_information(
        source_mode=source_mode
    )

    display_analysis_button(
        source_mode=source_mode,
        facebook_post_limit=facebook_post_limit,
    )

    if (
        "analysis_result"
        in st.session_state
    ):
        display_analysis_results(
            st.session_state[
                "analysis_result"
            ]
        )


if __name__ == "__main__":
    main()
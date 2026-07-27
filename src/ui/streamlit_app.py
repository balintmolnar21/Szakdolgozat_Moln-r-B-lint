import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))


from sentiment.hubert_sentiment_analyzer import (
    HuBERTSentimentAnalyzer,
)
from pipeline.analysis_pipeline import (
    AnalysisPipelineResult,
    run_analysis_pipeline,
)

DEFAULT_VALIDATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "validacios_teszthalmaz.csv"
)

DEFAULT_POST_CONTEXT_FILE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "post_context.csv"
)

EXCEL_OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sentiment_analysis_results.xlsx"
)

CHARTS_OUTPUT_DIRECTORY = (
    PROJECT_ROOT
    / "outputs"
    / "charts"
)

REPORT_OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "sentiment_summary.txt"
)

@st.cache_resource(show_spinner=False)
def load_sentiment_analyzer() -> HuBERTSentimentAnalyzer:
    """
    Egyszer tölti be a huBERT modellt, majd a későbbi
    Streamlit-futtatások során újra felhasználja.
    """
    return HuBERTSentimentAnalyzer()


def configure_page() -> None:
    """
    Beállítja a Streamlit oldal alapvető tulajdonságait.
    """
    st.set_page_config(
        page_title="Social media hangulatelemző",
        page_icon="📊",
        layout="wide",
    )


def display_header() -> None:
    """
    Megjeleníti az alkalmazás címét és rövid leírását.
    """
    st.title("Social media hangulatelemző szoftver")

    st.write(
        "Magyar nyelvű Facebook-kommentek huBERT-alapú "
        "sentimentelemzése, statisztikai összesítése és "
        "kontextuális értelmezése."
    )

    st.info(
        "A jelenlegi tesztmód a projektben található validációs "
        "CSV-fájlokat használja. A Facebook Graph API-integráció "
        "egy későbbi fejlesztési iterációban készül el."
    )


def display_input_files() -> None:
    """
    Megjeleníti a CSV-alapú tesztmód bemeneti fájljait.
    """
    st.subheader("Bemeneti fájlok")

    validation_exists = DEFAULT_VALIDATION_FILE.exists()
    context_exists = DEFAULT_POST_CONTEXT_FILE.exists()

    first_column, second_column = st.columns(2)

    with first_column:
        st.write("Validációs kommentadatok")
        st.code(str(DEFAULT_VALIDATION_FILE))

        if validation_exists:
            st.success("A validációs fájl elérhető.")
        else:
            st.error("A validációs fájl nem található.")

    with second_column:
        st.write("Posztkontextus-adatok")
        st.code(str(DEFAULT_POST_CONTEXT_FILE))

        if context_exists:
            st.success("A posztkontextus-fájl elérhető.")
        else:
            st.error("A posztkontextus-fájl nem található.")


def display_output_information() -> None:
    """
    Megjeleníti a tervezett kimeneti fájlok helyét.
    """
    st.subheader("Kimenetek")

    st.write("A feldolgozás után létrejövő fő kimenetek:")

    st.code(
        "\n".join(
            [
                str(EXCEL_OUTPUT_FILE),
                str(CHARTS_OUTPUT_DIRECTORY),
                str(REPORT_OUTPUT_FILE),
            ]
        )
    )


def display_analysis_button() -> None:
    """
    Megjeleníti az elemzés indítására szolgáló gombot,
    és lefuttatja a teljes feldolgozási pipeline-t.
    """
    st.subheader("Elemzés indítása")

    input_files_available = (
        DEFAULT_VALIDATION_FILE.exists()
        and DEFAULT_POST_CONTEXT_FILE.exists()
    )

    analysis_button_clicked = st.button(
        "Elemzés indítása",
        type="primary",
        disabled=not input_files_available,
    )

    if not input_files_available:
        st.warning(
            "Az elemzés indításához mindkét bemeneti "
            "CSV-fájlnak rendelkezésre kell állnia."
        )

    if analysis_button_clicked:
        try:
            with st.spinner(
                "A huBERT-modell betöltése és az elemzés "
                "futtatása folyamatban..."
            ):
                analyzer = load_sentiment_analyzer()

                result = run_analysis_pipeline(
                    validation_file=DEFAULT_VALIDATION_FILE,
                    post_context_file=DEFAULT_POST_CONTEXT_FILE,
                    excel_output_file=EXCEL_OUTPUT_FILE,
                    charts_output_directory=(
                        CHARTS_OUTPUT_DIRECTORY
                    ),
                    reports_output_directory=(
                        REPORT_OUTPUT_FILE.parent
                    ),
                    analyzer=analyzer,
                    limit=None,
                )

                st.session_state["analysis_result"] = result

            st.success(
                "Az elemzés sikeresen befejeződött."
            )

        except Exception as error:
            st.error(
                "Az elemzés futtatása közben hiba történt."
            )
            st.exception(error)

def translate_sentiment_label(value) -> str:
    """
    A belső angol sentiment címkéket magyar megnevezésre alakítja.
    """
    translations = {
        "positive": "Pozitív",
        "negative": "Negatív",
        "neutral": "Semleges",
        "mixed": "Vegyes",
        "no_data": "Nincs adat",
    }

    normalized_value = str(value).strip().lower()

    return translations.get(
        normalized_value,
        str(value),
    )


def translate_context_alignment(value) -> str:
    """
    A belső kontextusilleszkedési kategóriákat magyarítja.
    """
    translations = {
        "aligned": "Azonos irányú",
        "opposite": "Ellentétes",
        "mixed": "Vegyes",
        "different": "Eltérő",
        "unclear": "Nem egyértelmű",
    }

    normalized_value = str(value).strip().lower()

    return translations.get(
        normalized_value,
        str(value),
    )


def create_display_dataframe(
    dataframe,
    column_translations: dict[str, str],
):
    """
    Megjelenítési célra másolatot készít a DataFrame-ről,
    majd magyar oszlopnevekre nevezi át a mezőket.

    Az eredeti DataFrame-et nem módosítja.
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

def display_analysis_results(
    result: AnalysisPipelineResult,
) -> None:
    """
    Füles elrendezésben megjeleníti a teljes elemzési pipeline
    legfontosabb eredményeit, grafikonjait és exportfájljait.
    """
    st.header("Elemzési eredmények")

    if result.overall_statistics_df.empty:
        st.warning(
            "Az összesített statisztikai eredmények nem "
            "tartalmaznak megjeleníthető adatot."
        )
        return

    overall_row = result.overall_statistics_df.iloc[0]

    post_count = int(
        overall_row["post_count"]
    )

    comment_count = int(
        overall_row["total_comment_count"]
    )

    dominant_sentiment = translate_sentiment_label(
        overall_row["overall_dominant_sentiment"]
    )

    average_confidence = float(
        overall_row["overall_average_confidence"]
    )

    first_column, second_column, third_column, fourth_column = (
        st.columns(4)
    )

    with first_column:
        st.metric(
            "Feldolgozott posztok",
            post_count,
        )

    with second_column:
        st.metric(
            "Feldolgozott kommentek",
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
        charts_tab,
        report_tab,
        comments_tab,
    ) = st.tabs(
        [
            "Összegzés",
            "Posztonkénti statisztikák",
            "Kontextuselemzés",
            "Grafikonok",
            "Szöveges riport",
            "Részletes kommenteredmények",
        ]
    )

    with summary_tab:
        st.subheader("Összesített sentimenteredmények")

        positive_count = int(
            overall_row["total_positive_count"]
        )

        negative_count = int(
            overall_row["total_negative_count"]
        )

        neutral_count = int(
            overall_row["total_neutral_count"]
        )

        positive_ratio = float(
            overall_row["total_positive_ratio"]
        )

        negative_ratio = float(
            overall_row["total_negative_ratio"]
        )

        neutral_ratio = float(
            overall_row["total_neutral_ratio"]
        )

        positive_column, negative_column, neutral_column = (
            st.columns(3)
        )

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

        st.subheader("Kimeneti fájlok")

        if result.excel_output_file.exists():
            excel_file_bytes = (
                result.excel_output_file.read_bytes()
            )

            st.download_button(
                label="Excel-eredményfájl letöltése",
                data=excel_file_bytes,
                file_name=result.excel_output_file.name,
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
            )
        else:
            st.warning(
                "Az Excel-eredményfájl nem található."
            )

        if result.report_file.exists():
            report_file_bytes = result.report_file.read_bytes()

            st.download_button(
                label="Szöveges riport letöltése",
                data=report_file_bytes,
                file_name=result.report_file.name,
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.warning(
                "A szöveges riport nem található."
            )

    with post_statistics_tab:
        st.subheader("Posztonkénti statisztikák")

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
            "post_sentiment_label": "Poszt sentimentje",
        }

        post_statistics_display_df = create_display_dataframe(
            result.post_statistics_df,
            post_statistics_column_translations,
        )

        if "Domináns kommentsentiment" in (
            post_statistics_display_df.columns
        ):
            post_statistics_display_df[
                "Domináns kommentsentiment"
            ] = post_statistics_display_df[
                "Domináns kommentsentiment"
            ].apply(translate_sentiment_label)

        if "Poszt sentimentje" in (
            post_statistics_display_df.columns
        ):
            post_statistics_display_df[
                "Poszt sentimentje"
            ] = post_statistics_display_df[
                "Poszt sentimentje"
            ].apply(translate_sentiment_label)

        st.dataframe(
            post_statistics_display_df,
            use_container_width=True,
            hide_index=True,
        )

    with context_tab:
        st.subheader("Kontextuselemzési eredmények")

        context_column_translations = {
            "post_id": "Posztazonosító",
            "post_type": "Poszttípus",
            "post_sentiment_label": "Poszt sentimentje",
            "dominant_comment_sentiment": (
                "Domináns kommentsentiment"
            ),
            "positive_ratio": "Pozitív arány (%)",
            "negative_ratio": "Negatív arány (%)",
            "neutral_ratio": "Semleges arány (%)",
            "context_reaction_type": "Reakciótípus",
            "context_alignment": "Kontextusilleszkedés",
            "context_interpretation": "Értelmezés",
        }

        context_display_df = create_display_dataframe(
            result.context_analysis_df,
            context_column_translations,
        )

        if "Poszt sentimentje" in context_display_df.columns:
            context_display_df[
                "Poszt sentimentje"
            ] = context_display_df[
                "Poszt sentimentje"
            ].apply(translate_sentiment_label)

        if "Domináns kommentsentiment" in (
            context_display_df.columns
        ):
            context_display_df[
                "Domináns kommentsentiment"
            ] = context_display_df[
                "Domináns kommentsentiment"
            ].apply(translate_sentiment_label)

        if "Kontextusilleszkedés" in (
            context_display_df.columns
        ):
            context_display_df[
                "Kontextusilleszkedés"
            ] = context_display_df[
                "Kontextusilleszkedés"
            ].apply(translate_context_alignment)

        st.dataframe(
            context_display_df,
            use_container_width=True,
            hide_index=True,
        )

    with charts_tab:
        st.subheader("Létrehozott grafikonok")

        existing_chart_files = [
            chart_file
            for chart_file in result.chart_files
            if chart_file.exists()
        ]

        if not existing_chart_files:
            st.warning(
                "Nem találhatók megjeleníthető grafikonok."
            )
        else:
            for chart_file in existing_chart_files:
                st.image(
                    str(chart_file),
                    caption=chart_file.stem,
                    use_container_width=True,
                )

    with report_tab:
        st.subheader("Automatikusan létrehozott riport")

        if result.report_file.exists():
            report_text = result.report_file.read_text(
                encoding="utf-8"
            )

            st.text_area(
                "Szöveges összefoglaló",
                value=report_text,
                height=500,
                disabled=True,
            )

            st.download_button(
                label="Riport letöltése TXT-formátumban",
                data=report_text.encode("utf-8"),
                file_name=result.report_file.name,
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.warning(
                "A szöveges riport nem található."
            )

    with comments_tab:
        st.subheader("Kommentenkénti sentimenteredmények")

        comment_column_translations = {
            "post_id": "Posztazonosító",
            "comment_id": "Kommentazonosító",
            "comment_text": "Eredeti komment",
            "cleaned_comment_text": "Tisztított komment",
            "manual_label": "Kézi címke",
            "model_label": "Modell címkéje",
            "confidence": "Modellbizonyosság",
            "original_model_label": (
                "Eredeti modellcímke"
            ),
        }

        comments_display_df = create_display_dataframe(
            result.full_sentiment_df,
            comment_column_translations,
        )

        preferred_comment_columns = [
            "Posztazonosító",
            "Kommentazonosító",
            "Eredeti komment",
            "Tisztított komment",
            "Kézi címke",
            "Modell címkéje",
            "Modellbizonyosság",
            "Eredeti modellcímke",
        ]

        available_comment_columns = [
            column
            for column in preferred_comment_columns
            if column in comments_display_df.columns
        ]

        comments_display_df = comments_display_df[
            available_comment_columns
        ]

        if "Kézi címke" in comments_display_df.columns:
            comments_display_df[
                "Kézi címke"
            ] = comments_display_df[
                "Kézi címke"
            ].apply(translate_sentiment_label)

        if "Modell címkéje" in comments_display_df.columns:
            comments_display_df[
                "Modell címkéje"
            ] = comments_display_df[
                "Modell címkéje"
            ].apply(translate_sentiment_label)

        st.dataframe(
            comments_display_df,
            use_container_width=True,
            hide_index=True,
            height=550,
        )


def main() -> None:
    configure_page()
    display_header()
    display_input_files()
    display_output_information()
    display_analysis_button()

    if "analysis_result" in st.session_state:
        display_analysis_results(
            st.session_state["analysis_result"]
        )

if __name__ == "__main__":
    main()
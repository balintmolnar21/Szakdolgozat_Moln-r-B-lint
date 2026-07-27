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

def display_analysis_results(
    result: AnalysisPipelineResult,
) -> None:
    """
    Megjeleníti a pipeline legfontosabb eredményeit.
    """
    st.header("Elemzési eredmények")

    overall_row = result.overall_statistics_df.iloc[0]

    first_column, second_column, third_column = st.columns(3)

    with first_column:
        st.metric(
            "Feldolgozott posztok",
            int(overall_row["post_count"]),
        )

    with second_column:
        st.metric(
            "Feldolgozott kommentek",
            int(overall_row["total_comment_count"]),
        )

    with third_column:
        st.metric(
            "Domináns sentiment",
            str(
                overall_row[
                    "overall_dominant_sentiment"
                ]
            ),
        )

    st.subheader("Posztonkénti statisztikák")
    st.dataframe(
        result.post_statistics_df,
        use_container_width=True,
    )

    st.subheader("Kontextuselemzési eredmények")
    st.dataframe(
        result.context_analysis_df,
        use_container_width=True,
    )

    st.subheader("Létrehozott grafikonok")

    for chart_file in result.chart_files:
        if chart_file.exists():
            st.image(
                str(chart_file),
                caption=chart_file.stem,
                use_container_width=True,
            )

    st.subheader("Szöveges összefoglaló")

    if result.report_file.exists():
        report_text = result.report_file.read_text(
            encoding="utf-8"
        )

        st.text_area(
            "Automatikusan létrehozott riport",
            value=report_text,
            height=400,
        )

    st.success(
        f"Excel-eredményfájl: {result.excel_output_file}"
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
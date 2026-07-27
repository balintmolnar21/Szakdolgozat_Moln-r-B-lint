from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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
    Megjeleníti az elemzés indítására szolgáló gombot.

    Ebben az első változatban még nem futtatja a teljes feldolgozási
    folyamatot, csak ellenőrzi a felület működését.
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

    if analysis_button_clicked:
        st.success(
            "A Streamlit felület megfelelően működik. "
            "A következő lépésben ehhez a gombhoz kapcsoljuk "
            "a teljes elemzési pipeline-t."
        )


def main() -> None:
    """
    A Streamlit alkalmazás belépési pontja.
    """
    configure_page()
    display_header()
    display_input_files()
    display_output_information()
    display_analysis_button()


if __name__ == "__main__":
    main()
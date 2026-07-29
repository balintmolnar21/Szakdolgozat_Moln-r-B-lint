import sys
from pathlib import Path

import streamlit as st
from pandas.errors import EmptyDataError, ParserError


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

EVALUATION_OUTPUT_DIRECTORY = (
    PROJECT_ROOT / "outputs" / "evaluation"
)

@st.cache_resource(show_spinner=False)
def load_sentiment_analyzer() -> HuBERTSentimentAnalyzer:
    print("HU­BERT MODELL TÉNYLEGES BETÖLTÉSE")
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

def clear_previous_analysis() -> None:
    
    session_keys_to_delete = [
        "analysis_result",
        "analysis_success",
    ]

    for key in session_keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]


def display_analysis_error(error: Exception) -> None:
    
    if isinstance(error, FileNotFoundError):
        st.error(
            "A feldolgozáshoz szükséges egyik bemeneti fájl "
            "nem található. Ellenőrizd a CSV-fájlok helyét."
        )

    elif isinstance(error, EmptyDataError):
        st.error(
            "Az egyik bemeneti CSV-fájl üres, ezért az elemzés "
            "nem indítható el."
        )

    elif isinstance(error, ParserError):
        st.error(
            "A CSV-fájl szerkezete nem értelmezhető. "
            "Ellenőrizd az elválasztó karaktereket, az oszlopokat "
            "és az idézőjelek használatát."
        )

    elif isinstance(error, UnicodeDecodeError):
        st.error(
            "A bemeneti fájl karakterkódolása nem megfelelő. "
            "A CSV-fájlt célszerű UTF-8 kódolással menteni."
        )

    elif isinstance(error, PermissionError):
        st.error(
            "A program nem tudta megnyitni vagy felülírni az egyik "
            "kimeneti fájlt. Ellenőrizd, hogy az Excel-fájl vagy "
            "más kimenet nincs-e megnyitva egy másik programban."
        )

    elif isinstance(error, ValueError):
        st.error(
            "A bemeneti adatok szerkezete vagy tartalma nem megfelelő. "
            "Ellenőrizd a kötelező oszlopokat és azt, hogy az "
            "adathalmaz tartalmaz-e feldolgozható rekordokat."
        )

    elif isinstance(error, RuntimeError):
        st.error(
            "A modell betöltése vagy futtatása közben technikai "
            "hiba történt. Ellenőrizd a PyTorch-, Transformers- "
            "és modellbeállításokat."
        )

    elif isinstance(error, OSError):
        st.error(
            "Fájl- vagy mappakezelési hiba történt. Ellenőrizd, "
            "hogy a kimeneti könyvtárak elérhetők és írhatók-e."
        )

    else:
        st.error(
            "Az elemzés futtatása közben nem várt hiba történt."
        )

    with st.expander("Technikai részletek"):
        st.exception(error)


def display_analysis_button() -> None:
    
    st.subheader("Elemzés vezérlése")

    input_files_available = (
        DEFAULT_VALIDATION_FILE.exists()
        and DEFAULT_POST_CONTEXT_FILE.exists()
    )

    start_column, clear_column = st.columns(2)

    with start_column:
        analysis_button_clicked = st.button(
            "Elemzés indítása",
            type="primary",
            disabled=not input_files_available,
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

    if st.session_state.get("analysis_success", False):
        st.success(
            "Az elemzés sikeresen befejeződött."
        )

        st.session_state["analysis_success"] = False

    if not input_files_available:
        st.warning(
            "Az elemzés indításához mindkét bemeneti "
            "CSV-fájlnak rendelkezésre kell állnia."
        )

    if clear_button_clicked:
        clear_previous_analysis()

        st.session_state["clear_success"] = True

        st.rerun()

    if st.session_state.get("clear_success", False):
        st.success(
            "A korábbi elemzési eredmények törlésre kerültek."
        )

        st.session_state["clear_success"] = False

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
                    evaluation_output_directory=Path(
                        "outputs/evaluation"
                    ),
                    analyzer=analyzer,
                    limit=None,
                )

                st.session_state["analysis_result"] = result
                st.session_state["analysis_success"] = True

            st.rerun()

        except Exception as error:
            display_analysis_error(error)

def translate_sentiment_label(value) -> str:
    
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

def display_metric_explanations() -> None:
    """
    Röviden ismerteti a modellkiértékelés fő mérőszámait.
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
        A magasabb érték nagyobb modellbizonyosságot jelez, de nem garantálja
        a predikció tényleges helyességét.
        """
    )


def display_chart_explanation(chart_file: Path) -> None:
    """
    Rövid magyarázatot jelenít meg az adott grafikonhoz.
    """
    chart_explanations = {
        "overall_sentiment_distribution.png": (
            "A diagram az összes vizsgált komment pozitív, negatív és "
            "semleges megoszlását mutatja."
        ),
        "post_sentiment_distribution.png": (
            "A diagram posztonként hasonlítja össze a pozitív, negatív "
            "és semleges kommentek arányát."
        ),
        "average_confidence_by_post.png": (
            "A diagram azt mutatja meg, hogy a modell átlagosan mennyire "
            "volt biztos az egyes posztok kommentjeinek besorolásában."
        ),
        "context_alignment_distribution.png": (
            "A diagram a poszt tartalma és a kommentek domináns hangulata "
            "közötti illeszkedés megoszlását szemlélteti."
        ),
        "confusion_matrix.png": (
            "A confusion matrix sorai a kézi címkéket, oszlopai a modell "
            "predikcióit mutatják. A főátlóban találhatók a helyes találatok."
        ),
        "classification_metrics.png": (
            "A diagram sentimentkategóriánként hasonlítja össze a "
            "precision, recall és F1-score értékeket."
        ),
    }

    explanation = chart_explanations.get(
        chart_file.name,
        "A grafikon az elemzés egyik összesített eredményét szemlélteti.",
    )

    st.caption(explanation)

def display_model_evaluation(result) -> None:
    """
    Megjeleníti a modellkiértékelés fő eredményeit.
    """
    evaluation_result = result.evaluation_result

    st.subheader("Modellkiértékelés")

    evaluated_count = len(
        evaluation_result.evaluated_data
    )

    misclassified_count = len(
        evaluation_result.misclassified_comments
    )

    low_confidence_count = len(
        evaluation_result.low_confidence_comments
    )

    metric_column_1, metric_column_2, metric_column_3 = st.columns(3)

    with metric_column_1:
        st.metric(
            label="Accuracy",
            value=f"{evaluation_result.accuracy:.2%}",
        )

    with metric_column_2:
        st.metric(
            label="Hibás predikciók",
            value=misclassified_count,
        )

    with metric_column_3:
        st.metric(
            label="Alacsony konfidenciájú esetek",
            value=low_confidence_count,
        )

    st.caption(
        f"Összesen {evaluated_count} kézzel címkézett komment "
        "került bevonásra a modell kiértékelésébe."
    )

    with st.expander("A mérőszámok rövid magyarázata"):
        display_metric_explanations()

    st.subheader("Osztályonkénti eredmények")

    metrics_display_df = evaluation_result.metrics.copy()

    metrics_display_df = metrics_display_df.rename(
        columns={
            "category": "Kategória",
            "precision": "Precision",
            "recall": "Recall",
            "f1_score": "F1-score",
            "support": "Esetszám",
        }
    )

    category_translations = {
        "negative": "Negatív",
        "neutral": "Semleges",
        "positive": "Pozitív",
        "macro_avg": "Makróátlag",
        "weighted_avg": "Súlyozott átlag",
    }

    metrics_display_df["Kategória"] = (
        metrics_display_df["Kategória"].replace(
            category_translations
        )
    )

    st.dataframe(
        metrics_display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Precision": st.column_config.NumberColumn(
                format="%.3f"
            ),
            "Recall": st.column_config.NumberColumn(
                format="%.3f"
            ),
            "F1-score": st.column_config.NumberColumn(
                format="%.3f"
            ),
        },
    )

    st.subheader("Confusion matrix")

    st.caption(
        "A sorok az ember által megadott címkéket, az oszlopok a modell "
        "által előre jelzett kategóriákat jelentik."
    )

    st.dataframe(
        evaluation_result.confusion_matrix,
        use_container_width=True,
    )

    st.subheader("Hibás predikciók")

    if evaluation_result.misclassified_comments.empty:
        st.success(
            "A kiértékelt adatok között nem található hibás predikció."
        )
    else:
        misclassified_columns = [
            column
            for column in [
                "comment_text",
                "manual_label",
                "model_label",
                "confidence",
            ]
            if column
            in evaluation_result.misclassified_comments.columns
        ]

        st.dataframe(
            evaluation_result.misclassified_comments[
                misclassified_columns
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Alacsony konfidenciájú predikciók")

    st.caption(
        "Ide azok a kommentek kerülnek, amelyeknél a modell "
        "konfidenciaértéke 0,60 alatti. Ezek a predikciók "
        "bizonytalanabbnak tekinthetők, ezért külön ellenőrzésük indokolt."
    )

    if evaluation_result.low_confidence_comments.empty:
        st.info(
            "Nem található 0,60 alatti konfidenciájú predikció."
        )
    else:
        low_confidence_columns = [
            column
            for column in [
                "comment_text",
                "manual_label",
                "model_label",
                "confidence",
            ]
            if column
            in evaluation_result.low_confidence_comments.columns
        ]

        st.dataframe(
            evaluation_result.low_confidence_comments[
                low_confidence_columns
            ],
            use_container_width=True,
            hide_index=True,
        )


def display_analysis_results(
    result: AnalysisPipelineResult,
) -> None:
    
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
            for chart_file in result.chart_files:
                st.markdown(
                    f"#### {chart_file.stem.replace('_', ' ').title()}"
                )

                display_chart_explanation(chart_file)

                st.image(
                    str(chart_file),
                    use_container_width=True,
                )

                st.divider()

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

    with evaluation_tab:
            display_model_evaluation(result)


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
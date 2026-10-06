# „Social media” hangulatelemző szoftver

## Saját adatok

- **Név:** Molnár Bálint Ottó
- **Neptun-kód:** VP35W1
- **Szak:** Mérnökinformatikus BSc
- **Intézmény:** Széchenyi István Egyetem
- **Készítés éve:** 2026

---

## Projektállapot

A projekt szakdolgozati prototípusként funkcionálisan elkészült.

A rendszer jelenlegi változata két adatforrást támogat:

1. **kézzel címkézett CSV tesztadatokat**, amelyek a modell objektív kiértékelésére használhatók;
2. **Facebook Graph API-adatokat**, amelyek egy adminisztrált Facebook-oldal legutóbbi bejegyzéseiből, főkommentjeiből és a kommentekre adott válaszokból származnak.

A két adatforrás ugyanabba a központi feldolgozási pipeline-ba kerül. A Facebook API-ból származó adatokhoz nem tartozik ember által megadott `manual_label`, ezért Accuracy, Precision, Recall, F1-score és confusion matrix csak a kézzel címkézett teszthalmazon számítható.

---

## Projektleírás

Ez a repository egy Python-alapú szoftverprototípust tartalmaz, amely magyar nyelvű Facebook-kommentek automatikus hangulatelemzésére készült.

A rendszer egy finomhangolt, huBERT-alapú magyar nyelvi sentimentmodellt használ. A kommentek elemzése nem önmagában történik: a modell a **Facebook-poszt szövegét és a hozzá tartozó komment szövegét együtt** kapja bemenetként.

A feldolgozás eredménye három sentimentkategória egyike:

- **pozitív**,
- **negatív**,
- **semleges**.

A rendszer a modell nyers predikciója mellett konfidenciaértéket is kezel. A végleges alkalmazásban használt operatív confidence threshold értéke **0,60**. Ha egy pozitív vagy negatív nyers predikció konfidenciája 0,60 alatti, a rendszer a végleges sentimentcímkét semlegesre módosítja. A nyers semleges predikciókat a threshold nem módosítja.

A program az eredményeket statisztikailag összesíti, szabályalapú kontextuselemzést végez, grafikonokat és szöveges riportot készít, valamint Streamlit-alapú grafikus felületen jeleníti meg a főbb eredményeket.

---

## A megoldandó probléma

Egy Facebook-bejegyzéshez rövid idő alatt nagy mennyiségű hozzászólás érkezhet. Ezek kézi feldolgozása időigényes, nehezen ismételhető és szubjektív lehet.

A rendszer célja, hogy az adminisztrált Facebook-oldal bejegyzéseihez tartozó szöveges visszajelzéseket automatikusan feldolgozza, meghatározza azok hangulati kategóriáját, majd összesített képet adjon a bejegyzések fogadtatásáról.

A projekt különösen a magyar nyelvű, informális közösségimédia-szövegek sajátosságaira fókuszál, például:

- rövid kommentek,
- elírások,
- szleng,
- emojik,
- kontextusfüggő megfogalmazások,
- vegyes érzelmi tartalom,
- implicit vagy ironikus megfogalmazások.

A rendszer nem külön iróniafelismerő modell. A posztkontextus bevonása azonban egyes kontextusfüggő vagy implicit sentimentet tartalmazó esetek kezelését javíthatja.

---

## A rendszer fő funkciói

A prototípus képes:

- CSV-formátumú kommentadatok beolvasására;
- posztkontextus-adatok kezelésére;
- kommentek és posztok összekapcsolására;
- magyar nyelvű szöveg-előfeldolgozásra;
- emojik szöveges reprezentációvá alakítására;
- context-aware huBERT-alapú sentiment elemzésre;
- confidence threshold alkalmazására;
- statisztikai összesítésre;
- szabályalapú kontextuselemzésre;
- kézzel címkézett adatokon modellkiértékelésre;
- hibás és alacsony konfidenciájú predikciók kigyűjtésére;
- Facebook Graph API-alapú posztlekérésre;
- a legutóbbi N Facebook-bejegyzés lekérésére;
- Facebook-főkommentek lekérésére;
- kommentekre adott válaszok lekérésére;
- lapozott API-válaszok kezelésére;
- Facebook-adatok pandas DataFrame formára alakítására;
- Excel-fájl exportálására;
- grafikonok készítésére;
- szöveges riport létrehozására;
- Streamlit-alapú megjelenítésre;
- CSV és Facebook API adatforrás közötti választásra;
- az eredmények letöltésére.

---

## A sentimentmodell

### Alapmodell

A projekt kiindulási magyar sentimentmodellje:

```text
NYTK/sentiment-hts5-hubert-hungarian
```

A baseline rendszer az eredeti ötosztályos modellkimenetet három sentimentkategóriára képezte le.

### Finomhangolt context-aware modell

A végleges rendszer egy domain-specifikusan finomhangolt, háromosztályos modellt használ.

A modell bemenete:

```text
poszt szövege + komment szövege
```

A célváltozó a komment sentimentje.

A három osztály:

```text
negative
neutral
positive
```

A modell a következő könyvtárból töltődik be:

```text
models/context_aware_hubert_text/
```

### Emoji-kezelés

A fine-tuning és az inference során az emojik szöveges reprezentációja kerül alkalmazásra.

Például:

```text
😂 → nevetős emoji
❤️ → szív emoji
```

A végleges pipeline beállítása:

```text
emoji_mode = "text"
```

### Confidence threshold

A végleges alkalmazás operatív threshold értéke:

```text
0.60
```

A szabály:

```text
ha a nyers predikció pozitív vagy negatív
ÉS
a konfidencia < 0.60
AKKOR
a végleges címke = semleges
```

A threshold kizárólag a pozitív és negatív nyers predikciókat módosíthatja.

---

## Modellvalidáció és tesztelés

A fejlesztés során elkülönített tanító-, validációs- és teszthalmaz került alkalmazásra.

| Adathalmaz | Rekordszám | Szerep |
|---|---:|---|
| Train | 400 | finomhangolás |
| Validation | 100 | modellválasztás, learning rate és threshold vizsgálata |
| Test | 230 | végső modellkiértékelés |

A végső modell főbb tanítási beállításai:

```text
learning_rate = 2e-5
num_train_epochs = 4
max_length = 128
seed = 42
emoji_mode = "text"
```

A négy epochos tanítás során a validációs eredmények alapján a második epoch adta a legjobb modellt, amelyet a tréningfolyamat automatikusan visszatöltött.

A végső teszthalmazon mért fő eredmények:

| Modellváltozat | Accuracy | Macro F1 |
|---|---:|---:|
| Baseline huBERT | 0.6565 | 0.6561 |
| Finomhangolt context-aware modell, threshold nélkül | 0.6957 | 0.6767 |
| Finomhangolt context-aware modell, 0.60 threshold | 0.7130 | 0.7081 |

A validációs threshold-vizsgálatban a **0,70** érték adta a legmagasabb Macro F1-et. A végleges alkalmazásban ugyanakkor a kevésbé agresszív **0,60-as operatív threshold** került használatra.

Fontos módszertani megjegyzés: a baseline és a végleges modell közötti különbség egyszerre tartalmazza a domain-specifikus finomhangolás és a posztkontextus bevonásának hatását, ezért a teljesítménynövekedés nem tulajdonítható kizárólag a kontextus használatának.

---

## Fejlesztési környezet beállítása

A projekt futtatásához **Python 3.11** használata javasolt.

### 1. A projekt mappájának megnyitása

```powershell
cd "C:\Users\USER\Desktop\projektek_fejlesztes\diplomamunka\Szakdolgozat_Moln-r-B-lint"
```

### 2. Virtuális környezet létrehozása

```powershell
py -3.11 -m venv .venv
```

### 3. Virtuális környezet aktiválása

PowerShell használata esetén:

```powershell
.venv\Scripts\Activate.ps1
```

Parancssor használata esetén:

```cmd
.venv\Scripts\activate
```

### 4. A pip frissítése

```powershell
python -m pip install --upgrade pip
```

### 5. Függőségek telepítése

```powershell
python -m pip install -r requirements.txt
```

---

## Fontos – modellfájlok letöltése

A finomhangolt huBERT-alapú modell nagy méretű bináris állományai a GitHub fájlméret-korlátai és a repository méretének csökkentése miatt nem kerülnek verziókezelés alá.

A külön letölthető fájlok:

```text
model.safetensors
training_args.bin
```

A fájlok az alábbi OneDrive/SharePoint mappából tölthetők le:

[Molnar_Balint_szakdoga – modellfájlok](https://laesze-my.sharepoint.com/:f:/g/personal/molnar_balint_otto_hallgato_sze_hu/IgDs8n03EgZ-T7ZP3tdJ0vQhAcwaNnjKvLoHi_YbYXH9lF4?e=oeYMFm)

A fájlokat a következő könyvtárba kell elhelyezni:

```text
models/context_aware_hubert_text/
```

A normál inference futtatásához a `model.safetensors` szükséges. A `training_args.bin` a tanítási beállítások megőrzéséhez és reprodukálhatósági célokra hasznos, de a normál sentiment inference közvetlenül nem igényli.

A modellkönyvtár további konfigurációs és tokenizer fájljai a repository-ban maradhatnak, például:

```text
config.json
tokenizer.json
tokenizer_config.json
training_metrics.json
validation_metrics.json
```

---

## Facebook Graph API konfiguráció

A Facebook API használatához szükséges érzékeny adatok a projekt gyökerében található helyi `.env` fájlban tárolhatók:

```env
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_GRAPH_API_VERSION=v25.0
```

A valódi `.env` fájl **nem kerülhet verziókezelés alá**. A repository kizárólag a `.env.example` mintafájlt tartalmazza.

Az access tokent nem szabad forráskódba írni, GitHubra feltölteni vagy nyilvánosan megosztani.

A Facebook funkció olyan adminisztrált oldal adataira készült, amelyhez a szükséges API-hozzáférés szabályosan rendelkezésre áll.

---

## Alkalmazott technológiák

A projekt főbb technológiái:

- **Python 3.11**
- **pandas**
- **Matplotlib**
- **openpyxl**
- **Hugging Face Transformers**
- **PyTorch**
- **huBERT-alapú magyar sentimentmodell**
- **Streamlit**
- **scikit-learn**
- **python-dotenv**
- **requests**
- **Facebook Graph API**
- **Git és GitHub**

A `scikit-learn` biztosítja a modellkiértékelés során használt Accuracy, Precision, Recall, F1-score és confusion matrix számítását.

---

## Projektstruktúra

```text
Szakdolgozat_Moln-r-B-lint/
├── data/
│   ├── mock/
│   ├── processed/
│   ├── raw/
│   └── validation/
│       ├── train_comments.csv
│       ├── train_post_context.csv
│       ├── validation_comments.csv
│       ├── validation_post_context.csv
│       ├── test_comments.csv
│       └── test_post_context.csv
├── docs/
│   └── development_log.md
├── models/
│   └── context_aware_hubert_text/
├── outputs/
│   ├── charts/
│   │   └── facebook/
│   ├── evaluation/
│   ├── exports/
│   ├── reports/
│   │   └── facebook/
│   └── training/
├── src/
│   ├── analytics/
│   │   └── sentiment_statistics.py
│   ├── context_analysis/
│   │   └── context_analyzer.py
│   ├── data_input/
│   │   └── csv_loader.py
│   ├── data_model/
│   │   └── schema.py
│   ├── evaluation/
│   │   ├── model_evaluator.py
│   │   ├── evaluation_exporter.py
│   │   ├── evaluation_visualizer.py
│   │   └── context_aware_error_analysis.py
│   ├── facebook_api/
│   │   ├── config.py
│   │   ├── graph_api_client.py
│   │   ├── post_fetcher.py
│   │   ├── comment_fetcher.py
│   │   └── facebook_data_mapper.py
│   ├── pipeline/
│   │   └── analysis_pipeline.py
│   ├── preprocessing/
│   │   ├── emoji_lib.py
│   │   └── text_preprocessor.py
│   ├── reporting/
│   │   └── summary_report.py
│   ├── sentiment/
│   │   ├── hubert_sentiment_analyzer.py
│   │   └── context_aware_sentiment_analyzer.py
│   ├── training/
│   ├── ui/
│   │   └── streamlit_app.py
│   ├── visualization/
│   │   └── sentiment_visualizer.py
│   └── main.py
├── tests/
├── tools/
│   ├── train_context_aware_model.py
│   ├── evaluate_final_test.py
│   └── analyze_confidence_thresholds.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Fő modulok

### Adatbeolvasás

```text
src/data_input/csv_loader.py
```

Feladata:

- címkézett CSV-adatok beolvasása;
- posztkontextus-adatok beolvasása;
- kommentek és posztok összekapcsolása;
- kötelező oszlopok ellenőrzése.

### Szöveg-előfeldolgozás

```text
src/preprocessing/text_preprocessor.py
src/preprocessing/emoji_lib.py
```

Feladata:

- szövegek normalizálása;
- URL-ek kezelése;
- fölösleges szóközök és sortörések eltávolítása;
- emojik szöveges reprezentációvá alakítása;
- a modell bemenetének előkészítése.

### Context-aware sentiment elemzés

```text
src/sentiment/context_aware_sentiment_analyzer.py
```

Feladata:

- a finomhangolt háromosztályos modell betöltése;
- `post_text + comment_text` párok elemzése;
- pozitív, negatív és semleges nyers predikció meghatározása;
- konfidenciaérték előállítása;
- 0,60-as confidence threshold alkalmazása;
- kompatibilitási sentimentoszlopok előállítása.

A fő kimeneti oszlopok:

```text
finetuned_label
finetuned_confidence
final_sentiment_label
threshold_applied
model_label
confidence
```

### Baseline huBERT modul

```text
src/sentiment/hubert_sentiment_analyzer.py
```

A végleges pipeline-ban ez a modul nem a komment végleges sentimentjét határozza meg. A rendszer a baseline modellt a poszt önálló sentimentjének meghatározására használja, amelyre a szabályalapú kontextuselemző modulnak szüksége van.

### Statisztikai összesítés

```text
src/analytics/sentiment_statistics.py
```

Feladata:

- kommentek darabszámának meghatározása;
- pozitív, negatív és semleges arányok kiszámítása;
- domináns sentiment meghatározása;
- átlagos modellbizonyosság számítása;
- több munkalapos Excel-fájl létrehozása.

### Kontextuselemzés

```text
src/context_analysis/context_analyzer.py
```

Feladata:

- a poszt sentimentjének és a kommentek domináns sentimentjének összevetése;
- reakciótípus meghatározása;
- kontextusilleszkedés meghatározása;
- rövid szöveges értelmezés készítése.

A modul szabályalapú, nem végez teljes körű stance detection vagy iróniafelismerést.

### Modellkiértékelés

```text
src/evaluation/
```

Feladata:

- a kézi és a modell által előállított címkék összehasonlítása;
- Accuracy, Precision, Recall és F1-score számítása;
- confusion matrix létrehozása;
- hibás predikciók kigyűjtése;
- alacsony konfidenciájú eredmények azonosítása;
- a kiértékelési eredmények fájlba mentése és vizualizálása.

A modellkiértékelés csak olyan adatokon értelmezhető, amelyekhez `manual_label` is tartozik.

### Facebook Graph API

```text
src/facebook_api/
```

Feladata:

- Facebook Graph API-kapcsolat kezelése;
- access token, Page ID és API-verzió betöltése környezeti változókból;
- a legutóbbi N Facebook-bejegyzés lekérése;
- főkommentek lekérése;
- kommentekre adott válaszok lekérése;
- pagination kezelése;
- API-hibák kezelése;
- adatok normalizálása;
- pandas DataFrame-ek előállítása.

A főkommentek és a válaszkommentek a sentiment pipeline-ban egységesen feldolgozandó hozzászólásként jelennek meg. Mindkét esetben az eredeti Facebook-poszt szövege szolgál kontextusként.

A rendszer jelenlegi változata nem végez automatikus képfelismerést vagy videótartalom-elemzést. A Facebook API-ból lekért poszt **szöveges tartalma** kerül közvetlenül sentimentkontextusként felhasználásra.

### Közös feldolgozási pipeline

```text
src/pipeline/analysis_pipeline.py
```

A modul egy közös elemzési folyamatot biztosít mind a CSV-, mind a Facebook-adatok számára.

Fő belépési pontok:

```text
run_analysis_pipeline(...)
run_analysis_pipeline_from_dataframes(...)
```

A CSV-s belépési pont betölti a fájlokat, majd továbbadja az adatokat a közös DataFrame-alapú pipeline-nak.

A Facebook API-ból származó DataFrame-ek közvetlenül a közös pipeline-ba adhatók.

### Vizualizáció

```text
src/visualization/sentiment_visualizer.py
```

Feladata:

- teljes sentimenteloszlás ábrázolása;
- posztonkénti sentimentarányok megjelenítése;
- átlagos modellbizonyosság ábrázolása;
- kontextusilleszkedési eredmények megjelenítése.

A modellkiértékeléshez tartozó grafikonokat a következő modul készíti:

```text
src/evaluation/evaluation_visualizer.py
```

### Riportkészítés

```text
src/reporting/summary_report.py
```

Feladata:

- összesített szöveges riport készítése;
- sentimentmegoszlás összegzése;
- domináns sentiment meghatározása;
- legpozitívabb és legnegatívabb poszt meghatározása;
- modellbizonyosság összegzése;
- posztonkénti kontextuális értelmezések megjelenítése.

### Streamlit felület

```text
src/ui/streamlit_app.py
```

Feladata:

- adatforrás kiválasztása;
- CSV tesztmód és Facebook API mód kezelése;
- Facebook módban az elemzendő legutóbbi posztok számának megadása;
- elemzés indítása;
- főbb statisztikák megjelenítése;
- modellkiértékelési eredmények megjelenítése CSV módban;
- grafikonok és riport megjelenítése;
- Excel- és TXT-fájl letöltése;
- korábbi eredmények törlése;
- felhasználóbarát hibakezelés.

A modell a Streamlit `cache_resource` funkciójával gyorsítótárazásra kerül, így nem töltődik újra minden felületi interakció során.

---

## A rendszer működési folyamata

### CSV-alapú feldolgozás

```text
test_comments.csv
+
test_post_context.csv
        ↓
CSV-adatok betöltése
        ↓
kommentek és posztok összekapcsolása
        ↓
szöveg-előfeldolgozás
        ↓
post_text + comment_text
        ↓
context-aware fine-tuned huBERT
        ↓
0.60 confidence threshold
        ↓
statisztikai összesítés
        ↓
szabályalapú kontextuselemzés
        ↓
modellkiértékelés
        ↓
Excel + grafikonok + riport
        ↓
Streamlit megjelenítés
```

### Facebook API-alapú feldolgozás

```text
Facebook oldal
        ↓
legutóbbi N bejegyzés
        ↓
főkommentek + válaszkommentek
        ↓
comments_df + post_context_df
        ↓
szöveg-előfeldolgozás
        ↓
post_text + comment_text
        ↓
context-aware fine-tuned huBERT
        ↓
0.60 confidence threshold
        ↓
statisztikai összesítés
        ↓
szabályalapú kontextuselemzés
        ↓
Excel + grafikonok + riport
        ↓
Streamlit megjelenítés
```

Facebook API módban a modellkiértékelési lépés kimarad, mivel nincs `manual_label`.

---

## Parancssoros futtatás

A CSV-alapú teljes feldolgozási folyamat a projekt gyökérmappájából indítható:

```powershell
python src/main.py
```

A `main.py` alapértelmezetten a kézzel címkézett teszthalmazzal fut.

A parancssoros futtatás létrehozza:

- az Excel-eredményfájlt;
- a modellkiértékelési eredményeket;
- a grafikonokat;
- a szöveges riportot.

---

## Streamlit felület indítása

A grafikus felületet **nem** hagyományos Python-szkriptként, hanem a Streamlit futtatóparancsával kell indítani:

```powershell
streamlit run src/ui/streamlit_app.py
```

Alternatív indítás:

```powershell
python -m streamlit run src/ui/streamlit_app.py
```

A következő indítás nem megfelelő:

```powershell
python src/ui/streamlit_app.py
```

mert ilyen futtatásnál a Streamlit `ScriptRunContext` és `session_state` környezete nem jön létre.

A böngészőben alapértelmezés szerint az alábbi cím nyílik meg:

```text
http://localhost:8501
```

---

## Streamlit adatforrások

### CSV tesztadatok

A CSV mód a kézzel címkézett teszthalmazt elemzi.

Ebben a módban elérhető:

- Accuracy;
- Precision;
- Recall;
- F1-score;
- confusion matrix;
- hibás predikciók listája;
- alacsony konfidenciájú esetek listája.

### Facebook API

Facebook módban a felhasználó megadhatja az elemzendő legutóbbi Facebook-posztok számát.

A felület jelenlegi beállítása:

```text
minimum: 1
maximum: 50
alapértelmezett: 10
```

A rendszer minden kiválasztott poszthoz lekéri:

- a főkommenteket;
- a kommentekre adott válaszokat.

A válaszkommentek ugyanúgy az eredeti poszt szövegéhez viszonyítva kerülnek sentiment elemzésre.

Facebook módban nincs automatikus modellkiértékelés, mert az API-adatokhoz nem tartozik kézi referencia-címke.

---

## Bemeneti fájlok

A kézzel címkézett adatok fő fájljai:

```text
data/validation/train_comments.csv
data/validation/train_post_context.csv

data/validation/validation_comments.csv
data/validation/validation_post_context.csv

data/validation/test_comments.csv
data/validation/test_post_context.csv
```

A `manual_label` mező a referencia-sentimentcímkét tartalmazza.

Támogatott értékek:

```text
positive
negative
neutral
```

---

## Kimeneti fájlok

### CSV/test mód

Excel:

```text
data/processed/sentiment_analysis_results.xlsx
```

Grafikonok:

```text
outputs/charts/
```

Modellkiértékelés:

```text
outputs/evaluation/
```

Riportok:

```text
outputs/reports/
```

### Facebook mód

Excel:

```text
data/processed/facebook_sentiment_analysis_results.xlsx
```

Grafikonok:

```text
outputs/charts/facebook/
```

Riportok:

```text
outputs/reports/facebook/
```

Facebook módban nem készül objektív modellkiértékelés.

---

## Excel-eredményfájl

A munkafüzet fő lapjai:

```text
full_dataset
post_statistics
overall_statistics
context_analysis
```

A `full_dataset` tartalmazza többek között a nyers és végleges sentimenteredményeket, a modellkonfidenciát és azt, hogy a threshold módosította-e a predikciót.

---

## Modellkiértékelési kimenetek

Címkézett tesztadatok esetén a kiértékelési modul többek között az alábbi fájlokat hozhatja létre:

```text
model_metrics.csv
confusion_matrix.csv
misclassified_comments.csv
low_confidence_comments.csv
evaluation_summary.txt
```

A `misclassified_comments.csv` a kézi címkétől eltérő modellpredikciókat tartalmazza.

A `low_confidence_comments.csv` a beállított confidence threshold alatti esetek azonosítására szolgál.

---

## Grafikonok

A rendszer főbb grafikonjai:

```text
overall_sentiment_distribution.png
post_sentiment_distribution.png
average_confidence_by_post.png
context_alignment_distribution.png
```

Címkézett teszthalmaz esetén ezen felül:

```text
confusion_matrix.png
classification_metrics.png
```

Facebook API módban a kiértékelési grafikonok nem készülnek el.

---

## Szöveges riport

A riport többek között összegzi:

- a feldolgozott posztok és hozzászólások mennyiségét;
- a sentimentmegoszlást;
- a domináns sentimentet;
- az átlagos modellbizonyosságot;
- a legpozitívabb és legnegatívabb posztot;
- a kontextuselemzés főbb eredményeit.

---

## Modellkiértékelési mérőszámok

A fő mérőszámok:

- **Accuracy:** az összes komment közül a helyesen osztályozott esetek aránya;
- **Precision:** az adott kategóriába sorolt kommentek közül a ténylegesen oda tartozók aránya;
- **Recall:** az adott kategóriába ténylegesen tartozó kommentek közül a modell által helyesen megtalált esetek aránya;
- **F1-score:** a Precision és Recall harmonikus átlaga;
- **Support:** az adott kategóriába tartozó kézzel címkézett kommentek száma.

A confusion matrix sorai a kézi címkéket, oszlopai a modell predikcióit jelentik.

---

## Hibakezelés

A Streamlit felület és a feldolgozási pipeline többek között kezeli:

- hiányzó bemeneti fájlokat;
- üres CSV-fájlokat;
- hibás CSV-szerkezetet;
- karakterkódolási problémákat;
- megnyitott vagy nem írható kimeneti fájlokat;
- hiányzó kötelező oszlopokat;
- hiányzó modellfájlokat;
- modellbetöltési és PyTorch-hibákat;
- fájl- és mappakezelési problémákat;
- Facebook API-kapcsolati hibákat;
- érvénytelen vagy lejárt access tokent;
- Facebook API jogosultsági problémákat;
- üres API-válaszokat.

A részletes technikai hibaüzenetek a Streamlit felületen külön lenyitható panelen jelennek meg.

---

## Biztonsági és verziókezelési megjegyzések

A következő adatok és nagy bináris állományok nem kerülhetnek publikus repository-ba:

```text
.env
FACEBOOK_ACCESS_TOKEN
model.safetensors
training_args.bin
checkpoint könyvtárak
```

A nagy modellállományok külön OneDrive/SharePoint tárhelyről tölthetők le.

A `.gitignore` feladata többek között a helyi környezeti változók, a nagy modell bináris fájlok és a tréning checkpointok kizárása.

---

## Korlátok

A rendszer szakdolgozati prototípus, ezért több korláttal rendelkezik:

- kizárólag olyan Facebook-oldal adatainak lekérésére készült, amelyhez a szükséges API-hozzáférés szabályosan rendelkezésre áll;
- nem általános közösségimédia-monitoring platform;
- a Facebook Graph API által ténylegesen hozzáférhető adatok köre függ a token jogosultságaitól és az API szabályaitól;
- a rendszer nem elemez automatikusan képi vagy videós tartalmat;
- a sentimentmodell nem külön iróniafelismerő rendszer;
- a rövid, többértelmű, ironikus vagy erősen domainfüggő kommentek továbbra is nehéz esetek lehetnek;
- Facebook API módban nincs automatikus ground-truth címke, ezért az ott kapott predikciókból nem számítható objektív Accuracy vagy F1-score;
- a baseline és a finomhangolt context-aware modell közötti különbség nem izolálja külön a finomhangolás és a kontextus hatását.

---

## Fejlesztési napló

A részletes fejlesztési folyamat, az iterációk, döntések, teszteredmények és módosítások a következő fájlban találhatók:

```text
docs/development_log.md
```

---

## Fejlesztési szakasz lezárása

A prototípus fő fejlesztési céljai teljesültek.

A végleges rendszer képes a következő folyamat végrehajtására:

```text
Facebook API / CSV
        ↓
adatok normalizálása
        ↓
magyar szöveg-előfeldolgozás
        ↓
poszt + komment context-aware sentiment elemzés
        ↓
0.60 confidence threshold
        ↓
pozitív / negatív / semleges eredmény
        ↓
statisztikai összesítés
        ↓
kontextuselemzés
        ↓
Excel + grafikonok + riport
        ↓
Streamlit felület
```

A további munka elsődlegesen nem új fő funkciók fejlesztését, hanem a rendszer végső stabilitásellenőrzését, dokumentálását, szakdolgozati bemutatását és az esetleges jövőbeli továbbfejlesztési lehetőségek meghatározását jelenti.


# „Social media” hangulatelemző szoftver

## Saját adatok

- **Név:** Molnár Bálint Ottó
- **Neptun-kód:** VP35W1
- **Szak:** Mérnökinformatikus BSc
- **Intézmény:** Széchenyi István Egyetem
- **Készítés éve:** 2026

---

## Projektleírás

Ez a repository egy Python-alapú szoftverprototípust tartalmaz, amely magyar nyelvű közösségimédia-kommentek automatikus hangulatelemzésére készült.

A rendszer jelenlegi változata CSV-alapú validációs adatokkal működik. A kommentek, a posztok szövege, a képi kontextus manuális szöveges leírása és a videós leirat előfeldolgozásra kerül, majd egy huBERT-alapú magyar sentimentmodell pozitív, negatív vagy semleges kategóriába sorolja azokat.

A program az eredményeket statisztikailag összesíti, szabályalapú kontextuselemzést végez, grafikonokat és szöveges riportot készít, valamint Streamlit-alapú grafikus felületen jeleníti meg a főbb eredményeket.

A Facebook Graph API integrációja egy későbbi fejlesztési iteráció része.

---

## A megoldandó probléma

Egy Facebook-bejegyzéshez rövid idő alatt nagy mennyiségű hozzászólás érkezhet. Ezek kézi feldolgozása időigényes, nehezen ismételhető és sok esetben szubjektív.

A rendszer célja, hogy a bejegyzésekhez tartozó szöveges visszajelzéseket automatikusan feldolgozza, meghatározza azok hangulati kategóriáját, majd összesített képet adjon a poszt fogadtatásáról.

A rendszer különösen a magyar nyelvű, informális közösségimédia-szövegek sajátosságaira fókuszál, például:

- rövid kommentek,
- elírások,
- szleng,
- emojik,
- irónia,
- vegyes érzelmi tartalom,
- kontextusfüggő megfogalmazások.

---

## A rendszer jelenlegi célja

A jelenlegi prototípus képes:

- CSV-formátumú kommentadatok beolvasására,
- posztkontextus-adatok kezelésére,
- kommentek és posztok összekapcsolására,
- szöveg-előfeldolgozásra,
- magyar nyelvű sentiment elemzésre,
- statisztikai összesítésre,
- szabályalapú kontextuselemzésre,
- Excel-fájl exportálására,
- grafikonok készítésére,
- szöveges riport létrehozására,
- Streamlit-alapú megjelenítésre,
- az eredmények letöltésére.

---

## Fejlesztési környezet beállítása

A projekt futtatásához Python 3.11 használata javasolt.

### 1. A projekt mappájának megnyitása

```powershell
cd "C:\Users\USER\Desktop\projektek_fejlesztes\diplomamunka\Szakdolgozat_Moln-r-B-lint"
````

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

## Alkalmazott technológiák

A projekt főbb technológiái:

* **Python 3.11**
* **pandas**
* **Matplotlib**
* **openpyxl**
* **Hugging Face Transformers**
* **PyTorch**
* **huBERT-alapú magyar sentimentmodell**
* **Streamlit**
* **Git és GitHub**
* **python-dotenv**
* **scikit-learn** – a későbbi validációs és modellkiértékelési szakaszhoz

---

## Projektstruktúra

```text
Szakdolgozat_Moln-r-B-lint/
├── data/
│   ├── processed/
│   ├── raw/
│   └── validation/
│       ├── validacios_teszthalmaz.csv
│       └── post_context.csv
├── docs/
│   └── development_log.md
├── outputs/
│   ├── charts/
│   ├── exports/
│   └── reports/
├── src/
│   ├── analytics/
│   ├── context_analysis/
│   ├── data_input/
│   ├── data_model/
│   ├── pipeline/
│   ├── preprocessing/
│   ├── reporting/
│   ├── sentiment/
│   ├── ui/
│   ├── visualization/
│   └── main.py
├── tests/
├── tools/
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

* validációs kommentadatok beolvasása,
* posztkontextus-adatok beolvasása,
* kommentek és posztok összekapcsolása.

### Szöveg-előfeldolgozás

```text
src/preprocessing/text_preprocessor.py
```

Feladata:

* szövegek tisztítása,
* URL-ek kezelése,
* fölösleges szóközök és sortörések eltávolítása,
* emojik szöveges tokenné alakítása,
* kommentek, posztok, képleírások és videós leiratok előkészítése.

### Sentiment elemzés

```text
src/sentiment/hubert_sentiment_analyzer.py
```

Feladata:

* a huBERT-alapú modell betöltése,
* pozitív, negatív és semleges címkék meghatározása,
* konfidenciaértékek előállítása,
* több szöveges mező együttes elemzése.

### Statisztikai összesítés

```text
src/analytics/sentiment_statistics.py
```

Feladata:

* kommentek darabszámának meghatározása,
* pozitív, negatív és semleges arányok kiszámítása,
* domináns sentiment meghatározása,
* átlagos modellbizonyosság számítása,
* több munkalapos Excel-fájl létrehozása.

### Kontextuselemzés

```text
src/context_analysis/context_analyzer.py
```

Feladata:

* a poszt sentimentjének és a kommentek domináns hangulatának összevetése,
* reakciótípus meghatározása,
* kontextusilleszkedés meghatározása,
* rövid szöveges értelmezés készítése.

A modul szabályalapú, nem végez teljes körű álláspont-felismerést.

### Vizualizáció

```text
src/visualization/sentiment_visualizer.py
```

Feladata:

* teljes sentimenteloszlás ábrázolása,
* posztonkénti sentimentarányok megjelenítése,
* átlagos modellbizonyosság ábrázolása,
* kontextusilleszkedési eredmények megjelenítése.

### Riportkészítés

```text
src/reporting/summary_report.py
```

Feladata:

* összesített szöveges riport készítése,
* legpozitívabb és legnegatívabb poszt meghatározása,
* domináns sentiment és modellbizonyosság összegzése,
* posztonkénti kontextuális értelmezések megjelenítése.

### Közös feldolgozási pipeline

```text
src/pipeline/analysis_pipeline.py
```

Feladata a teljes feldolgozási folyamat közös kezelése.

A modult használja:

* a parancssoros `main.py`,
* a Streamlit-alapú felület.

Ez megakadályozza a feldolgozási logika duplikálását.

### Streamlit felület

```text
src/ui/streamlit_app.py
```

Feladata:

* az elemzés elindítása,
* bemeneti fájlok ellenőrzése,
* főbb statisztikák megjelenítése,
* grafikonok és riport megjelenítése,
* Excel- és TXT-fájl letöltése,
* korábbi eredmények törlése,
* felhasználóbarát hibakezelés.

---

## A rendszer működési folyamata

```text
CSV-adatok beolvasása
→ posztkontextusok beolvasása
→ kommentek és posztok összekapcsolása
→ szöveg-előfeldolgozás
→ huBERT sentiment elemzés
→ posztonkénti statisztikák
→ teljes adathalmaz összesítése
→ kontextuselemzés
→ Excel-export
→ grafikonok létrehozása
→ szöveges riport készítése
→ eredmények megjelenítése a Streamlit felületen
```

---

## Parancssoros futtatás

A teljes feldolgozási folyamat a projekt gyökérmappájából indítható:

```powershell
python src/main.py
```

A parancssoros futtatás létrehozza:

* az Excel-eredményfájlt,
* a grafikonokat,
* a szöveges riportot.

---

## Streamlit felület indítása

A grafikus felület indítása:

```powershell
streamlit run src/ui/streamlit_app.py
```

A böngészőben várhatóan az alábbi cím nyílik meg:

```text
http://localhost:8501
```

A felületen az „Elemzés indítása” gomb elindítja a teljes feldolgozási pipeline-t.

Az első futás hosszabb ideig tarthat, mert a huBERT-modell és a PyTorch környezet inicializálása is megtörténik. A modell a Streamlit `cache_resource` funkciójával gyorsítótárazásra kerül, de az egyes szövegek elemzése minden új futtatáskor ismét végrehajtódik.

---

## Streamlit felület funkciói

A felület megjeleníti:

* a feldolgozott posztok számát,
* a feldolgozott kommentek számát,
* a domináns sentimentet,
* az átlagos modellbizonyosságot,
* az összesített sentimentmegoszlást,
* a posztonkénti statisztikákat,
* a kontextuselemzési eredményeket,
* a grafikonokat,
* a szöveges riportot,
* a részletes kommentenkénti eredményeket.

Az eredmények külön füleken jelennek meg.

A felület lehetőséget biztosít:

* az Excel-fájl letöltésére,
* a szöveges riport letöltésére,
* a korábbi elemzési eredmény törlésére,
* új elemzés indítására.

---

## Bemeneti fájlok

### Validációs kommentadatok

```text
data/validation/validacios_teszthalmaz.csv
```

A fájl a kommentek szövegét, azonosítóit és kézi sentiment címkéit tartalmazza.

### Posztkontextus-adatok

```text
data/validation/post_context.csv
```

A fájl tartalmazhatja:

* a poszt szövegét,
* a poszt típusát,
* a kép manuális szöveges leírását,
* a videós leiratot,
* további megjegyzéseket.

---

## Kimeneti fájlok

### Excel-eredményfájl

```text
data/processed/sentiment_analysis_results.xlsx
```

A munkafüzet fő lapjai:

```text
full_dataset
post_statistics
overall_statistics
context_analysis
```

### Grafikonok

```text
outputs/charts/
```

Létrejövő főbb fájlok:

```text
overall_sentiment_distribution.png
post_sentiment_distribution.png
average_confidence_by_post.png
context_alignment_distribution.png
```

### Szöveges riport

```text
outputs/reports/sentiment_summary.txt
```

A riport tartalmazza:

* a feldolgozott adatok mennyiségét,
* a sentimentmegoszlást,
* a domináns sentimentet,
* a legpozitívabb és legnegatívabb posztot,
* az átlagos modellbizonyosságot,
* a kontextuselemzés főbb eredményeit.

---

## Hibakezelés

A Streamlit felület külön kezeli többek között:

* hiányzó bemeneti fájlokat,
* üres CSV-fájlokat,
* hibás CSV-szerkezetet,
* karakterkódolási problémákat,
* megnyitott vagy nem írható Excel-fájlt,
* hiányzó kötelező oszlopokat,
* modellbetöltési és PyTorch-hibákat,
* fájl- és mappakezelési problémákat.

A részletes technikai hibaüzenetek külön lenyitható panelen jelennek meg.


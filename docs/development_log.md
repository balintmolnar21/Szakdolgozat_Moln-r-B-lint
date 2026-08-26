# Fejlesztési napló

## 0. iteráció – Kezdeti projektstruktúra kialakítása

### Cél

A 0. iteráció célja a szakdolgozati prototípus fejlesztési alapjainak kialakítása volt. Ebben a szakaszban még nem konkrét funkcionális modulok implementálása történt, hanem a repository olyan alapstruktúrájának létrehozása, amely támogatja a későbbi iteratív fejlesztést, a forráskód átlátható kezelését, valamint a szakdolgozatban bemutatható fejlesztési folyamat dokumentálását.

A fejlesztés ebben az iterációban szándékosan minimális projektvázzal indult. Ennek oka, hogy az egyes forráskódmodulok csak akkor kerüljenek létrehozásra, amikor az adott funkció fejlesztése ténylegesen elkezdődik. Ez jobban szemlélteti az iteratív fejlesztési modell gyakorlati alkalmazását.

### Létrehozott projektstruktúra

A repository jelenlegi struktúrája az alábbi főbb elemekből áll:

```text
Szakdolgozat_Moln-r-B-lint/
│
├── data/
│   ├── processed/
│   ├── raw/
│   └── validation/
│
├── docs/
│   ├── diagrams/
│   ├── literature/
│   ├── planning/
│   ├── specification/
│   └── development_log.md
│
├── outputs/
│   ├── charts/
│   ├── exports/
│   └── reports/
│
├── src/
│   └── main.py
│
├── tests/
│   └── .gitkeep
│
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```
## 1. iteráció – CSV-alapú validációs adathalmaz beolvasása

### Cél

Az 1. iteráció célja az első tényleges adatbeolvasási funkció elkészítése volt. A rendszer ebben a szakaszban még nem a Facebook Graph API-ból dolgozik, hanem egy lokális CSV-fájlban tárolt validációs teszthalmazt olvas be.

Ez a megközelítés lehetővé teszi, hogy az adatfeldolgozási folyamat első lépése külső API-hozzáféréstől függetlenül legyen tesztelhető. A fejlesztés során így először a belső adatformátum és az adatbeolvasási logika került kialakításra, amelyre a későbbi modulok is épülhetnek.

### Megvalósított elemek

Az iteráció során létrejött a `src/data_input/` modul, amely a CSV-alapú adatbeolvasásért felel. A modul részeként elkészült a `csv_loader.py` fájl, amely képes a validációs teszthalmaz beolvasására, az oszlopnevek ellenőrzésére, valamint a bemeneti adatok egységes belső formátumra alakítására.

A fejlesztés során az alábbi elemek valósultak meg:

- általános CSV-beolvasó függvény kialakítása,
- a validációs teszthalmazhoz tartozó oszlopnév-leképezés megadása,
- kötelező mezők meglétének ellenőrzése,
- oszlopnevek egységesítése,
- üres kommenttartalmak kiszűrése,
- a kommentek szöveges formátumra alakítása,
- a beolvasott adathalmaz ellenőrző kiíratása a `main.py` fájlon keresztül.

### Belső adatformátum kialakítása

A validációs CSV eredeti oszlopnevei magyar nyelvűek, ezért a rendszer a beolvasás után egységes belső oszlopneveket használ. Ez azért fontos, mert a későbbi feldolgozó moduloknak nem kell ismerniük az eredeti CSV-fájl szerkezetét.

Az alkalmazott oszlopnév-leképezés:

```text
Poszt ID           → post_id
Poszt típusa       → post_type
Poszt link         → post_link
Komment ID         → comment_id
Komment tartalma   → comment_text
Kézi címke         → manual_label
Modell címke       → model_label
Megjegyzés         → note
```

## 2. iteráció – Belső adatmodell bővítése posztkontextussal

### Cél

A 2. iteráció célja az volt, hogy a rendszer ne kizárólag kommentenként kezelje az adatokat, hanem a kommenteket össze tudja kapcsolni a hozzájuk tartozó Facebook-poszt szöveges kontextusával is.

Az előző iterációban elkészült a validációs kommenthalmaz CSV-alapú beolvasása. Ez azonban elsősorban a kommentekre és azok kézi címkéire koncentrált. A szakdolgozati rendszer működése szempontjából viszont fontos, hogy a kommentek mellett a poszt saját szövege, képes poszt esetén a kép manuálisan megadott szöveges leírása, videós poszt esetén pedig a videó szöveges leirata is kezelhető legyen.

Ebben az iterációban ezért létrejött egy bővített belső adatmodell, valamint egy külön posztkontextus-adathalmaz, amely a validációs teszthalmazban szereplő `P1`–`P5` posztazonosítókhoz kapcsolódik.

### Megvalósított elemek

Az iteráció során létrejött a `src/data_model/` modul, amely a rendszer belső adatszerkezetének központi definícióit tartalmazza. Ebben kerültek rögzítésre azok az oszlopnevek és kötelező mezők, amelyeket a rendszer későbbi moduljai egységesen használni fognak.

Létrejött továbbá a `data/validation/post_context.csv` fájl, amely az öt vizsgált Facebook-poszthoz tartozó posztszintű szöveges adatokat tartalmazza.

A posztkontextus-adathalmaz mezői:

```text
post_id
post_type
post_text
image_context_text
video_context_text
note
```
A különböző változók jelentése:
```text
post_id              → a poszt azonosítója, például P1, P2, P3
post_type            → a poszt típusa, például image vagy video
post_text            → a Facebook-poszt eredeti szövege
image_context_text   → képes poszt esetén a kép manuális szöveges leírása
video_context_text   → videós poszt esetén a videó manuális leirata vagy felirata
note                 → technikai vagy adatkezelési megjegyzés
```

## 3. iteráció – Szöveg-előfeldolgozó modul és emoji-tokenizálás kialakítása

### Cél

A 3. fejlesztési iteráció célja a rendszer szöveg-előfeldolgozó rétegének kialakítása volt. Az előző iteráció végére a program már képes volt a validációs kommenthalmaz és a posztkontextus-adathalmaz beolvasására, majd ezek `post_id` alapján történő összekapcsolására. Ennek eredményeként minden kommenthez elérhetővé vált a hozzá tartozó poszt szövege, képes poszt esetén a kép manuális szöveges leírása, videós poszt esetén pedig a videó manuális leirata.

Az így létrejött adathalmaz azonban még nyers szöveges mezőket tartalmazott. A közösségi médiából származó szövegek gyakran tartalmaznak emojikat, URL-eket, többszörös szóközöket, sortöréseket, rövid és informális megfogalmazásokat, valamint olyan karaktereket, amelyek közvetlenül nem minden esetben ideálisak modellalapú feldolgozásra. Emiatt szükségessé vált egy külön előfeldolgozó modul létrehozása, amely a nyers szövegekből egységesebb, a későbbi hangulatelemzés számára jobban kezelhető bemenetet állít elő.

Az iteráció fontos tervezési célja volt, hogy az előfeldolgozás ne írja felül az eredeti adatokat. Ehelyett a rendszer új, `cleaned_` előtaggal ellátott oszlopokat hoz létre. Ez lehetővé teszi, hogy az eredeti és a tisztított szövegek egymás mellett megmaradjanak, így a fejlesztés és validáció során pontosan ellenőrizhető, milyen változtatásokat végzett az előfeldolgozás.

### Megvalósított fájlstruktúra

Az iteráció során a projektben létrejött a szöveg-előfeldolgozásért felelős új modulstruktúra:

```text
src/preprocessing/
├── __init__.py
├── emoji_library.py
└── text_preprocessor.py
```

## 4. iteráció – huBERT-alapú sentiment modell integrálása

### Cél

A 4. fejlesztési iteráció célja a magyar nyelvű, huBERT-alapú sentiment elemző modell integrálása volt a rendszerbe. Az előző iterációk során elkészült az adatok beolvasása, a posztkontextus kezelése, valamint a szöveges mezők előfeldolgozása. A rendszer így már rendelkezett olyan tisztított szöveges oszlopokkal, amelyek alkalmasak voltak a modellalapú hangulatelemzés bemeneteként történő felhasználásra.

Ebben az iterációban a cél az volt, hogy a rendszer képes legyen egy előre betanított magyar nyelvű Transformer-alapú modellt betölteni, a megtisztított kommenteket elemezni, majd minden kommenthez automatikus hangulatcímkét és konfidenciaértéket rendelni.

A fejlesztés során a hangsúly első lépésben a kommentek hangulatelemzésén volt, ugyanakkor a sentiment elemző modult általános szövegelemző komponensként alakítottuk ki. Ez lehetővé teszi, hogy később ugyanaz a modul ne csak kommentekre, hanem posztszövegre, képi kontextus manuális leírására és videós leiratra is alkalmazható legyen.

### Megvalósított fájlstruktúra

Az iteráció során létrejött a sentiment elemzésért felelős új modul:

```text
src/sentiment/
├── __init__.py
└── hubert_sentiment_analyzer.py
```

## 5. iteráció – Posztkontextus és kommentek együttes sentiment elemzése

### Cél

Az ötödik fejlesztési iteráció célja az volt, hogy a rendszer a kommentek mellett a hozzájuk tartozó posztkontextust is sentiment elemzésnek vesse alá. A fejlesztés során a meglévő huBERT-alapú sentiment elemző modul kibővítésre került, hogy több szövegoszlopon is képes legyen egymás után elemzést végezni.

A rendszer ebben az iterációban már az alábbi szöveges mezőket elemzi:

```text
cleaned_comment_text
cleaned_post_text
cleaned_image_context_text
cleaned_video_context_text
```

Ez lehetővé teszi, hogy a kommentek hangulata mellett a poszt szövege, a képi kontextus szöveges leírása és a videós leirat is külön sentiment címkét kapjon.

### Érintett fájlok

Az iteráció során az alábbi fájlok módosultak:

```text
src/data_model/schema.py
src/sentiment/hubert_sentiment_analyzer.py
src/main.py
README.md
```

Új külön pipeline-fájl nem készült. A feldolgozási sorrendet továbbra is a `main.py` kezeli, míg a sentiment elemzés modelllogikája a `hubert_sentiment_analyzer.py` fájlban maradt.

### Adatséma bővítése

A `schema.py` fájlban új oszlopok kerültek bevezetésre a posztkontextus sentiment eredményeinek tárolására:

```text
post_sentiment_label
post_sentiment_confidence
post_original_model_label

image_context_sentiment_label
image_context_sentiment_confidence
image_context_original_model_label

video_context_sentiment_label
video_context_sentiment_confidence
video_context_original_model_label
```

Ezek az oszlopok külön tárolják a poszt szövegének, a képi kontextus leírásának és a videós leiratnak a modell által adott címkéjét, konfidenciaértékét és eredeti modellcímkéjét.

### Sentiment elemző modul bővítése

A `hubert_sentiment_analyzer.py` fájlban a `HuBERTSentimentAnalyzer` osztály egy új metódussal bővült:

```python
analyze_multiple_dataframe_columns(...)
```

Ez a metódus konfigurációs lista alapján több DataFrame-oszlopon futtatja le a sentiment elemzést. A megoldás a korábban elkészült `analyze_dataframe_column()` metódust használja újra, így a modellfuttatási logika nem ismétlődik.

A lokális tesztblokk is frissítésre került, így már nemcsak egyedi mintaszövegeken, hanem többoszlopos DataFrame-példán is ellenőrizhető a sentiment elemző működése.

### A main.py módosítása

A `main.py` fájlban létrejött egy `sentiment_analysis_configs` konfigurációs lista, amely meghatározza, hogy mely szövegoszlopokat kell elemezni, és az eredményeket mely oszlopokba kell menteni.

A feldolgozási folyamat az iteráció után:

```text
validációs kommentadatok beolvasása
→ posztkontextus beolvasása
→ kommentek és posztkontextus összekapcsolása
→ szöveg-előfeldolgozás
→ huBERT sentiment modell betöltése
→ kommentek sentiment elemzése
→ posztszöveg sentiment elemzése
→ képi kontextus sentiment elemzése
→ videós leirat sentiment elemzése
→ egységes Excel-adatbázis exportálása
```

A fő kimeneti fájl:

```text
data/processed/full_sentiment_analysis.xlsx
```

### Egységes sentiment adatbázis

Az iteráció eredményeként létrejön egy egységes Excel-alapú adathalmaz, amelyben egy sor továbbra is egy kommentet jelent, de minden komment mellett szerepel a hozzá tartozó poszt szöveges kontextusa és annak sentiment eredménye is.

Az Excel többek között tartalmazza:

```text
post_id
post_type
post_text
cleaned_post_text
post_sentiment_label

image_context_text
cleaned_image_context_text
image_context_sentiment_label

video_context_text
cleaned_video_context_text
video_context_sentiment_label

comment_id
comment_text
cleaned_comment_text
manual_label
model_label
confidence
original_model_label
```

Ez az egységes adatszerkezet megalapozza a későbbi statisztikai összesítést, validációt és kontextusalapú értelmezést.

### Képi és videós kontextus kezelése

A képes posztok esetében a rendszer jelenleg nem magát a képfájlt elemzi, hanem a `post_context.csv` fájlban megadott szöveges képleírást. A későbbiekben ez a képleírás automatikus képelemző modell kimenetével is kiváltható lesz.

Videós posztok esetében a rendszer a videóhoz tartozó szöveges leiratot vagy manuálisan megadott összefoglalót elemzi. Ez illeszkedik a prototípus céljához, mert a rendszer fókusza továbbra is a magyar nyelvű szöveges tartalmak sentiment elemzésén van.

### Fontos tervezési döntés

A kommentek `model_label` értéke nem kerül átírásra a poszt hangulata alapján. A rendszer külön kezeli:

```text
model_label
→ a komment önálló sentiment címkéje

post_sentiment_label
→ a poszt szövegének sentiment címkéje

image_context_sentiment_label
→ a képi kontextus szöveges leírásának sentiment címkéje

video_context_sentiment_label
→ a videós leirat sentiment címkéje
```

Ez azért fontos, mert a kommenthangulat és a poszthangulat külön elemzési szintet képvisel. A kettő összevetése majd egy későbbi kontextuselemző modul feladata lesz.

### README bővítése

A `README.md` fájl kiegészült a virtuális környezet létrehozásának, aktiválásának, a `requirements.txt` alapján történő függőségtelepítésnek és a program futtatásának parancsaival. Ez megkönnyíti a projekt reprodukálását és a konzulensi ellenőrzést.

### Eredmény

Az ötödik iteráció eredményeként a rendszer képes a kommentek, a poszt szövege, a képi kontextus leírása és a videós leirat sentiment elemzésére, majd ezek eredményét egy közös Excel-fájlban tárolja.

A létrejött fő kimenet:

```text
data/processed/full_sentiment_analysis.xlsx
```

## 6. iteráció – Statisztikai összesítés és több munkalapos Excel-kimenet

### Cél

A hatodik fejlesztési iteráció célja az volt, hogy a korábban elkészült részletes sentiment adathalmazból automatikusan előálljanak a posztonkénti és a teljes adathalmazra vonatkozó statisztikai összesítések.

A fejlesztés eredményeként a rendszer már nemcsak kommentenként tárolja a modell által adott sentiment címkéket és konfidenciaértékeket, hanem képes kiszámítani:

```text
a pozitív kommentek számát,
a negatív kommentek számát,
a semleges kommentek számát,
a sentiment kategóriák százalékos arányát,
a domináns kommenthangulatot,
az átlagos modellkonfidenciát,
a posztok és kommentek teljes számát.
```

Az eredmények egyetlen Excel-munkafüzetbe kerülnek, három külön munkalapon.

### Érintett fájlok

A fejlesztés során az alábbi fájlok jöttek létre vagy módosultak:

```text
src/analytics/__init__.py
src/analytics/sentiment_statistics.py
src/main.py
```

A statisztikai logika külön `analytics` modulba került. Ez azért indokolt, mert ebben a fejlesztési fázisban már nem történik új modellpredikció, hanem a korábban létrehozott sentiment eredmények feldolgozása és összesítése valósul meg.

A `main.py` továbbra is a teljes feldolgozási sorrendet vezérli.

### Az analytics modul kialakítása

A statisztikai műveletekhez létrejött az alábbi modul:

```text
src/analytics/sentiment_statistics.py
```

A modul fő feladatai:

```text
a szükséges oszlopok ellenőrzése,
a sentiment címkék előkészítése,
a posztonkénti statisztikák kiszámítása,
a teljes adathalmaz összesítése,
a domináns sentiment meghatározása,
a három munkalapos Excel-fájl exportálása.
```

A modul a pandas könyvtár DataFrame-műveleteire épül, az Excel-fájl létrehozásához pedig az `openpyxl` motort használja.

### Adatellenőrzés és előkészítés

A `validate_required_columns()` függvény ellenőrzi, hogy a feldolgozandó DataFrame tartalmazza-e a statisztikai számításokhoz szükséges mezőket.

A kötelező oszlopok:

```text
post_id
model_label
confidence
```

Ha valamelyik mező hiányzik, a rendszer jól értelmezhető hibaüzenettel leáll. Ez megelőzi, hogy a statisztikai számítás hiányos vagy hibás adatokon fusson le.

A `prepare_sentiment_dataframe()` függvény előkészíti az adatokat az összesítéshez. Ennek során:

```text
másolat készül az eredeti DataFrame-ről,
a model_label értékei kisbetűs és whitespace-mentes formára kerülnek,
a confidence oszlop numerikus típussá alakul,
ellenőrzésre kerülnek a hiányzó címkék,
ellenőrzésre kerülnek az ismeretlen sentiment kategóriák.
```

A rendszer az alábbi normalizált sentiment címkéket fogadja el:

```text
positive
negative
neutral
```

### Domináns sentiment meghatározása

A `determine_dominant_sentiment()` függvény megállapítja, hogy egy adott poszt vagy a teljes adathalmaz esetében melyik sentiment kategória fordul elő a legnagyobb számban.

Például:

```text
positive: 17
negative: 6
neutral: 5
```

esetén az eredmény:

```text
positive
```

Ha két vagy több kategória azonos legmagasabb darabszámmal rendelkezik, az eredmény:

```text
mixed
```

Ha nincs feldolgozható adat, az eredmény:

```text
no_data
```

Ez a megoldás elkerüli, hogy a rendszer döntetlen esetén önkényesen válasszon sentiment címkét.

### Posztonkénti statisztikák

A `calculate_post_statistics()` függvény a teljes sentiment adathalmazt `post_id` alapján csoportosítja.

Minden poszthoz egyetlen statisztikai rekord készül, amely többek között az alábbi adatokat tartalmazza:

```text
post_id
post_type
post_link
comment_count

positive_count
negative_count
neutral_count

positive_ratio
negative_ratio
neutral_ratio

dominant_comment_sentiment
average_comment_confidence
```

A darabszámok a `model_label` oszlop alapján kerülnek meghatározásra.

A százalékos arányok számítása:

```text
kategória darabszáma / összes komment száma × 100
```

Az eredmények két tizedesjegyre kerekítve kerülnek tárolásra.

A posztonkénti statisztikai táblázat a posztkontextushoz tartozó sentiment mezőket is megtartja:

```text
post_sentiment_label
post_sentiment_confidence
image_context_sentiment_label
image_context_sentiment_confidence
video_context_sentiment_label
video_context_sentiment_confidence
```

Ez azért fontos, mert a következő fejlesztési fázis kontextuselemző modulja ezekre az adatokra tud majd építeni.

### Ismétlődő posztkontextus kezelése

A részletes adathalmazban ugyanaz a posztkontextus minden hozzá tartozó komment sorában megismétlődik.

A `get_first_available_value()` függvény ezért egy adott poszt csoportján belül kiválasztja az első elérhető, nem üres értéket például a következő mezőkből:

```text
post_type
post_link
post_sentiment_label
image_context_sentiment_label
video_context_sentiment_label
```

Így a posztonkénti összesítésben minden kontextusadat csak egyszer jelenik meg.

### Teljes adathalmaz statisztikája

A `calculate_overall_statistics()` függvény a teljes kommenthalmazra készít összesítést.

A kimeneti DataFrame egyetlen sort tartalmaz, amelyben szerepel:

```text
post_count
total_comment_count

total_positive_count
total_negative_count
total_neutral_count

total_positive_ratio
total_negative_ratio
total_neutral_ratio

overall_dominant_sentiment
overall_average_confidence
```

A `post_count` az egyedi posztazonosítók száma, míg a `total_comment_count` a teljes feldolgozott kommentmennyiséget jelenti.

Az `overall_average_confidence` a kommentekhez tartozó modellkonfidencia-értékek átlaga.

### Több munkalapos Excel-kimenet

A `export_sentiment_workbook()` függvény egyetlen Excel-munkafüzetbe exportálja a részletes és összesített adatokat.

A létrejövő fájl:

```text
data/processed/sentiment_analysis_results.xlsx
```

A munkafüzet három lapot tartalmaz:

```text
full_dataset
post_statistics
overall_statistics
```

A `full_dataset` munkalap a teljes kommentenkénti sentiment adatbázist tartalmazza.

A `post_statistics` munkalap posztonként egy sort tartalmaz, a kommentek darabszámával, arányaival, domináns hangulatával és a posztkontextus sentiment adataival.

Az `overall_statistics` munkalap a teljes adathalmaz összesített mutatóit tartalmazza egyetlen sorban.

### Excel-formázás

A `format_excel_worksheet()` függvény alapvető formázást végez minden munkalapon.

A formázás részei:

```text
a fejlécsor rögzítése,
az automatikus szűrés bekapcsolása,
az oszlopszélességek automatikus beállítása.
```

A rögzített fejléc megkönnyíti a nagyobb táblázatok áttekintését, az automatikus szűrés pedig lehetővé teszi a munkalapok közvetlen Excelen belüli szűrését.

### A main.py módosítása

A `main.py` új importokkal egészült ki:

```python
from analytics.sentiment_statistics import (
    calculate_post_statistics,
    calculate_overall_statistics,
    export_sentiment_workbook,
)
```

A sentiment elemzés után a program először elkészíti a posztonkénti statisztikát:

```python
post_statistics_df = calculate_post_statistics(
    full_sentiment_df
)
```

Ezután elkészíti a teljes adathalmaz összesítését:

```python
overall_statistics_df = calculate_overall_statistics(
    full_sentiment_df
)
```

Végül létrehozza a három munkalapos Excel-fájlt:

```python
created_output_file = export_sentiment_workbook(
    full_dataset_df=full_sentiment_df,
    post_statistics_df=post_statistics_df,
    overall_statistics_df=overall_statistics_df,
    output_file=output_file,
)
```

A korábbi közvetlen Excel-mentés helyett tehát már egy összetettebb exportfolyamat fut le.

### A teljes feldolgozási folyamat

A hatodik iteráció után a rendszer működési sorrendje:

```text
validációs kommentadatok beolvasása
→ posztkontextus-adatok beolvasása
→ kommentek és posztkontextus összekapcsolása
→ szöveg-előfeldolgozás
→ huBERT sentiment modell betöltése
→ kommentek és kontextusszövegek sentiment elemzése
→ posztonkénti statisztikák számítása
→ teljes adathalmaz statisztikáinak számítása
→ három munkalapos Excel-fájl létrehozása
```

### Kimeneti adatok ellenőrzése

A `main.py` a futtatás végén kiírja:

```text
a kommentek számát,
a posztkontextusok számát,
az összekapcsolt adatsorok számát,
a teljes sentiment rekordok számát,
a posztonkénti statisztikai sorok számát,
a teljes adathalmaz statisztikai sorainak számát,
a létrehozott fájl útvonalát.
```

A terminálban előnézetként megjelenik:

```text
a teljes sentiment adathalmaz első tíz sora,
a posztonkénti statisztikai táblázat,
a teljes adathalmaz összesítő rekordja.
```

Ez lehetővé teszi a feldolgozás gyors ellenőrzését az Excel-fájl megnyitása előtt.

### Eredmény

A hatodik fejlesztési iteráció eredményeként a rendszer képes a részletes komment- és posztkontextus-adatokból automatikusan statisztikai összesítéseket készíteni.

A létrejövő Excel-munkafüzet egyszerre tartalmazza:

```text
a teljes rekord szintű adatbázist,
a posztonkénti statisztikai eredményeket,
a teljes adathalmaz összesített mutatóit.
```

A fejlesztés fő kimeneti fájlja:

```text
data/processed/sentiment_analysis_results.xlsx
```


## 7. iteráció – Kontextuselemző modul kialakítása

### Cél

A hetedik fejlesztési iteráció célja az volt, hogy a rendszer a korábban előállított posztszintű sentiment eredményeket és kommentstatisztikákat összevesse, majd ezek alapján szabályalapú kontextuális értelmezést készítsen.

A korábbi fejlesztési fázisok eredményeként már rendelkezésre álltak az alábbi adatok:

```text
a poszt szövegének sentiment címkéje,
a kommentek domináns sentiment címkéje,
a pozitív kommentek aránya,
a negatív kommentek aránya,
a semleges kommentek aránya.
```

Ezek az adatok külön-külön már alkalmasak voltak a poszt és a kommentszekció általános hangulatának leírására, azonban önmagukban még nem mutatták meg, hogy a kommentek hangulata milyen kapcsolatban áll a poszt hangvételével. A fejlesztési lépés ezért arra irányult, hogy a rendszer ne csak statisztikai adatokat közöljön, hanem rövid, értelmezhető következtetést is készítsen a poszt és a kommentek sentimentje közötti viszonyról.

A kontextuselemző modul szabályalapú működésű. Ez azt jelenti, hogy nem egy új mesterséges intelligencia modell hozza létre az értelmezést, hanem előre meghatározott logikai szabályok alapján történik a poszt és a kommentek hangulatának összehasonlítása. A megoldás előnye, hogy működése átlátható, minden eredményhez egyértelműen megadható, mely szabály vezetett az adott következtetéshez.

A modul például külön kezeli azokat az eseteket, amikor:
```text
a poszt és a kommentek hangulata azonos irányú,
a kommentek domináns hangulata ellentétes a poszt hangulatával,
a kommentek megoszlása vegyes,
a semleges kommentek vannak többségben,
nem áll rendelkezésre elegendő vagy megfelelő adat.
```
A fejlesztés során fontos szempont volt, hogy a rendszer ne vonjon le túlzottan erős vagy bizonytalan következtetéseket. A sentiment elemzés önmagában nem alkalmas annak biztos megállapítására, hogy egy kommentelő egyetért-e a poszt állításával, vagy éppen elutasítja azt. Emiatt a létrehozott szöveges értelmezések óvatos megfogalmazást használnak, például:
- utalhat,
- jelezhet,
- értelmezhető,
- valószínűsíthető.

A fejlesztési iteráció célja tehát nem egy teljes körű álláspont-felismerő rendszer létrehozása volt, hanem egy olyan egyszerű és jól magyarázható kontextuselemző réteg kialakítása, amely a már rendelkezésre álló sentiment eredményeket magasabb szintű, felhasználóbarát információvá alakítja.

A modul kimeneteként minden poszthoz három új érték készül:
A `context_reaction_type` egy rövid kategóriában foglalja össze a reakció jellegét, például támogató, kritikus, vegyes vagy bizonytalan reakcióként.

A `context_alignment` azt jelzi, hogy a poszt és a kommentek hangulata azonos, ellentétes, vegyes vagy nem egyértelmű kapcsolatban áll-e egymással.

A `context_interpretation` pedig egy rövid, ember számára olvasható szöveges magyarázatot tartalmaz, amelyben a rendszer összefoglalja a poszt hangvételét, a kommentek domináns sentimentjét, valamint a pozitív, negatív és semleges kommentek százalékos megoszlását.

A fejlesztés eredményeként a rendszer a korábbi pusztán numerikus és kategóriaalapú kimenetek mellett már egyszerű kontextuális értelmezést is képes előállítani. Ez közvetlenül támogatja a későbbi összegző, vizualizációs és felhasználói felületi fejlesztéseket.


## 8. iteráció – Riportkészítés és eredményvizualizáció

### Cél

A nyolcadik fejlesztési iteráció célja az volt, hogy a rendszer a korábban elkészített sentiment-, statisztikai és kontextuselemzési eredményeket grafikus és szöveges formában is megjelenítse.

A korábbi eredmények alapján már rendelkezésre álltak:

```text
a kommentek sentiment címkéi,
a posztonkénti sentiment arányok,
az összesített statisztikák,
a kontextuselemzés eredményei.
```

### Új modulok

A fejlesztés során két új modul jött létre:

```text
src/visualization/sentiment_visualizer.py
src/reporting/summary_report.py
```

A vizualizációs modul a grafikonok elkészítéséért, a riportkészítő modul pedig a szöveges összefoglaló előállításáért felel.

### Grafikonok készítése

A rendszer négy PNG-formátumú grafikont hoz létre:

```text
overall_sentiment_distribution.png
post_sentiment_distribution.png
average_confidence_by_post.png
context_alignment_distribution.png
```

A grafikonok bemutatják:

```text
a teljes sentimenteloszlást,
a posztonkénti sentimentarányokat,
az átlagos modellbizonyosságot,
a kontextusilleszkedési kategóriák megoszlását.
```

A fájlok mentési helye:

```text
outputs/charts/
```

### Szöveges riport

A rendszer automatikusan létrehoz egy rövid összefoglaló riportot:

```text
outputs/reports/sentiment_summary.txt
```

A riport tartalmazza:

```text
a feldolgozott posztok és kommentek számát,
a teljes sentimentmegoszlást,
a domináns sentimentet,
a legpozitívabb és legnegatívabb fogadtatású posztot,
az átlagos modellbizonyosságot,
a leggyakoribb kontextusilleszkedést,
a posztonkénti kontextuális értelmezéseket.
```

### A main.py módosítása

A `main.py` új függvényhívásokkal bővült:

```python
create_all_sentiment_charts(...)
create_summary_report(...)
```

A teljes feldolgozási folyamat:

```text
adatbeolvasás
→ előfeldolgozás
→ sentiment elemzés
→ statisztikai összesítés
→ kontextuselemzés
→ Excel-export
→ grafikonok készítése
→ szöveges riport készítése
```

### Kimenetek

A rendszer a nyolcadik iteráció után az alábbi fájlokat hozza létre:

```text
data/processed/sentiment_analysis_results.xlsx
outputs/charts/*.png
outputs/reports/sentiment_summary.txt
```


## 9. iteráció – Streamlit felület kialakítása CSV-alapú tesztmóddal

### Cél

A kilencedik fejlesztési iteráció célja egy egyszerű, grafikus Streamlit felület létrehozása volt, amely a meglévő CSV-alapú tesztadatokkal képes elindítani a teljes elemzési folyamatot és megjeleníteni az eredményeket.

### Új fájlok

```text
src/ui/__init__.py
src/ui/streamlit_app.py
src/pipeline/__init__.py
src/pipeline/analysis_pipeline.py
````

A `requirements.txt` fájl kiegészült a `streamlit` csomaggal.

### Közös feldolgozási pipeline

A teljes elemzési folyamat külön pipeline-modulba került:

```text
src/pipeline/analysis_pipeline.py
```

Ez a modul végzi:

```text
adatbeolvasás
→ előfeldolgozás
→ huBERT sentiment elemzés
→ statisztikai összesítés
→ kontextuselemzés
→ Excel-export
→ grafikonok készítése
→ szöveges riport létrehozása
```

A közös pipeline használatával a parancssoros program és a Streamlit felület ugyanazt a feldolgozási logikát használja, így nem keletkezett kódduplikáció.

### Streamlit felület

A grafikus felület az alábbi fájlban készült el:

```text
src/ui/streamlit_app.py
```

A felület lehetővé teszi:

```text
a bemeneti fájlok ellenőrzését,
az elemzés gombbal történő elindítását,
a fő statisztikák megjelenítését,
a posztonkénti eredmények megtekintését,
a kontextuselemzés megjelenítését,
a grafikonok megjelenítését,
a szöveges riport megtekintését,
az Excel- és TXT-fájl letöltését.
```

Az eredmények külön füleken jelennek meg.

### Modell gyorsítótárazása

A huBERT-modell betöltése Streamlit gyorsítótárazással történik:

```python
@st.cache_resource
```

Ez biztosítja, hogy a modell ugyanazon munkameneten belül ne töltődjön be minden elemzésnél újra.

### Munkamenet-kezelés

A pipeline eredményei a Streamlit munkamenet-állapotában kerülnek tárolásra:

```python
st.session_state["analysis_result"]
```

Külön gomb készült a korábbi eredmények törlésére és a felület alapállapotba történő visszaállítására.

### Hibakezelés

A felület külön kezeli többek között:

```text
a hiányzó vagy üres CSV-fájlokat,
a hibás CSV-szerkezetet,
a karakterkódolási problémákat,
a megnyitott vagy nem írható kimeneti fájlokat,
a hiányzó kötelező oszlopokat,
a modellbetöltési és futtatási hibákat.
```

A technikai részletek külön lenyitható panelen jelennek meg.

### Futtatás

A Streamlit felület a projekt gyökérmappájából indítható:

```powershell
streamlit run src/ui/streamlit_app.py
```

### Eredmény

A kilencedik iteráció eredményeként a rendszer már grafikus felületen is használható. A felhasználó egyetlen gombnyomással elindíthatja a teljes elemzést, majd áttekintheti és letöltheti a létrehozott eredményeket.




## 10. iteráció – Modellvalidáció és teljesítménykiértékelés

### Cél

A tizedik fejlesztési iteráció célja a huBERT-alapú sentimentmodell teljesítményének objektív kiértékelése volt. A modell által előállított címkék összehasonlításra kerültek az ember által megadott kézi címkékkel.

### Új modulok

A modellkiértékeléshez az alábbi fájlok készültek:

```text
src/evaluation/__init__.py
src/evaluation/model_evaluator.py
src/evaluation/evaluation_exporter.py
src/evaluation/evaluation_visualizer.py
````

A kiértékelési eredmények számára külön kimeneti mappa került kialakításra:

```text
outputs/evaluation/
```

### Kiértékelési folyamat

A kiértékelés során a rendszer a következő oszlopokat hasonlítja össze:

```text
manual_label
model_label
```

A kézi és modellcímkék egységesítés után pozitív, negatív és semleges kategóriákba kerülnek.

A rendszer kiszámítja:

```text
accuracy
precision
recall
F1-score
support
```

Az eredmények osztályonként, valamint makró- és súlyozott átlagként is előállnak.

### Confusion matrix

A fejlesztés részeként confusion matrix is készül. A mátrix sorai az ember által megadott címkéket, az oszlopai pedig a modell predikcióit jelentik.

A főátlóban találhatók a helyes predikciók, míg a főátlón kívüli értékek a téves osztályozásokat mutatják.

A confusion matrix táblázatos és grafikus formában is elkészül.

### Hibás és alacsony konfidenciájú predikciók

A rendszer külön kigyűjti azokat a kommenteket, amelyeknél a modell címkéje eltér a kézi címkétől.

Külön fájlba kerülnek azok a predikciók is, amelyeknél a modell konfidenciaértéke 0,60 alatti. Ezek az esetek bizonytalanabbnak tekinthetők, ezért részletesebb vizsgálatuk indokolt.

### Létrehozott kimenetek

A kiértékelés során az alábbi fájlok készülnek:

```text
outputs/evaluation/model_metrics.csv
outputs/evaluation/confusion_matrix.csv
outputs/evaluation/misclassified_comments.csv
outputs/evaluation/low_confidence_comments.csv
outputs/evaluation/evaluation_summary.txt
```

A grafikus eredmények:

```text
outputs/charts/confusion_matrix.png
outputs/charts/classification_metrics.png
```

### Pipeline-integráció

A modellkiértékelés bekerült a közös elemzési pipeline-ba. A kiértékelés a sentiment elemzés után automatikusan lefut, majd létrehozza a metrikákat, exportfájlokat és grafikonokat.

A pipeline eredményobjektuma kiegészült a kiértékelési eredményekkel és a létrehozott fájlok elérési útjaival.

### Streamlit megjelenítés

A Streamlit felület új „Modellkiértékelés” füllel egészült ki.

A felület megjeleníti:

```text
az accuracy értékét,
a hibás predikciók számát,
az alacsony konfidenciájú esetek számát,
az osztályonkénti precision, recall és F1-score értékeket,
a confusion matrixot,
a hibás predikciókat,
az alacsony konfidenciájú kommenteket.
```

A főbb mérőszámokhoz és grafikonokhoz rövid magyarázatok is készültek.


## 11. iteráció – Facebook Graph API adatlekérési réteg kialakítása

### Cél

A tizenegyedik fejlesztési iteráció célja a Facebook Graph API-alapú adatlekérési réteg kialakítása volt. A fejlesztés során a rendszer képessé vált arra, hogy egy adminisztrált Facebook-oldalhoz kapcsolódó adatokat közvetlenül a Graph API-n keresztül érjen el.

### Konfiguráció és hitelesítés

A Facebook API-hozzáféréshez szükséges adatok környezeti változókból kerülnek betöltésre. A `.env` fájl tartalmazza:

```text
FACEBOOK_ACCESS_TOKEN
FACEBOOK_PAGE_ID
FACEBOOK_GRAPH_API_VERSION
```

A token és az oldalazonosító nem kerül verziókezelés alá.

### Új modulok

A Facebook API kezeléséhez az alábbi modulok készültek:

```text
src/facebook_api/
├── __init__.py
├── config.py
├── graph_api_client.py
├── post_fetcher.py
├── comment_fetcher.py
└── facebook_data_mapper.py
```

### Graph API kliens

A `graph_api_client.py` felelős az API-kérések végrehajtásáért. A kliens kezeli:

```text
GET kérések küldését
access token használatát
API-verzió kezelését
hálózati hibákat
Meta API hibaválaszokat
lapozott lekérések támogatását
```

### Posztok lekérése

A rendszer képes egy konkrét Facebook-poszt alapadatainak lekérésére.

A lekért adatok többek között:

```text
post_id
post_text
post_link
created_time
```

Ezen kívül külön teszt készült az oldal legutóbbi bejegyzéseinek lekérésére is.

### Kommentek lekérése

A `comment_fetcher.py` segítségével a rendszer egy adott poszthoz tartozó kommenteket is le tudja kérni.

A kommentlekérés támogatja a Graph API lapozását, így több oldalnyi komment automatikusan összegyűjthető.

A normalizált kommentadatok többek között:

```text
post_id
comment_id
comment_text
created_time
```

### Adatok átalakítása

A `facebook_data_mapper.py` a Graph API-ból érkező adatokat pandas DataFrame formára alakítja.

A létrehozott struktúra illeszkedik a projekt meglévő feldolgozási logikájához, így később közvetlenül beköthető a sentiment elemzési pipeline-ba.

A valódi Facebook-adatok esetén a `manual_label` mező üres marad, mivel ezekhez nem tartozik előzetesen kézzel megadott referencia-címke.

### Tesztelés

A fejlesztési iteráció során külön tesztek készültek az alábbi funkciók ellenőrzésére:

```text
API-kapcsolat ellenőrzése
Facebook-oldal elérése
posztok lekérése
konkrét poszt lekérése
kommentek lekérése
pagination kezelése
DataFrame átalakítás
```

A tesztek valódi Facebook-oldallal és érvényes Page Access Tokennel sikeresen lefutottak.

### Eredmény

A tizenegyedik iteráció eredményeként elkészült az önálló Facebook Graph API adatlekérési réteg. A rendszer már képes valódi Facebook-posztok és kommentek lekérésére, valamint ezek belső adatstruktúrára történő átalakítására.

A következő fejlesztési iteráció feladata az API-adatforrás bekötése lesz a közös feldolgozási pipeline-ba és a Streamlit felületbe.


## 12. iteráció – Validációs teszthalmaz bővítése

A tizenkettedik fejlesztési iteráció célja a validációs adathalmaz méretének növelése és domain-specifikusabbá tétele volt. A korábbi teszthalmaz kiegészítésre került további Facebook-posztokkal és az azokhoz tartozó kommentekkel annak érdekében, hogy a későbbi modellfinomítás és kiértékelés megbízhatóbb alapokon történjen.

Az új kommentek nyers formában kerültek eltárolásra, az eredeti Unicode emojik megtartásával. Ez azért fontos, mert a későbbi kísérletek során külön vizsgálható lesz a nyers emoji, a szöveges emoji-leírás és a korábban alkalmazott tokenizált forma hatása a modell teljesítményére.

A kibővített adathalmaz minden kommentje kézi sentimentcímkét kap pozitív, negatív vagy semleges kategóriában. Az így létrejött nagyobb, egységesen címkézett adathalmaz szolgál majd alapul a tanító-, validációs- és teszthalmaz kialakításához, valamint a huBERT modell későbbi domain-specifikus finomhangolásához.



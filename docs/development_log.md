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
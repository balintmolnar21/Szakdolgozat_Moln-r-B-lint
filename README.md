# „Social media” hangulatelemző szoftver

## Saját adatok

- **Név:** Molnár Bálint Ottó
- **Neptun-kód:** VP35W1
- **Szak:** Mérnökinformatiksu Bsc
- **Intézmény:** Széchenyi István Egyetem
- **Készítés éve:** 2026.


---
## Fejlesztési környezet beállítása

A projekt Python alapú alkalmazás, ezért a futtatásához Python 3.11 verzió használata javasolt.  
A függőségek elkülönített virtuális környezetben kerülnek telepítésre, így nem keverednek a rendszer globálisan telepített Python-csomagjaival.

### 1. Projekt mappájának megnyitása

A terminálban először a projekt gyökérmappájába kell lépni:

```bash
cd "C:\Users\USER\Desktop\projektek_fejlesztes\diplomamunka\Szakdolgozat_Moln-r-B-lint"
```
### 2. .venv létrehozása és aktiválása
 ```bash
py -3.11 -m venv .venv
```
Majd:
 ```bash
.venv\Scripts\activate
```
Végül pedig a requirements.txt telepítése
 ```bash
py -m pip install --upgrade pip
```
 ```bash
py -m pip install -r requirements.txt
```

---

## Projektleírás

Ez a repository egy Python alapú szoftverprototípust tartalmaz, amely Facebook-oldalak bejegyzéseinek és kommentjeinek automatikus hangulatelemzésére készült. A rendszer célja, hogy egy megadott bejegyzéshez kapcsolódó felhasználói visszajelzéseket összegyűjtse, feldolgozza, majd ezek alapján átfogó képet adjon a tartalom fogadtatásáról. A megoldás a Facebook Graph API használatára, szöveg-előfeldolgozásra és NLP-alapú sentiment elemzésre épül. :contentReference[oaicite:1]{index=1}

A projekt központi feladata, hogy a közösségi médiában keletkező nagy mennyiségű kommentet és reakciót automatizált módon elemezze, és az eredményeket áttekinthető, összesített formában jelenítse meg.

---

## A megoldandó probléma

A közösségi médiafelületeken megjelenő posztokhoz gyakran nagyszámú reakció, hozzászólás és válaszkomment kapcsolódik. Ezek kézi feldolgozása időigényes, nehezen átlátható, és sok esetben szubjektív. A rendszer célja, hogy a bejegyzésekhez tartozó szöveges visszajelzéseket automatikusan feldolgozza, majd azok hangulati jellemzőit meghatározza, ezzel támogatva a tartalom fogadtatásának gyorsabb értelmezését. :contentReference[oaicite:2]{index=2}

---

## A rendszer célja

A rendszer elsődleges célja egy olyan működő prototípus létrehozása, amely:

- képes egy Facebook-bejegyzés azonosítására link vagy egyedi azonosító alapján,
- lekéri a poszthoz tartozó releváns adatokat,
- előfeldolgozza a bejegyzés és a kommentek szövegét,
- automatikus hangulatelemzést végez,
- összesített statisztikákat állít elő,
- és az eredményeket könnyen értelmezhető formában jeleníti meg. :contentReference[oaicite:3]{index=3}

---

## Fő funkciók

A rendszer főbb funkciói:

- Facebook-bejegyzés azonosítása link vagy posztazonosító alapján
- Adatok lekérdezése a Facebook Graph API segítségével
- Kommentek feldolgozható formában történő kezelése
- Szöveg-előfeldolgozás
- Kommentek automatikus hangulatelemzése
- Összesített értékelés készítése a bejegyzés fogadtatásáról
- Statisztikai eredmények előállítása
- Eredmények megjelenítése
- Hibakezelés
- Bővíthető moduláris felépítés támogatása :contentReference[oaicite:4]{index=4}

---

## A rendszer működésének áttekintése

A rendszer működése több egymásra épülő lépésből áll:

1. A felhasználó megadja a vizsgálni kívánt Facebook-bejegyzést.
2. A rendszer lekéri a releváns adatokat a Facebook Graph API-n keresztül.
3. A bejegyzés és a kommentek szövege előfeldolgozásra kerül.
4. A hangulatelemző modul meghatározza az egyes kommentek érzelmi kategóriáját.
5. A rendszer összesíti az eredményeket.
6. A felhasználó statisztikai és szöveges összesítést kap a poszt általános fogadtatásáról. :contentReference[oaicite:5]{index=5}

---

## Alkalmazott technológiák

A specifikáció alapján a projekt fejlesztéséhez az alábbi technológiák és eszközök használata indokolt:

- **Python**
- **venv** virtuális környezet
- **PyCharm**
- **Git / GitHub**
- **Facebook Graph API**
- **pandas**
- **Matplotlib**
- **scikit-learn**
- **Hugging Face Transformers**
- **PyTorch**

A specifikáció említi továbbá, hogy a rendszerhez magyar nyelvű előtanított modellek és referencia-adatkészletek is felhasználhatók, például magyar sentiment feladatokra alkalmas modellek és a HuSST adatkészlet. :contentReference[oaicite:6]{index=6}

---

## Adatforrások és kezelt adatok

A rendszer elsődleges adatforrása a Facebook Graph API. Az elemzéshez a következő adatok kerülhetnek felhasználásra:

- a bejegyzés szövege,
- a kommentek szövege,
- a reakciók összesített adatai,
- technikai azonosítók a lekérdezéshez és összekapcsoláshoz. :contentReference[oaicite:7]{index=7}

Az alkalmazás csak olyan adatokkal dolgozik, amelyekhez szabályos hozzáférés áll rendelkezésre, és kizárólag a működéshez szükséges adatokat kezeli.

---

## Szöveg-előfeldolgozás

A közösségi médiás szövegek gyakran tartalmaznak rövidítéseket, ismétlődő karaktereket, felesleges írásjeleket, emojikat és más, a feldolgozást nehezítő elemeket. A rendszer előfeldolgozási lépéseinek célja, hogy a nyers szöveges adatokat alkalmassá tegye az automatikus elemzésre.

Az előfeldolgozás során például az alábbi lépések történhetnek:

- üres vagy hiányos szövegek kiszűrése,
- zavaró karakterek kezelése,
- szöveg egységesítése,
- nem releváns elemek eltávolítása vagy figyelmen kívül hagyása. :contentReference[oaicite:8]{index=8}

---

## Hangulatelemzés

A rendszer a bejegyzések és kommentek automatikus értékelésére hangulatelemzési eljárást alkalmaz. Az elemzés célja annak meghatározása, hogy az adott szöveg pozitív, negatív vagy semleges érzelmi töltetű-e.

Az alkalmazott módszer előtanított nyelvi modellre vagy más NLP-alapú szövegosztályozási megoldásra épülhet. A megközelítés célja, hogy a rövid, informális közösségi médiás szövegek esetén is használható eredményt adjon. :contentReference[oaicite:9]{index=9}

---

## Eredmények és statisztikák

A rendszer az elemzés alapján összesített eredményeket állít elő, például:

- pozitív kommentek száma,
- negatív kommentek száma,
- semleges kommentek száma,
- hangulati arányok,
- a bejegyzés általános fogadtatásának összesített értékelése. :contentReference[oaicite:10]{index=10}

Az eredmények megjelenhetnek:

- szöveges összefoglalásként,
- táblázatos formában,
- egyszerű grafikus kimutatásként. :contentReference[oaicite:11]{index=11}

---

## Nem funkcionális követelmények

A rendszerrel szemben támasztott főbb nem funkcionális elvárások:

- egyszerű használhatóság,
- megbízható működés,
- prototípus szinten elfogadható teljesítmény,
- karbantartható moduláris felépítés,
- biztonságos hitelesítési adatkezelés,
- kompatibilitás Python-alapú környezettel,
- lehető legjobb pontosság,
- átlátható működés és eredményközlés. :contentReference[oaicite:12]{index=12}

---

## Fejlesztési megközelítés

A specifikáció szerint a projekt iteratív prototípusfejlesztési megközelítést követ. Ez azt jelenti, hogy a rendszer nem egyetlen lépésben készül el, hanem egymásra épülő fejlesztési szakaszok során válik egyre teljesebbé.

A fejlesztés főbb iterációi:

1. adatlekérési folyamat kialakítása,
2. szövegek előfeldolgozása,
3. hangulatelemzés integrálása,
4. eredmények összesítése és megjelenítése,
5. hibakezelés és finomhangolás. :contentReference[oaicite:13]{index=13}

---

## Használat

A rendszer használata egyszerű:

1. Add meg a vizsgálni kívánt Facebook-bejegyzés linkjét vagy azonosítóját.
2. A rendszer automatikusan lekéri az adatokat.
3. Lefut a szöveg-előfeldolgozás és a hangulatelemzés.
4. A rendszer megjeleníti az összesített eredményeket és statisztikákat. :contentReference[oaicite:14]{index=14}

---

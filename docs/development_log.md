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
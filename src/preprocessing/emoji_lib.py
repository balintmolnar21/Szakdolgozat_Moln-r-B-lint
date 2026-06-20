try:
    import emoji as emoji_lib
except ImportError:
    emoji_lib = None


CUSTOM_EMOJI_TOKEN_MAP = {
    # Pozitív / öröm
    "😀": " [mosolygós emoji] ",
    "😃": " [mosolygós emoji] ",
    "😄": " [mosolygós emoji] ",
    "😁": " [mosolygós emoji] ",
    "😆": " [nevetős emoji] ",
    "😅": " [mosolygós emoji] ",
    "😂": " [nevetős emoji] ",
    "🤣": " [nevetős emoji] ",
    "😊": " [mosolygós emoji] ",
    "😇": " [mosolygós emoji] ",
    "🙂": " [mosolygós emoji] ",
    "😉": " [kacsintós emoji] ",
    "😍": " [szeretetteljes emoji] ",
    "🥰": " [szeretetteljes emoji] ",
    "😘": " [szeretetteljes emoji] ",
    "😋": " [elégedett emoji] ",
    "🤩": " [lelkes emoji] ",
    "🥳": " [ünneplő emoji] ",

    # Semleges / bizonytalan
    "😐": " [semleges emoji] ",
    "😑": " [semleges emoji] ",
    "😶": " [semleges emoji] ",
    "🙄": " [szemforgatós emoji] ",
    "🤔": " [gondolkodó emoji] ",
    "🫤": " [bizonytalan emoji] ",
    "😬": " [kínos emoji] ",
    "😶‍🌫️": " [bizonytalan emoji] ",

    # Szomorúság / csalódottság
    "😔": " [szomorú emoji] ",
    "😞": " [szomorú emoji] ",
    "😟": " [aggódó emoji] ",
    "😢": " [szomorú emoji] ",
    "😭": " [síró emoji] ",
    "☹️": " [szomorú emoji] ",
    "🙁": " [szomorú emoji] ",
    "😕": " [bizonytalan emoji] ",
    "😣": " [szenvedő emoji] ",
    "😖": " [szenvedő emoji] ",
    "😫": " [fáradt emoji] ",
    "😩": " [fáradt emoji] ",

    # Düh / elégedetlenség
    "😠": " [dühös emoji] ",
    "😡": " [dühös emoji] ",
    "🤬": " [dühös emoji] ",
    "😤": " [elégedetlen emoji] ",
    "👿": " [dühös emoji] ",
    "😾": " [dühös emoji] ",

    # Meglepődés / félelem
    "😮": " [meglepett emoji] ",
    "😯": " [meglepett emoji] ",
    "😲": " [meglepett emoji] ",
    "😳": " [zavarban lévő emoji] ",
    "😱": " [félelemmel teli emoji] ",
    "😨": " [aggódó emoji] ",
    "😰": " [aggódó emoji] ",
    "😥": " [megkönnyebbült vagy szomorú emoji] ",

    # Támogatás / reakció
    "👍": " [like] ",
    "👎": " [dislike] ",
    "👏": " [taps] ",
    "🙌": " [ünneplés] ",
    "🙏": " [köszönet] ",
    "🤝": " [kézfogás] ",
    "💪": " [erő emoji] ",
    "👌": " [ok emoji] ",
    "✌️": " [béke emoji] ",
    "✅": " [pipa] ",
    "✔️": " [pipa] ",
    "❌": " [elutasítás] ",
    "🚫": " [tiltás] ",

    # Szívek / érzelmi támogatás
    "❤️": " [szív emoji] ",
    "❤": " [szív emoji] ",
    "💙": " [kék szív emoji] ",
    "💚": " [zöld szív emoji] ",
    "💛": " [sárga szív emoji] ",
    "🧡": " [narancs szív emoji] ",
    "💜": " [lila szív emoji] ",
    "🖤": " [fekete szív emoji] ",
    "🤍": " [fehér szív emoji] ",
    "🤎": " [barna szív emoji] ",
    "💔": " [összetört szív emoji] ",
    "💕": " [szív emoji] ",
    "💞": " [szív emoji] ",
    "💓": " [szív emoji] ",
    "💗": " [szív emoji] ",
    "💖": " [szív emoji] ",

    # Politikai / közéleti kommunikációban gyakori
    "🇭🇺": " [magyar zászló] ",
    "🚩": " [zászló emoji] ",
    "📢": " [felhívás] ",
    "📣": " [felhívás] ",
    "🗳️": " [szavazás] ",
    "✍️": " [írás] ",
    "📝": " [jegyzet] ",
    "📌": " [kiemelés] ",
    "📍": " [helyszín] ",

    # Irányjelző / figyelemfelhívó
    "👇": " [lefelé mutató emoji] ",
    "👆": " [felfelé mutató emoji] ",
    "☝️": " [felfelé mutató emoji] ",
    "👉": " [jobbra mutató emoji] ",
    "👈": " [balra mutató emoji] ",
    "➡️": " [jobbra nyíl emoji] ",
    "⬅️": " [balra nyíl emoji] ",
    "⬆️": " [felfelé nyíl emoji] ",
    "⬇️": " [lefelé nyíl emoji] ",

    # Erősítés / figyelem / kiemelés
    "🔥": " [tűz emoji] ",
    "💥": " [erős hatás emoji] ",
    "⭐": " [csillag emoji] ",
    "🌟": " [csillag emoji] ",
    "✨": " [kiemelés] ",
    "⚠️": " [figyelmeztetés] ",
    "❗": " [felkiáltójel] ",
    "❗️": " [felkiáltójel] ",
    "❓": " [kérdőjel] ",

    # Közösségi média
    "💬": " [komment] ",
    "🗨️": " [komment] ",
    "🔗": " [link] ",
    "📷": " [fénykép] ",
    "📸": " [fénykép] ",
    "🎥": " [videó] ",
    "🎬": " [videó] ",
    "📺": " [videó] ",
}


FLAG_KEYWORDS = [
    "flag",
]

ANIMAL_KEYWORDS = [
    "animal", "dog", "cat", "mouse", "hamster", "rabbit", "bunny", "fox",
    "bear", "panda", "koala", "tiger", "lion", "cow", "pig", "frog",
    "monkey", "bird", "penguin", "chicken", "duck", "eagle", "owl",
    "horse", "zebra", "deer", "camel", "llama", "giraffe", "elephant",
    "rhinoceros", "hippopotamus", "kangaroo", "bat", "wolf", "boar",
    "goat", "ram", "sheep", "bee", "butterfly", "bug", "beetle",
    "cricket", "spider", "scorpion", "mosquito", "fly", "worm",
    "snail", "fish", "dolphin", "whale", "shark", "octopus", "squid",
    "crab", "lobster", "shrimp", "seal", "snake", "lizard", "crocodile",
    "turtle", "dragon", "unicorn",
]

VEHICLE_KEYWORDS = [
    "car", "automobile", "taxi", "bus", "trolleybus", "truck", "lorry",
    "tractor", "bicycle", "bike", "scooter", "motorcycle", "motorbike",
    "train", "locomotive", "tram", "metro", "subway", "railway",
    "airplane", "aeroplane", "aircraft", "helicopter", "rocket",
    "ship", "boat", "ferry", "sailboat", "canoe", "ambulance",
    "fire engine", "police car", "racing car", "delivery truck",
]

OBJECT_KEYWORDS = [
    "compass", "phone", "mobile", "telephone", "computer", "laptop",
    "keyboard", "mouse", "printer", "camera", "video camera",
    "television", "tv", "radio", "microphone", "headphone", "speaker",
    "battery", "plug", "bulb", "flashlight", "candle", "book",
    "notebook", "ledger", "page", "newspaper", "pen", "pencil",
    "crayon", "paintbrush", "scissors", "briefcase", "bag", "backpack",
    "purse", "wallet", "money", "coin", "credit card", "receipt",
    "key", "lock", "hammer", "wrench", "screwdriver", "tool",
    "gear", "magnet", "ladder", "package", "box", "gift", "balloon",
    "chair", "bed", "door", "window", "mirror", "basket", "bucket",
    "soap", "toothbrush", "razor", "umbrella", "watch", "clock",
    "hourglass", "calendar", "clipboard", "file", "folder", "label",
    "bell", "bookmark", "link", "chain", "paperclip", "pin",
]

FOOD_KEYWORDS = [
    "apple", "pear", "orange", "lemon", "banana", "watermelon",
    "grapes", "strawberry", "blueberries", "melon", "cherries",
    "peach", "mango", "pineapple", "coconut", "kiwi", "tomato",
    "olive", "eggplant", "potato", "carrot", "corn", "pepper",
    "cucumber", "leafy green", "broccoli", "garlic", "onion",
    "mushroom", "bread", "croissant", "bagel", "pancakes",
    "cheese", "meat", "bacon", "hamburger", "fries", "pizza",
    "sandwich", "taco", "burrito", "salad", "popcorn", "rice",
    "spaghetti", "cake", "cookie", "chocolate", "candy", "coffee",
    "tea", "milk", "beer", "wine", "drink", "cup", "glass",
]

PLACE_KEYWORDS = [
    "house", "home", "building", "office", "school", "hospital",
    "bank", "hotel", "church", "mosque", "synagogue", "temple",
    "castle", "stadium", "factory", "store", "shop", "market",
    "post office", "station", "airport", "park", "mountain",
    "beach", "desert", "island", "city", "village", "bridge",
    "fountain", "tent",
]

PERSON_KEYWORDS = [
    "person", "people", "man", "woman", "boy", "girl", "child",
    "baby", "older person", "old man", "old woman", "family",
    "couple", "bust", "silhouette", "face", "farmer", "student",
    "teacher", "worker", "doctor", "nurse", "police", "firefighter",
    "judge", "mechanic", "cook", "singer", "artist", "pilot",
]

ACTIVITY_KEYWORDS = [
    "running", "walking", "dancing", "swimming", "cycling", "biking",
    "climbing", "skiing", "football", "soccer", "basketball", "tennis",
    "volleyball", "handball", "baseball", "golf", "boxing", "wrestling",
    "yoga", "medal", "trophy", "game", "sports",
]

NATURE_KEYWORDS = [
    "sun", "moon", "star", "cloud", "rain", "snow", "snowflake",
    "lightning", "thunder", "fire", "water", "droplet", "wave",
    "rainbow", "flower", "rose", "tulip", "tree", "evergreen",
    "cactus", "plant", "leaf", "herb", "seedling", "mushroom",
    "earth", "globe", "volcano",
]

SYMBOL_KEYWORDS = [
    "arrow", "check", "cross", "question", "exclamation", "warning",
    "prohibited", "no entry", "heart", "star", "circle", "square",
    "triangle", "plus", "minus", "divide", "multiply", "copyright",
    "registered", "trade mark", "infinity", "recycling", "peace",
]

HEALTH_KEYWORDS = [
    "pill", "syringe", "drop of blood", "stethoscope", "x-ray",
    "adhesive bandage", "crutch", "wheelchair", "hospital",
    "medical", "mask", "microbe", "soap",
]


def _normalize_emoji_name(demojized_name: str) -> str:
    normalized_name = demojized_name.strip(":")
    normalized_name = normalized_name.replace("_", " ")
    normalized_name = normalized_name.replace("-", " ")
    normalized_name = " ".join(normalized_name.split())
    return normalized_name.lower()


def _contains_keyword(emoji_name: str, keywords: list[str]) -> bool:
    return any(keyword in emoji_name for keyword in keywords)


def get_emoji_category_token(emoji_character: str) -> str | None:
    if emoji_lib is None:
        return None

    demojized_name = emoji_lib.demojize(emoji_character, language="en")

    if demojized_name == emoji_character:
        return None

    emoji_name = _normalize_emoji_name(demojized_name)

    if _contains_keyword(emoji_name, FLAG_KEYWORDS):
        return " [zászló emoji] "

    if _contains_keyword(emoji_name, ANIMAL_KEYWORDS):
        return " [állat emoji] "

    if _contains_keyword(emoji_name, VEHICLE_KEYWORDS):
        return " [jármű emoji] "

    if _contains_keyword(emoji_name, FOOD_KEYWORDS):
        return " [étel emoji] "

    if _contains_keyword(emoji_name, PLACE_KEYWORDS):
        return " [helyszín emoji] "

    if _contains_keyword(emoji_name, PERSON_KEYWORDS):
        return " [személy emoji] "

    if _contains_keyword(emoji_name, ACTIVITY_KEYWORDS):
        return " [tevékenység emoji] "

    if _contains_keyword(emoji_name, HEALTH_KEYWORDS):
        return " [egészség emoji] "

    if _contains_keyword(emoji_name, NATURE_KEYWORDS):
        return " [természet emoji] "

    if _contains_keyword(emoji_name, SYMBOL_KEYWORDS):
        return " [szimbólum emoji] "

    if _contains_keyword(emoji_name, OBJECT_KEYWORDS):
        return " [tárgy emoji] "

    return None


def emoji_to_token(emoji_character: str) -> str:
    if emoji_character in CUSTOM_EMOJI_TOKEN_MAP:
        return CUSTOM_EMOJI_TOKEN_MAP[emoji_character]

    category_token = get_emoji_category_token(emoji_character)

    if category_token is not None:
        return category_token

    return " [emoji] "


def replace_emojis(text: str | None) -> str:
    if text is None:
        return ""

    text = str(text)

    if emoji_lib is not None:
        return emoji_lib.replace_emoji(
            text,
            replace=lambda emoji_character, data: emoji_to_token(emoji_character),
        )

    converted_text = text

    for emoji_character, token in sorted(
        CUSTOM_EMOJI_TOKEN_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        converted_text = converted_text.replace(emoji_character, token)

    return converted_text

# Tesztelési lehetőség
'''
if __name__ == "__main__":
    print(f"Egyedi magyar emoji-tokenek száma: {len(CUSTOM_EMOJI_TOKEN_MAP)}")

    if emoji_lib is None:
        print("Az 'emoji' Python csomag nincs telepítve.")
        print("Telepítés: pip install emoji")
    else:
        print("Az 'emoji' Python csomag elérhető.")

    sample_text = """
    Jó hangulat volt! 😀💙👇
    Állatok: 🐶 🐱 🦊 🐝
    Járművek: 🚗 🚌 🚲 ✈️
    Tárgyak: 📱 💻 📷 🔗 🧭 🪙
    Zászlók: 🇭🇺 🇪🇺 🇩🇪 🇺🇸
    Ételek: 🍎 🍕 ☕
    Helyek: 🏠 🏥 🏫
    Természet: 🌧️ 🌳 🌹
    Ritkább emoji: 🪴 🧩 🪩
    """

    converted_text = replace_emojis(sample_text)

    print("\nEredeti szöveg:")
    print(sample_text)

    print("Tokenizált szöveg:")
    print(converted_text)
'''
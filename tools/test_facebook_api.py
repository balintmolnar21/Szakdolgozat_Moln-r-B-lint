import sys
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from facebook_api.config import (
    get_facebook_access_token,
    get_facebook_graph_api_version,
    get_facebook_page_id,
)


def main() -> None:
    """
    Közvetlenül ellenőrzi a Facebook Graph API kapcsolatot.

    A teszt nem használja a FacebookGraphAPIClient osztályt,
    így a Meta eredeti válasza közvetlenül vizsgálható.
    """

    print("Facebook Graph API kapcsolat tesztelése...")
    print()

    api_version = get_facebook_graph_api_version()
    page_id = get_facebook_page_id()
    access_token = get_facebook_access_token()

    print(f"API-verzió: {api_version}")
    print(f"Facebook Page ID: {page_id}")
    print("Access token: betöltve")
    print()

    url = (
        f"https://graph.facebook.com/"
        f"{api_version}/"
        f"{page_id}"
    )

    params = {
        "fields": "id,name",
        "access_token": access_token,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

    except requests.Timeout:
        print(
            "HIBA: A Facebook Graph API kérés időtúllépés "
            "miatt megszakadt."
        )
        return

    except requests.ConnectionError:
        print(
            "HIBA: Nem sikerült kapcsolódni a Facebook "
            "Graph API-hoz."
        )
        return

    except requests.RequestException:
        print(
            "HIBA: Hálózati hiba történt az API-kérés során."
        )
        return

    print(
        f"HTTP státuszkód: {response.status_code}"
    )

    try:
        response_data = response.json()

    except ValueError:
        print(
            "HIBA: A Meta nem JSON formátumú választ adott."
        )
        print(
            f"Válasz szövege: {response.text}"
        )
        return

    if response.ok:
        print()
        print("A Facebook Graph API kapcsolat sikeres.")
        print("API-válasz:")
        print(response_data)

    else:
        print()
        print("A Facebook Graph API hibát adott vissza.")

        error_data = response_data.get(
            "error",
            {},
        )

        print(
            "Hibatípus:",
            error_data.get(
                "type",
                "ismeretlen",
            ),
        )

        print(
            "Hibakód:",
            error_data.get(
                "code",
                "ismeretlen",
            ),
        )

        if "error_subcode" in error_data:
            print(
                "Hiba alkód:",
                error_data["error_subcode"],
            )

        print(
            "Meta hibaüzenet:",
            error_data.get(
                "message",
                "Ismeretlen hiba.",
            ),
        )


if __name__ == "__main__":
    main()
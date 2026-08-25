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
    print("Facebook-posztok lekérése...")

    api_version = get_facebook_graph_api_version()
    page_id = get_facebook_page_id()
    access_token = get_facebook_access_token()

    url = (
        f"https://graph.facebook.com/"
        f"{api_version}/"
        f"{page_id}/posts"
    )

    params = {
        "fields": (
            "id,"
            "message,"
            "created_time,"
            "permalink_url"
        ),
        "limit": 10,
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

    except requests.RequestException as error:
        print(
            "HIBA: Hálózati hiba történt:"
        )
        print(error)
        return

    try:
        response_data = response.json()

    except ValueError:
        print(
            "HIBA: A Meta nem JSON formátumú választ adott."
        )
        return

    if not response.ok:
        print(
            f"HIBA: HTTP {response.status_code}"
        )

        error_data = response_data.get(
            "error",
            {},
        )

        print(
            "Meta hibaüzenet:",
            error_data.get(
                "message",
                "Ismeretlen hiba.",
            ),
        )

        return

    posts = response_data.get(
        "data",
        [],
    )

    print()
    print(
        f"Lekért posztok száma: {len(posts)}"
    )

    if not posts:
        print(
            "Az API nem adott vissza bejegyzéseket."
        )
        return

    for index, post in enumerate(
        posts,
        start=1,
    ):
        print()
        print("=" * 60)
        print(f"{index}. poszt")
        print("=" * 60)

        print(
            "Post ID:",
            post.get("id"),
        )

        print(
            "Létrehozás:",
            post.get("created_time"),
        )

        print(
            "Link:",
            post.get("permalink_url"),
        )

        message = post.get(
            "message",
            "",
        )

        print(
            "Szöveg:",
            message[:500],
        )


if __name__ == "__main__":
    main()
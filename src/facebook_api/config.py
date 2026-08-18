import os

from dotenv import load_dotenv


load_dotenv()


def get_facebook_access_token() -> str:
    """
    Betölti a Facebook Graph API hozzáférési tokent
    a környezeti változók közül.

    Returns:
        A konfigurált access token.

    Raises:
        ValueError:
            Ha a FACEBOOK_ACCESS_TOKEN nincs megadva.
    """
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")

    if not access_token:
        raise ValueError(
            "A FACEBOOK_ACCESS_TOKEN környezeti változó nincs beállítva."
        )

    return access_token


def get_facebook_graph_api_version() -> str:
    """
    Visszaadja a használni kívánt Graph API verzióját.

    A verzió .env fájlból felülírható.
    """
    return os.getenv(
        "FACEBOOK_GRAPH_API_VERSION",
        "v25.0",
    )

def get_facebook_page_id() -> str:
    """
    Betölti a Facebook-oldal azonosítóját
    a környezeti változók közül.
    """
    page_id = os.getenv("FACEBOOK_PAGE_ID")

    if not page_id:
        raise ValueError(
            "A FACEBOOK_PAGE_ID környezeti változó nincs beállítva."
        )

    return page_id
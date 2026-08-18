import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"

if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY),
    )


from facebook_api.config import (
    get_facebook_graph_api_version,
    get_facebook_page_id,
)
from facebook_api.graph_api_client import (
    FacebookGraphAPIClient,
)


def main() -> None:
    print("Facebook Graph API kapcsolat tesztelése...")

    print(
        "API-verzió:",
        get_facebook_graph_api_version(),
    )

    print(
        "Facebook Page ID:",
        get_facebook_page_id(),
    )

    client = FacebookGraphAPIClient()

    result = client.test_connection()

    print("A kapcsolat sikeres.")
    print("API-válasz:")
    print(result)


if __name__ == "__main__":
    main()
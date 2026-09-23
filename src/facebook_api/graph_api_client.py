from typing import Any

import requests

from facebook_api.config import (
    get_facebook_access_token,
    get_facebook_graph_api_version,
)


class FacebookGraphAPIClient:
    

    BASE_URL = "https://graph.facebook.com"

    def __init__(
        self,
        access_token: str | None = None,
        api_version: str | None = None,
        timeout: int = 30,
    ) -> None:
        
        self.access_token = (
            access_token
            if access_token is not None
            else get_facebook_access_token()
        )

        self.api_version = (
            api_version
            if api_version is not None
            else get_facebook_graph_api_version()
        )

        self.timeout = timeout

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        
        request_params = dict(params or {})

        request_params["access_token"] = self.access_token

        endpoint = endpoint.lstrip("/")

        url = (
            f"{self.BASE_URL}/"
            f"{self.api_version}/"
            f"{endpoint}"
        )

        try:
            response = requests.get(
                url,
                params=request_params,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise RuntimeError(
                "A Facebook Graph API kérés sikertelen volt."
            ) from error

        response_data = response.json()

        if "error" in response_data:
            error_data = response_data["error"]

            error_message = error_data.get(
                "message",
                "Ismeretlen Facebook API hiba.",
            )

            error_code = error_data.get(
                "code",
                "ismeretlen",
            )

            raise RuntimeError(
                "Facebook Graph API hiba "
                f"(kód: {error_code}): {error_message}"
            )

        return response_data


    def get_from_url(
            self,
            url: str,
        ) -> dict[str, Any]:
            
            try:
                response = requests.get(
                    url,
                    timeout=self.timeout,
                )

            except requests.RequestException as error:
                raise RuntimeError(
                    "A Facebook Graph API következő oldalának "
                    "lekérése sikertelen volt."
                ) from error

            try:
                response_data = response.json()

            except ValueError as error:
                raise RuntimeError(
                    "A Facebook Graph API nem JSON választ adott."
                ) from error

            if not response.ok:
                error_data = response_data.get(
                    "error",
                    {},
                )

                raise RuntimeError(
                    "Facebook Graph API hiba: "
                    f"{error_data.get('message', 'Ismeretlen hiba.')}"
                )

            return response_data

    def test_connection(self) -> dict[str, Any]:
        
        return self.get(
            endpoint="me",
            params={
                "fields": "id,name",
            },
    )
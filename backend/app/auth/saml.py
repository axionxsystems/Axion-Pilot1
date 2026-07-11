import os
from typing import Any

from fastapi import Request
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class SAMLAuth:
    def __init__(self, saml_settings: dict, request_data: dict | None = None):
        self.request_data = request_data or self._build_default_request()
        self.auth = OneLogin_Saml2_Auth(self.request_data, old_settings=saml_settings)

    def _build_default_request(self) -> dict[str, Any]:
        host = os.getenv("SAML_ENTITY_ID", "localhost").replace("https://", "").replace("http://", "")
        return {
            "https": "on",
            "http_host": host,
            "server_port": "443",
            "script_name": "/auth/saml/callback",
            "get_data": {},
            "post_data": {},
            "query_string": "",
        }

    def _build_request_from_form(self, saml_response: str, relay_state: str | None) -> dict[str, Any]:
        host = os.getenv("SAML_ENTITY_ID", "localhost").replace("https://", "").replace("http://", "")
        return {
            "https": "on",
            "http_host": host,
            "server_port": "443",
            "script_name": "/auth/saml/callback",
            "get_data": {"RelayState": relay_state} if relay_state else {},
            "post_data": {"SAMLResponse": saml_response},
            "query_string": "",
        }

    def get_login_url(self) -> tuple[str | None, str]:
        redirect_url = self.auth.login()
        return self.auth.get_last_request_id(), redirect_url

    def process_response(self, saml_response_b64: str, relay_state: str | None = None) -> dict[str, Any]:
        request_data = self._build_request_from_form(saml_response_b64, relay_state)
        self.auth = OneLogin_Saml2_Auth(request_data, old_settings=self.auth.get_settings())
        self.auth.process_response()

        errors = self.auth.get_errors()
        if errors:
            raise Exception("SAML authentication failed: %s" % ", ".join(errors))

        if not self.auth.is_authenticated():
            raise Exception("SAML authentication failed")

        return {
            "email": self._get_attribute("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"),
            "first_name": self._get_attribute("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname"),
            "last_name": self._get_attribute("http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"),
            "groups": self.auth.get_attribute("groups") or [],
        }

    def _get_attribute(self, name: str) -> str:
        values = self.auth.get_attribute(name)
        return values[0] if values else ""

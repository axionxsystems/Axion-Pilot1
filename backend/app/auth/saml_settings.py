import os
import xml.etree.ElementTree as ET

import httpx


def get_auth0_saml_cert() -> str:
    metadata_url = os.getenv("SAML_METADATA_URL", "").strip()
    if not metadata_url:
        raise RuntimeError("SAML_METADATA_URL is not configured")

    response = httpx.get(metadata_url, timeout=10.0)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    ns = {
        "md": "urn:oasis:names:tc:SAML:2.0:metadata",
        "ds": "http://www.w3.org/2000/09/xmldsig#",
    }
    cert_elem = root.find(".//ds:X509Certificate", namespaces=ns)
    if cert_elem is None or not cert_elem.text:
        raise RuntimeError("Unable to extract Auth0 SAML certificate from metadata")

    return cert_elem.text.strip()


def get_saml_settings(org_id: str) -> dict:
    entity_id = os.getenv("SAML_ENTITY_ID", "").strip()
    acs_url = os.getenv("SAML_ACS_URL", "").strip()
    if not entity_id or not acs_url:
        raise RuntimeError("SAML_ENTITY_ID and SAML_ACS_URL must be configured")

    return {
        "strict": True,
        "debug": False,
        "sp": {
            "entityId": entity_id,
            "assertionConsumerService": {
                "url": acs_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        },
        "idp": {
            "entityId": f"urn:auth0:{os.getenv('AUTH0_DOMAIN', '').strip()}",
            "singleSignOnService": {
                "url": f"https://{os.getenv('AUTH0_DOMAIN', '').strip()}/samlp/{os.getenv('AUTH0_CLIENT_ID', '').strip()}",
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "x509cert": get_auth0_saml_cert(),
        },
    }

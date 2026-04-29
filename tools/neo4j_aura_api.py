"""Small Neo4j Aura API helper.

The Aura API uses OAuth2 client credentials. This script prompts for the client
secret when it is not already supplied through the environment, so secrets do not
need to be placed in shell history or repository files.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
import urllib.error
import urllib.request


API_BASE = "https://api.neo4j.io"
TOKEN_URL = f"{API_BASE}/oauth/token"


def env_or_prompt(name: str, prompt: str, secret: bool = False) -> str:
    value = os.getenv(name)
    if value:
        return value
    return getpass.getpass(prompt) if secret else input(prompt)


def token(client_id: str, client_secret: str) -> str:
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
    data = b"grant_type=client_credentials"
    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["access_token"]


def api_get(access_token: str, path: str) -> dict:
    request = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["instances", "projects"], help="Aura API command.")
    args = parser.parse_args()

    client_id = env_or_prompt("NEO4J_AURA_CLIENT_ID", "Neo4j Aura client ID: ")
    client_secret = env_or_prompt("NEO4J_AURA_CLIENT_SECRET", "Neo4j Aura client secret: ", secret=True)

    try:
        access_token = token(client_id, client_secret)
        path = "/v1/instances" if args.command == "instances" else "/v1/projects"
        print(json.dumps(api_get(access_token, path), indent=2))
    except urllib.error.HTTPError as exc:
        print(exc.read().decode("utf-8"))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

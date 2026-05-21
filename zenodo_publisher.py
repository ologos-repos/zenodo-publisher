import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests


ZENODO_API = "https://zenodo.org/api"
ZENODO_SANDBOX_API = "https://sandbox.zenodo.org/api"


class ZenodoPublisherError(RuntimeError):
    pass


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_token() -> str:
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        raise ZenodoPublisherError("Set ZENODO_ACCESS_TOKEN in your environment or .env file.")
    return token


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def request(method: str, url: str, token: str, **kwargs: Any) -> dict[str, Any]:
    params = kwargs.pop("params", {}) or {}
    params["access_token"] = token
    response = requests.request(method, url, params=params, timeout=kwargs.pop("timeout", 60), **kwargs)
    if response.status_code >= 400:
        raise ZenodoPublisherError(f"Zenodo API error {response.status_code}: {response.text}")
    if response.content:
        return response.json()
    return {}


def create_deposition(api_base: str, token: str) -> dict[str, Any]:
    return request("POST", f"{api_base}/deposit/depositions", token, json={})


def update_metadata(api_base: str, token: str, deposition_id: int, metadata: dict[str, Any]) -> dict[str, Any]:
    if "metadata" not in metadata:
        raise ZenodoPublisherError("Metadata JSON must contain a top-level 'metadata' object.")
    return request("PUT", f"{api_base}/deposit/depositions/{deposition_id}", token, json=metadata)


def upload_file(bucket_url: str, token: str, file_path: Path) -> dict[str, Any]:
    with file_path.open("rb") as file_handle:
        return request(
            "PUT",
            f"{bucket_url}/{file_path.name}",
            token,
            data=file_handle,
            timeout=180,
        )


def publish_deposition(api_base: str, token: str, deposition_id: int) -> dict[str, Any]:
    return request("POST", f"{api_base}/deposit/depositions/{deposition_id}/actions/publish", token)


def api_base_for(sandbox: bool) -> str:
    return ZENODO_SANDBOX_API if sandbox else ZENODO_API


def create_record(files: list[Path], metadata: dict[str, Any], sandbox: bool = False, publish: bool = False) -> dict[str, Any]:
    token = require_token()
    api_base = api_base_for(sandbox)
    upload_paths = [path.resolve() for path in files]
    for path in upload_paths:
        if not path.exists():
            raise ZenodoPublisherError(f"File not found: {path}")

    deposition = create_deposition(api_base, token)
    deposition_id = deposition["id"]
    bucket_url = deposition["links"]["bucket"]
    uploaded_files = []

    for path in upload_paths:
        uploaded_files.append(upload_file(bucket_url, token, path))

    updated = update_metadata(api_base, token, deposition_id, metadata)
    result = {
        "deposition_id": deposition_id,
        "draft_url": updated["links"].get("html"),
        "published": False,
        "uploaded_files": uploaded_files,
    }

    if publish:
        published = publish_deposition(api_base, token, deposition_id)
        result["published"] = True
        result["record_url"] = published["links"].get("html")
        result["record"] = published

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Zenodo draft deposition, upload files, and optionally publish.")
    parser.add_argument("files", nargs="+", type=Path, help="Files to upload")
    parser.add_argument("--metadata", type=Path, required=True, help="Zenodo metadata JSON file")
    parser.add_argument("--env", type=Path, default=Path(".env"), help="Optional .env file containing ZENODO_ACCESS_TOKEN")
    parser.add_argument("--sandbox", action="store_true", help="Use sandbox.zenodo.org instead of zenodo.org")
    parser.add_argument("--publish", action="store_true", help="Publish immediately after upload. Default is draft only.")
    args = parser.parse_args()

    load_dotenv(args.env)
    metadata = read_json(args.metadata)
    result = create_record(args.files, metadata, args.sandbox, args.publish)

    print("Created Zenodo deposition.")
    print(f"Deposition ID: {result['deposition_id']}")
    print(f"Draft URL: {result.get('draft_url') or 'Open your Zenodo uploads dashboard'}")

    if result["published"]:
        print("Published deposition.")
        print(f"Record URL: {result.get('record_url') or 'Open your Zenodo records dashboard'}")
    else:
        print("Draft only. Review in Zenodo before publishing.")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ZenodoPublisherError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from zenodo_publisher import (
    ZenodoPublisherError,
    api_base_for,
    create_deposition,
    create_record,
    load_dotenv,
    publish_deposition,
    read_json,
    require_token,
    update_metadata,
    upload_file,
)


mcp = FastMCP("zenodo-publisher")


def _load_env(env_path: str | None) -> None:
    load_dotenv(Path(env_path or ".env"))


def _error(error: Exception) -> dict[str, Any]:
    return {"ok": False, "error": str(error)}


@mcp.tool()
def create_zenodo_draft(sandbox: bool = False, env_path: str | None = None) -> dict[str, Any]:
    """Create an empty Zenodo draft deposition and return its deposition ID and bucket URL."""
    try:
        _load_env(env_path)
        token = require_token()
        deposition = create_deposition(api_base_for(sandbox), token)
        return {
            "ok": True,
            "deposition_id": deposition["id"],
            "bucket_url": deposition["links"]["bucket"],
            "draft_url": deposition["links"].get("html"),
            "deposition": deposition,
        }
    except ZenodoPublisherError as error:
        return _error(error)


@mcp.tool()
def set_zenodo_metadata(
    deposition_id: int,
    metadata_path: str,
    sandbox: bool = False,
    env_path: str | None = None,
) -> dict[str, Any]:
    """Apply metadata from a JSON file to an existing Zenodo draft deposition."""
    try:
        _load_env(env_path)
        token = require_token()
        metadata = read_json(Path(metadata_path))
        updated = update_metadata(api_base_for(sandbox), token, deposition_id, metadata)
        return {
            "ok": True,
            "deposition_id": deposition_id,
            "draft_url": updated["links"].get("html"),
            "deposition": updated,
        }
    except (OSError, ZenodoPublisherError) as error:
        return _error(error)


@mcp.tool()
def upload_zenodo_file(bucket_url: str, file_path: str, env_path: str | None = None) -> dict[str, Any]:
    """Upload one local file to an existing Zenodo deposition bucket URL."""
    try:
        _load_env(env_path)
        token = require_token()
        path = Path(file_path).resolve()
        if not path.exists():
            raise ZenodoPublisherError(f"File not found: {path}")
        uploaded = upload_file(bucket_url, token, path)
        return {"ok": True, "file": str(path), "upload": uploaded}
    except ZenodoPublisherError as error:
        return _error(error)


@mcp.tool()
def publish_zenodo_deposition(
    deposition_id: int,
    sandbox: bool = False,
    confirm: bool = False,
    env_path: str | None = None,
) -> dict[str, Any]:
    """Publish an existing Zenodo draft deposition. Requires confirm=True."""
    try:
        if not confirm:
            raise ZenodoPublisherError("Publishing requires confirm=True.")
        _load_env(env_path)
        token = require_token()
        published = publish_deposition(api_base_for(sandbox), token, deposition_id)
        return {
            "ok": True,
            "deposition_id": deposition_id,
            "record_url": published["links"].get("html"),
            "record": published,
        }
    except ZenodoPublisherError as error:
        return _error(error)


@mcp.tool()
def create_zenodo_record(
    files: list[str],
    metadata_path: str,
    sandbox: bool = False,
    publish: bool = False,
    env_path: str | None = None,
) -> dict[str, Any]:
    """Create a Zenodo draft, upload files, apply metadata, and optionally publish."""
    try:
        _load_env(env_path)
        metadata = read_json(Path(metadata_path))
        result = create_record([Path(file_path) for file_path in files], metadata, sandbox, publish)
        return {"ok": True, **result}
    except (OSError, ZenodoPublisherError) as error:
        return _error(error)


if __name__ == "__main__":
    mcp.run(transport="stdio")

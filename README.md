# Zenodo Publisher

A small CLI and stdio MCP server for creating Zenodo draft depositions from local files and reviewable metadata.

## Features

- Creates a Zenodo draft deposition
- Uploads one or more files
- Applies metadata from JSON
- Loads `ZENODO_ACCESS_TOKEN` from environment or local `.env`
- Supports Zenodo Sandbox
- Publishes only when `--publish` is explicitly provided
- Exposes the same workflow as local MCP tools over stdio

## Install

```powershell
python -m pip install -r requirements.txt
```

## Environment

Create `.env` locally:

```shell
ZENODO_ACCESS_TOKEN=your_token_here
```

Do not commit `.env`.

## Metadata

Copy and edit:

```text
metadata.example.json
```

The JSON must contain a top-level `metadata` object compatible with the Zenodo deposition API.

## Create a draft

```powershell
python zenodo_publisher.py "path/to/file.pdf" --metadata metadata.example.json
```

## Upload multiple files

```powershell
python zenodo_publisher.py "paper.pdf" "source.zip" --metadata metadata.example.json
```

## Sandbox

Use only with a Zenodo Sandbox token:

```powershell
python zenodo_publisher.py "paper.pdf" --metadata metadata.example.json --sandbox
```

## Publish immediately

Draft-first is safer. If you intentionally want to publish immediately:

```powershell
python zenodo_publisher.py "paper.pdf" --metadata metadata.example.json --publish
```

## MCP stdio server

Run the local MCP server:

```powershell
python zenodo_mcp_server.py
```

The MCP server exposes these tools:

- **`create_zenodo_draft`**: Create an empty draft deposition and return the bucket URL.
- **`set_zenodo_metadata`**: Apply metadata from a JSON file to an existing draft.
- **`upload_zenodo_file`**: Upload one file to an existing deposition bucket URL.
- **`publish_zenodo_deposition`**: Publish an existing deposition. Requires `confirm=true`.
- **`create_zenodo_record`**: Create draft, upload files, apply metadata, and optionally publish.

## MCP client configuration

Use the absolute path to this repo on your machine.

```json
{
  "mcpServers": {
    "zenodo-publisher": {
      "command": "python",
      "args": [
        "C:/Users/mlmic/Documents/Sync_Brain/Areas/Writing/Articles/Theseus's Agent Thesis/zenodo-publisher/zenodo_mcp_server.py"
      ],
      "env": {
        "ZENODO_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

If you do not want to put the token in client config, place a `.env` file in the working directory used by the MCP client or pass `env_path` to the tools.

## MCP tool examples

Create a draft record only:

```json
{
  "files": ["C:/path/to/paper.pdf"],
  "metadata_path": "C:/path/to/metadata.json",
  "sandbox": false,
  "publish": false
}
```

Publish is intentionally explicit:

```json
{
  "deposition_id": 123456,
  "confirm": true,
  "sandbox": false
}
```

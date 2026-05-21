# Zenodo Publisher

A small CLI for creating Zenodo draft depositions from local files and reviewable metadata.

## Features

- Creates a Zenodo draft deposition
- Uploads one or more files
- Applies metadata from JSON
- Loads `ZENODO_ACCESS_TOKEN` from environment or local `.env`
- Supports Zenodo Sandbox
- Publishes only when `--publish` is explicitly provided

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

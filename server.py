"""Sekrd MCP server — security scanner for web apps.

Provides 3 tools:
  scan_url    — submit a URL for security scan, poll until done
  get_scan    — retrieve results of a previous scan
  list_findings — get findings with fix prompts
"""

import asyncio
import json
import os
import sys

import httpx

API_BASE = "https://api.sekrd.com/api/v1"
POLL_INTERVAL = 3
MAX_POLLS = 40


def _headers() -> dict:
    """Build request headers with optional API key from env."""
    h = {"Content-Type": "application/json"}
    key = os.environ.get("SEKRD_API_KEY", "")
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


async def scan_url(url: str) -> dict:
    """Submit a URL for a full security scan and wait for results."""
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{API_BASE}/scan/url", json={"url": url}, headers=_headers())
        resp.raise_for_status()
        data = resp.json()
        scan_id = data["scan_id"]

        for _ in range(MAX_POLLS):
            poll = await client.get(f"{API_BASE}/scans/{scan_id}")
            poll.raise_for_status()
            scan = poll.json()
            if scan.get("status") in ("complete", "failed", "error"):
                return scan
            await asyncio.sleep(POLL_INTERVAL)

        return {"error": "Scan timed out", "scan_id": scan_id}


async def get_scan(scan_id: str) -> dict:
    """Retrieve a scan result by its ID."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{API_BASE}/scans/{scan_id}", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def list_findings(scan_id: str) -> list:
    """List findings with fix prompts for a given scan."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{API_BASE}/scans/{scan_id}", headers=_headers())
        resp.raise_for_status()
        scan = resp.json()
    findings = scan.get("findings", [])
    return [f for f in findings if f.get("fix_prompts")]


# --- MCP Protocol (JSON-RPC over stdio) ---

TOOLS = [
    {
        "name": "scan_url",
        "description": "Run a full security scan on a URL. Returns score, verdict (SHIP/BLOCK), findings, and fix prompts. Takes 10-30 seconds.",
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "The URL to scan (e.g. https://myapp.vercel.app)"}},
            "required": ["url"],
        },
    },
    {
        "name": "get_scan",
        "description": "Get results of a previous scan by its ID.",
        "inputSchema": {
            "type": "object",
            "properties": {"scan_id": {"type": "string", "description": "The scan ID returned by scan_url"}},
            "required": ["scan_id"],
        },
    },
    {
        "name": "list_findings",
        "description": "List findings with copy-paste fix prompts for Cursor, Lovable, and Claude Code.",
        "inputSchema": {
            "type": "object",
            "properties": {"scan_id": {"type": "string", "description": "The scan ID"}},
            "required": ["scan_id"],
        },
    },
]

TOOL_HANDLERS = {
    "scan_url": lambda args: scan_url(args["url"]),
    "get_scan": lambda args: get_scan(args["scan_id"]),
    "list_findings": lambda args: list_findings(args["scan_id"]),
}


def send(msg: dict):
    raw = json.dumps(msg)
    sys.stdout.write(f"Content-Length: {len(raw)}\r\n\r\n{raw}")
    sys.stdout.flush()


def read_message() -> dict:
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line or line.strip() == "":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    length = int(headers.get("content-length", 0))
    if length == 0:
        return {}
    body = sys.stdin.read(length)
    return json.loads(body)


async def handle(msg: dict) -> dict | None:
    method = msg.get("method", "")
    mid = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": mid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "sekrd", "version": "0.1.0"},
            },
        }

    if method == "notifications/initialized":
        return None  # no response needed

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = msg["params"]["name"]
        args = msg["params"].get("arguments", {})
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Unknown tool: {name}"}}
        try:
            result = await handler(args)
            text = json.dumps(result, indent=2) if isinstance(result, (dict, list)) else str(result)
            return {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {"content": [{"type": "text", "text": text}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True},
            }

    # Unknown method
    if mid is not None:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Unknown method: {method}"}}
    return None


async def main():
    while True:
        try:
            msg = read_message()
            if not msg:
                break
            resp = await handle(msg)
            if resp:
                send(resp)
        except (EOFError, KeyboardInterrupt):
            break
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())

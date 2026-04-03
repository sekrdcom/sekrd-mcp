"""Sekrd MCP server — security scanner for web apps."""

import asyncio

import httpx
from fastmcp import FastMCP

mcp = FastMCP("sekrd", instructions="Security scanner for web apps. Use scan_url to audit a URL.")

API_BASE = "https://api.sekrd.com/api/v1"
POLL_INTERVAL = 3
MAX_POLLS = 40  # 2 minutes max


@mcp.tool()
async def scan_url(url: str) -> dict:
    """Submit a URL for a full security scan and wait for results.

    Posts the URL to the Sekrd scan API, then polls every 3 seconds until the
    scan completes (max 2 minutes). Returns the full scan result with score,
    verdict, and findings.
    """
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{API_BASE}/scan/url", json={"url": url})
        resp.raise_for_status()
        data = resp.json()
        scan_id = data["scan_id"]

        for _ in range(MAX_POLLS):
            poll_resp = await client.get(f"{API_BASE}/scans/{scan_id}")
            poll_resp.raise_for_status()
            scan = poll_resp.json()

            status = scan.get("status", "")
            if status in ("complete", "failed", "error"):
                return scan

            await asyncio.sleep(POLL_INTERVAL)

        return {"error": "Scan timed out", "scan_id": scan_id}


@mcp.tool()
async def get_scan(scan_id: str) -> dict:
    """Retrieve a scan result by its ID."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{API_BASE}/scans/{scan_id}")
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def list_findings(scan_id: str) -> list:
    """List findings with fix prompts for a given scan."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{API_BASE}/scans/{scan_id}")
        resp.raise_for_status()
        scan = resp.json()

    findings = scan.get("findings", [])
    return [f for f in findings if f.get("fix_prompt") or f.get("fix_prompts")]


if __name__ == "__main__":
    mcp.run()

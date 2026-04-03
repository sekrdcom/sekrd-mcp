# Sekrd MCP Server

MCP (Model Context Protocol) server for [Sekrd](https://sekrd.com) — deep security audit for AI-built apps. Run security scans directly from Cursor, Claude Code, and other AI IDEs.

## Install

```bash
pip install sekrd-mcp
```

Or run directly with `uvx`:

```bash
uvx sekrd-mcp
```

## Setup

### Claude Code

```bash
claude mcp add sekrd -- uvx sekrd-mcp
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sekrd": {
      "command": "uvx",
      "args": ["sekrd-mcp"]
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sekrd": {
      "command": "uvx",
      "args": ["sekrd-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `scan_url(url)` | Run a security scan on a URL. Returns score, verdict (SHIP/BLOCK), and findings. |
| `get_scan(scan_id)` | Get results of a previous scan by ID. |
| `list_findings(scan_id)` | List findings with fix prompts for a scan. |

## Example

```
> scan_url("https://my-app.vercel.app")

Score: 34/100 — BLOCK
3 critical, 5 high, 2 medium findings

> list_findings("scan_abc123")

1. [CRITICAL] Stripe live secret key exposed in client code
   Fix (Cursor): Move the secret 'sk_live_...' to a .env file...
```

## License

MIT

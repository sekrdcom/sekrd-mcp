# Sekrd MCP Server

MCP (Model Context Protocol) server for [Sekrd](https://sekrd.com) — deep security audit for AI-built apps. Use security scanning directly from Cursor, Claude Code, and other AI IDEs.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### With Claude Code

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "sekrd": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

### With Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sekrd": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `scan_url(url)` | Run a security scan on a URL. Returns score, grade, and findings. |
| `get_scan(scan_id)` | Get results of a previous scan by ID. |
| `list_findings(scan_id)` | List findings with fix prompts for a scan. |

## Example

```
> scan_url("https://my-app.vercel.app")

Score: 34/100 (Grade F)
3 critical, 5 high, 2 medium findings

> list_findings("scan_abc123")

1. [CRITICAL] Stripe live secret key exposed in client code
   Fix (Cursor): Move the secret 'sk_live_...' to a .env file...
```

## License

MIT

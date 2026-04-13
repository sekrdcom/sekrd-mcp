# Sekrd MCP Server

MCP server for [Sekrd](https://sekrd.com) — deep security audit for AI-built apps. Run security scans directly from Cursor, Claude Code, and other AI IDEs.

## Install

```bash
pip install sekrd-mcp
```

Or clone and run directly:

```bash
git clone https://github.com/sekrdcom/sekrd-mcp.git
cd sekrd-mcp
pip install httpx
python server.py
```

## Setup

### Claude Code

```bash
claude mcp add sekrd -- python /path/to/sekrd-mcp/server.py
```

With API key (for paid plans, unlimited scans):

```bash
claude mcp add sekrd -e SEKRD_API_KEY=your_key_here -- python /path/to/sekrd-mcp/server.py
```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sekrd": {
      "command": "python",
      "args": ["/path/to/sekrd-mcp/server.py"],
      "env": {
        "SEKRD_API_KEY": "your_key_here"
      }
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
      "command": "python",
      "args": ["/path/to/sekrd-mcp/server.py"],
      "env": {
        "SEKRD_API_KEY": "your_key_here"
      }
    }
  }
}
```

## API Key

- **Without key**: 10 free scans per month (rate limited by IP)
- **With key**: Unlimited scans on Scan ($9 one-time) or Pro ($29/mo) plans

Get your API key at [sekrd.com/dashboard/settings](https://sekrd.com/dashboard/settings).

## Tools

| Tool | Description |
|------|-------------|
| `scan_url(url)` | Run a security scan on a URL. Returns score, verdict (SHIP/BLOCK), and findings with fix prompts. |
| `get_scan(scan_id)` | Get results of a previous scan by ID. |
| `list_findings(scan_id)` | List only findings that have fix prompts for Cursor, Lovable, Claude Code. |

## Example

```
You: Scan https://my-app.vercel.app for security issues

Sekrd: Score: 34/100 — BLOCK
3 critical, 5 high, 2 medium findings

1. [CRITICAL] Stripe live secret key exposed in client bundle
   Fix (Cursor): Move the secret 'sk_live_...' to a .env file...

2. [CRITICAL] Supabase RLS policy USING(true) on users table
   Fix: Replace with USING(auth.uid() = user_id)...
```

## License

MIT

# QuickStart
adding to settings.json
```json
{
	"mcpServers": {
		"googlemap-mcp": {
			"command": "uvx",
			"args": ["--from", "git+https://github.com/hidariutiwa/googlemap-mcp", "googlemap-mcp"],
			"env": {
				"GOOGLEMAPS_API_KEY": "YOUR API KEY"
			}
		}
	}
}
```

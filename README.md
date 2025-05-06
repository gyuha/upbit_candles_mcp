# Upbit Daily Candles MCP Server

This is a Model Context Protocol (MCP) server that provides access to daily candle data from the Upbit cryptocurrency exchange.

## Features

- Fetch daily candle data for any available market on Upbit
- List all available market symbols
- Calculate price changes over a specified period
- Format candle data in a readable way

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Starting the server

Run the MCP server with:

```bash
python -m src.upbit_candles_mcp.server
```

### Using the MCP API

The server provides the following MCP resources and tools:

#### Resources

- `upbit://markets` - List all available market symbols
- `upbit://candles/daily/{market}` - Get daily candle data for a specific market
  - Parameters:
    - `market`: Market symbol (e.g., "KRW-BTC")
    - `count`: Number of candles to retrieve (default: 7, max: 200)
    - `to`: End date in format 'YYYY-MM-DD' (default: now)

#### Tools

- `fetch_daily_candles`: Fetch and format daily candle data
  - Parameters:
    - `market`: Market symbol (e.g., "KRW-BTC")
    - `days`: Number of days to fetch (default: 7, max: 200)
    - `end_date`: End date in format 'YYYY-MM-DD' (optional)

- `get_price_change`: Calculate the price change over a period
  - Parameters:
    - `market`: Market symbol (e.g., "KRW-BTC")
    - `days`: Number of days to analyze (default: 7, max: 200)

## Example

Using the MCP client to fetch Bitcoin daily candles:

```python
from fastmcp import Client

async def main():
    async with Client("path/to/server.py") as client:
        # Fetch 14 days of Bitcoin candle data
        result = await client.call_tool(
            "fetch_daily_candles", 
            {"market": "KRW-BTC", "days": 14}
        )
        print(result.text)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## API Reference

This project uses the [Upbit API](https://docs.upbit.com/reference) for fetching cryptocurrency data.
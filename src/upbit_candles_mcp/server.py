"""
MCP server implementation for fetching daily candles from Upbit API.
"""

import logging

# Add site-packages to path if needed
import site
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

for site_path in site.getsitepackages():
    if site_path not in sys.path:
        sys.path.append(site_path)

# Import required packages
try:
    import requests
except ImportError:
    print("Error: Could not import 'requests' package")
    print("Installing required packages...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from fastmcp import Context, FastMCP
except ImportError:
    print("Error: Could not import 'fastmcp' package")
    print("Installing required packages...")
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastmcp"])
    from fastmcp import Context, FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("upbit-candles-mcp")

# Create the MCP server
mcp = FastMCP(
    name="Upbit Daily Candles",
    description="MCP server for fetching daily candle data from Upbit API",
)

# Upbit API base URL
UPBIT_API_BASE_URL = "https://api.upbit.com/v1"

# Market symbols cache
market_symbols = []


async def get_market_symbols() -> List[str]:
    """
    Fetch all available market symbols from Upbit.
    """
    global market_symbols

    # Return from cache if available
    if market_symbols:
        return market_symbols

    try:
        response = requests.get(f"{UPBIT_API_BASE_URL}/market/all")
        response.raise_for_status()

        # Extract market codes (e.g., "KRW-BTC")
        markets_data = response.json()
        market_symbols = [market["market"] for market in markets_data]

        return market_symbols
    except Exception as e:
        logger.error(f"Error fetching market symbols: {str(e)}")
        raise Exception(f"Failed to fetch market symbols: {str(e)}")


@mcp.resource("upbit://markets")
async def list_markets() -> List[str]:
    """
    List all available market symbols.
    """
    return await get_market_symbols()


@mcp.resource("upbit://candles/daily/{market}")
async def get_daily_candles(
    market: str, count: int = 7, to: str = None
) -> List[Dict[str, Any]]:
    """
    Get daily candle data for a specific market.

    Args:
        market: Market symbol (e.g., "KRW-BTC")
        count: Number of candles to retrieve (default: 7, max: 200)
        to: End date in format 'YYYY-MM-DD' (default: now)

    Returns:
        List of daily candles
    """
    # Validate market
    available_markets = await get_market_symbols()
    if market not in available_markets:
        raise ValueError(
            f"Invalid market: {market}. Available markets can be found at upbit://markets"
        )

    # Prepare parameters
    params = {
        "market": market,
        "count": min(count, 200),  # Upbit API has a limit of 200
    }

    # Add 'to' parameter if provided
    if to:
        try:
            # Validate date format
            datetime.strptime(to, "%Y-%m-%d")
            params["to"] = to
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")

    try:
        # Make API request
        response = requests.get(f"{UPBIT_API_BASE_URL}/candles/days", params=params)
        response.raise_for_status()

        # Process and return the data
        candles = response.json()

        # Format the response
        formatted_candles = []
        for candle in candles:
            formatted_candle = {
                "market": candle["market"],
                "date": candle["candle_date_time_kst"].split("T")[0],
                "opening_price": candle["opening_price"],
                "high_price": candle["high_price"],
                "low_price": candle["low_price"],
                "trade_price": candle["trade_price"],  # Closing price
                "candle_acc_trade_volume": candle["candle_acc_trade_volume"],
                "candle_acc_trade_price": candle["candle_acc_trade_price"],
            }
            formatted_candles.append(formatted_candle)

        return formatted_candles

    except requests.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        raise Exception(f"Failed to fetch candle data: {str(e)}")


@mcp.tool()
async def fetch_daily_candles(
    market: str, days: int = 7, end_date: Optional[str] = None, ctx: Context = None
) -> str:
    """
    Fetch daily candle data for a specific market.

    Args:
        market: Market symbol (e.g., "KRW-BTC")
        days: Number of days to fetch (default: 7, max: 200)
        end_date: End date in format 'YYYY-MM-DD' (default: today)

    Returns:
        Formatted candle data
    """
    if ctx:
        await ctx.info(f"Fetching {days} days of candle data for {market}")

    try:
        candles = await get_daily_candles(market, days, end_date)

        if ctx:
            await ctx.info(f"Successfully fetched {len(candles)} candles")

        # Format the response as a readable string
        result = f"Daily candles for {market} (past {len(candles)} days):\n\n"

        # Table header
        result += f"{'Date':<12} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<12}\n"
        result += "-" * 70 + "\n"

        # Table rows
        for candle in candles:
            result += (
                f"{candle['date']:<12} "
                f"{candle['opening_price']:<10.2f} "
                f"{candle['high_price']:<10.2f} "
                f"{candle['low_price']:<10.2f} "
                f"{candle['trade_price']:<10.2f} "
                f"{candle['candle_acc_trade_volume']:<12.2f}\n"
            )

        return result

    except Exception as e:
        error_message = f"Error fetching candle data: {str(e)}"
        if ctx:
            await ctx.error(error_message)
        return error_message


@mcp.tool()
async def get_price_change(market: str, days: int = 7, ctx: Context = None) -> str:
    """
    Calculate the price change over a period for a specific market.

    Args:
        market: Market symbol (e.g., "KRW-BTC")
        days: Number of days to analyze (default: 7)
        ctx: Context for MCP communication

    Returns:
        Formatted price change analysis
    """
    try:
        if ctx:
            await ctx.info(f"Analyzing price change for {market} over {days} days")

        # Fetch candles
        candles = await get_daily_candles(market, days)

        if not candles:
            return f"No data available for {market}"

        # Get oldest and newest candles
        oldest_candle = candles[-1]  # First item is most recent in Upbit API
        newest_candle = candles[0]

        # Calculate price change
        start_price = oldest_candle["opening_price"]
        end_price = newest_candle["trade_price"]
        price_change = end_price - start_price
        percent_change = (price_change / start_price) * 100

        # Calculate high and low during the period
        period_high = max(candle["high_price"] for candle in candles)
        period_low = min(candle["low_price"] for candle in candles)

        # Format the result
        result = f"Price Change Analysis for {market} (Past {days} days)\n\n"
        result += f"Period: {oldest_candle['date']} to {newest_candle['date']}\n"
        result += f"Start Price: {start_price:.2f}\n"
        result += f"End Price: {end_price:.2f}\n"
        result += f"Change: {price_change:.2f} ({percent_change:.2f}%)\n"
        result += f"Period High: {period_high:.2f}\n"
        result += f"Period Low: {period_low:.2f}\n"

        if ctx:
            await ctx.info("Price change analysis completed")

        return result

    except Exception as e:
        error_message = f"Error analyzing price data: {str(e)}"
        if ctx:
            await ctx.error(error_message)
        return error_message


def main():
    """
    Run the MCP server
    """
    mcp.run()


if __name__ == "__main__":
    main()

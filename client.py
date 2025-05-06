"""
Upbit Daily Candles MCP Client

This script demonstrates how to use the Upbit Daily Candles MCP server
to fetch cryptocurrency price data from Upbit.
"""

import asyncio
import os
import re

from fastmcp import Client


async def main():
    """Main function to run the MCP client."""
    # 서버 스크립트의 절대 경로 구성
    server_path = os.path.abspath("src/upbit_candles_mcp/server.py")

    # Connect to the MCP server
    print("연결 중...")
    async with Client(server_path) as client:
        print("서버에 연결됨!")

        # 사용 가능한 마켓 목록 확인
        print("\n사용 가능한 마켓 목록을 가져오는 중...")
        markets_response = await client.read_resource("upbit://markets")

        # Extract market symbols from the response
        markets_raw = str(markets_response)
        # Use regex to extract the market codes
        markets_match = re.search(r"\[(.*?)\]", markets_raw)
        if markets_match:
            markets_str = markets_match.group(1)
            # Split by commas and clean up the strings
            markets = [m.strip(" \"'\\n") for m in markets_str.split(",")]
        else:
            markets = []

        print(f"사용 가능한 마켓: {len(markets)}개")

        # Display example markets
        if markets:
            print(f"예시: {', '.join(markets[:5])}...\n")
        else:
            print("마켓 목록을 가져오는데 실패했습니다.\n")

        # 비트코인 일봉 데이터 가져오기
        market = "KRW-BTC"  # 한국원-비트코인 마켓
        days = 10  # 10일간의 데이터

        print(f"{market} {days}일 캔들 데이터 가져오는 중...")
        result = await client.call_tool(
            "fetch_daily_candles", {"market": market, "days": days}
        )

        print("\n일봉 데이터 결과:")
        # Parse and print the tool response
        result_str = str(result)
        # Clean up the response by removing annotations and formatting
        result_text = re.sub(r", annotations=None\)\]", "", result_str)
        result_text = result_text.replace("\\n", "\n")
        print(result_text)

        # 가격 변동 분석
        print(f"\n{market} 가격 변동 분석 중...")
        price_analysis = await client.call_tool(
            "get_price_change", {"market": market, "days": days}
        )

        print("\n가격 변동 분석 결과:")
        # Parse and print the price analysis response
        analysis_str = str(price_analysis)
        # Clean up the response
        analysis_text = re.sub(r", annotations=None\)\]", "", analysis_str)
        analysis_text = analysis_text.replace("\\n", "\n")
        print(analysis_text)


if __name__ == "__main__":
    asyncio.run(main())

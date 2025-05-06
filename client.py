"""
Upbit Daily Candles MCP Client

This script demonstrates how to use the Upbit Daily Candles MCP server
to fetch cryptocurrency price data from Upbit.
"""

import asyncio
import os
import json

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
        
        # In MCP, resource content is automatically serialized to JSON
        markets = []
        for item in markets_response:
            # Convert each item to a string
            markets.append(str(item))
            
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
        # In MCP, tool results are returned as objects with different attributes
        if hasattr(result, 'text'):
            print(result.text)
        else:
            print(str(result))

        # 가격 변동 분석
        print(f"\n{market} 가격 변동 분석 중...")
        price_analysis = await client.call_tool(
            "get_price_change", {"market": market, "days": days}
        )

        print("\n가격 변동 분석 결과:")
        if hasattr(price_analysis, 'text'):
            print(price_analysis.text)
        else:
            print(str(price_analysis))


if __name__ == "__main__":
    asyncio.run(main())

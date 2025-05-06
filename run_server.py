"""
Helper script to run the Upbit Candles MCP server.
This ensures that all dependencies are properly imported.
"""

import os
import sys


def main():
    """Run the MCP server with the correct Python environment"""
    # Get the absolute path to the server script
    project_path = os.path.abspath(os.path.dirname(__file__))

    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "src",
        "upbit_candles_mcp",
        "server.py",
    )

    # Print status
    print(f"Starting Upbit Candles MCP server from: {server_path}")

    # # Run the server script
    # result = subprocess.run(
    #     [
    #         sys.executable,
    #         "-m",
    #         "pip",
    #         "install",
    #         "-r",
    #         project_path + "/requirements.txt",
    #     ],
    #     check=False,
    # )
    # if result.returncode != 0:
    #     print(
    #         "Warning: Failed to install requirements. Some dependencies might be missing."
    #     )

    # Execute the server script
    os.execv(sys.executable, [sys.executable, server_path])


if __name__ == "__main__":
    main()

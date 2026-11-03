"""Kör ett Python-skript i Fusion via Fusions MCP (127.0.0.1:27182). Användning: run_in_fusion.py skript.py [--ro]"""
import sys, asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    src = open(sys.argv[1]).read()
    ro = '--ro' in sys.argv
    async with streamable_http_client('http://127.0.0.1:27182/mcp') as streams:
        r, w = streams[0], streams[1]
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool('fusion_mcp_execute', {'featureType': 'script', 'object': {'script': src, 'readOnly': ro}})
            for c in res.content:
                t = getattr(c, 'text', '')
                try:
                    print(json.loads(json.loads(t)['result'])['message'])
                except Exception:
                    print(t)

asyncio.run(main())

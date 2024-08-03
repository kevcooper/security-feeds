import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from aiohttp import ClientResponse, ClientSession

from .channel import Channel

PROJECT_ROOT: Path = Path(__file__).parent.parent
HEADERS: Dict[str, str] = {
    "User-Agent": "SecFeeds/1.0",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


async def fetch(url, session) -> Channel:
    try:
        async with session.get(url, headers=HEADERS) as resp:
            resp: ClientResponse = resp
            txt: str = await resp.text()
            return Channel.from_feed_xml(txt, str(resp.url))
    except Exception as e:
        print(f"problem with {url}", e)
        print("=" * 32)
        return Channel(
            xmlUrl=url,
            description=f"There was an error parsing this feed",
        )


async def main():
    urls: List[str] = Path(PROJECT_ROOT, "urls.txt").read_text().splitlines()
    async with ClientSession() as session:
        res = await asyncio.gather(*[fetch(url, session) for url in urls])
    res = [r for r in res if r is not None]
    json_feeds_text = json.dumps([asdict(r) for r in res], indent=2)
    Path(PROJECT_ROOT, "feeds.json").write_text(json_feeds_text)
    print(json_feeds_text)


asyncio.run(main())

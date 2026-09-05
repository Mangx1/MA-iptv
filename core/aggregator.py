import asyncio
import logging

from providers.iptv_org import get_iptv_org_channels
from providers.nexus import get_nexus_channels
from providers.free_tv import get_free_tv_channels
from providers.gnaidu import get_gnaidu_channels
from providers.vidio import get_vidio_channels

async def fetch_all_channels():
    tasks = [
        get_iptv_org_channels(),
        get_nexus_channels(),
        get_free_tv_channels(),
        get_gnaidu_channels(),
        get_vidio_channels()
    ]
    
    # Jalankan semua provider secara bersamaan
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    combined_channels = []
    for res in results:
        if isinstance(res, list):
            combined_channels.extend(res)
        elif isinstance(res, Exception):
            logging.error(f"Error pada salah satu provider: {res}")
            
    return combined_channels

async def search_channels(query: str):
    all_channels = await fetch_all_channels()
    query_clean = query.lower().strip()
    
    matched = [
        ch for ch in all_channels 
        if query_clean in ch.get("name", "").lower()
    ]
    
    return matched

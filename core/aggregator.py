import asyncio
import logging

async def fetch_all_channels():
    tasks = []

    # Provider Vidio
    try:
        from providers.vidio import get_vidio_channels
        tasks.append(get_vidio_channels())
    except ImportError as e:
        logging.warning(f"Provider Vidio gagal dimuat: {e}")

    # Provider IPTV-Org
    try:
        from providers.iptv_org import get_iptv_org_channels
        tasks.append(get_iptv_org_channels())
    except ImportError as e:
        logging.warning(f"Provider IPTV-Org gagal dimuat: {e}")

    # Provider Nexus (opsional/jika ada)
    try:
        from providers.nexus import get_nexus_channels
        tasks.append(get_nexus_channels())
    except (ImportError, AttributeError):
        pass

    # Provider Free TV (opsional/jika ada)
    try:
        from providers.free_tv import get_free_tv_channels
        tasks.append(get_free_tv_channels())
    except (ImportError, AttributeError):
        pass

    # Provider Gnaidu (opsional/jika ada)
    try:
        from providers.gnaidu import get_gnaidu_channels
        tasks.append(get_gnaidu_channels())
    except (ImportError, AttributeError):
        pass

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    combined_channels = []
    for res in results:
        if isinstance(res, list):
            combined_channels.extend(res)
        elif isinstance(res, Exception):
            logging.error(f"Error pada task provider: {res}")
            
    return combined_channels

async def search_channels(query: str):
    all_channels = await fetch_all_channels()
    query_clean = query.lower().strip()
    
    matched = [
        ch for ch in all_channels 
        if query_clean in ch.get("name", "").lower()
    ]
    
    return matched

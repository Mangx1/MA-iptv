import aiohttp
import logging

IPTV_ORG_URL = "https://iptv-org.github.io/iptv/index.m3u"

async def get_iptv_org_channels():
    channels = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(IPTV_ORG_URL, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    current_name = None
                    
                    for line in content.splitlines():
                        line = line.strip()
                        if line.startswith("#EXTINF:"):
                            parts = line.split(",", 1)
                            if len(parts) > 1:
                                current_name = parts[1].strip()
                        elif (line.startswith("http://") or line.startswith("https://")) and current_name:
                            channels.append({
                                "name": current_name,
                                "url": line,
                                "source": "IPTV-Org"
                            })
                            current_name = None
    except Exception as e:
        logging.error(f"Gagal mengambil data dari IPTV-Org: {e}")
        
    return channels

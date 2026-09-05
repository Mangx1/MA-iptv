import aiohttp
import logging

VIDIO_API_URL = "https://www.vidio.com/api/livestreamings"

async def get_vidio_channels():
    channels = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.vidio.com/"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(VIDIO_API_URL, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw_channels = data.get("data", [])
                    
                    for item in raw_channels:
                        attributes = item.get("attributes", {})
                        name = attributes.get("title") or item.get("title")
                        stream_url = attributes.get("stream_url") or item.get("stream_url")
                        
                        if not stream_url:
                            stream_url = attributes.get("share_url")

                        if name and stream_url:
                            # Menambahkan header pendukung agar URL bisa dimainkan player IPTV
                            formatted_url = f"{stream_url}|Referer=https://www.vidio.com/&User-Agent=Mozilla/5.0"
                            channels.append({
                                "name": name,
                                "url": formatted_url,
                                "source": "Vidio"
                            })
    except Exception as e:
        logging.error(f"Gagal mengambil data dari Vidio: {e}")
        
    return channels

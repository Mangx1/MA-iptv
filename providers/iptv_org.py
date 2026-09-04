import requests

API_URL = "https://iptv-org.github.io/api/streams.json"

HEADERS = {
    "User-Agent": "MA-IPTV/1.0"
}


def fetch_streams():
    r = requests.get(API_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def search(query, limit=20):
    query = query.lower().strip()

    streams = fetch_streams()
    results = []

    for item in streams:
        text = " ".join([
            str(item.get("channel", "")),
            str(item.get("feed", "")),
            str(item.get("title", "")),
            str(item.get("label", "")),
        ]).lower()

        if query in text:
            results.append({
                "source": "IPTV-Org",
                "channel": item.get("channel"),
                "feed": item.get("feed"),
                "title": item.get("title"),
                "url": item.get("url"),
                "referrer": item.get("referrer"),
                "user_agent": item.get("user_agent"),
                "quality": item.get("quality"),
                "label": item.get("label"),
            })

            if len(results) >= limit:
                break

    return results


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]).strip()

    if not query:
        print("Pemakaian: python providers/iptv_org.py BBC")
        raise SystemExit(1)

    print(f"Mencari: {query}")
    print("Mengambil database IPTV-Org...\n")

    results = search(query)

    print(f"Ditemukan: {len(results)} stream\n")

    for i, item in enumerate(results, 1):
        print(f"[{i}] {item['title'] or item['channel']}")
        print(f"    URL     : {item['url']}")
        print(f"    Quality : {item['quality']}")
        print(f"    Label   : {item['label']}")
        print()

import requests

BASE_URL = "https://dearbulut.github.io/iptv"
SEARCH_URL = f"{BASE_URL}/api/v1/search.json"

HEADERS = {
    "User-Agent": "MA-IPTV/1.0"
}


def fetch_channel(channel_id):
    url = f"{BASE_URL}/api/v1/channels/{channel_id}.json"

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    return r.json()


def normalize(text):
    if not text:
        return ""

    return " ".join(
        str(text).lower().split()
    )


def relevance(query, name):
    q = normalize(query)
    n = normalize(name)

    if not q or not n:
        return 0

    if n == q:
        return 100

    if n.startswith(q + " "):
        return 90

    if q in n:
        return 70

    q_words = q.split()
    n_words = set(n.split())

    matched = sum(
        1 for word in q_words
        if word in n_words
    )

    if matched == len(q_words):
        return 60

    if matched > 0:
        return 30

    return 0


def search(query, limit=20):
    query = query.strip()

    if not query:
        return []

    r = requests.get(
        SEARCH_URL,
        params={"q": query},
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    data = r.json()

    channels = data.get("channels", [])

    candidates = []

    for item in channels:
        if isinstance(item, dict):
            pass
        elif isinstance(item, list) and len(item) >= 2:
            item = {
                "id": item[0],
                "name": item[1]
            }
        else:
            continue

        channel_id = (
            item.get("id")
            or item.get("channel")
        )

        name = (
            item.get("name")
            or item.get("title")
            or ""
        )

        score = relevance(
            query,
            name
        )

        if score <= 0:
            continue

        candidates.append({
            "id": channel_id,
            "name": name,
            "country": item.get("country"),
            "categories": item.get("categories"),
            "relevance": score
        })

    candidates.sort(
        key=lambda x: (
            x["relevance"],
            x["name"].lower()
        ),
        reverse=True
    )

    results = []

    # Hanya ambil beberapa channel terbaik.
    # Ini mencegah channel yang kurang relevan
    # memenuhi hasil pencarian.
    for channel in candidates[:5]:

        channel_id = channel.get("id")

        if not channel_id:
            continue

        try:
            detail = fetch_channel(
                channel_id
            )
        except Exception:
            continue

        streams = detail.get(
            "streams",
            []
        )

        for stream in streams:

            health = (
                stream.get("health")
                or {}
            )

            media = (
                health.get("media")
                or {}
            )

            results.append({
                "source": "IPTV Nexus",

                "channel": channel_id,

                "name": (
                    detail.get("name")
                    or channel["name"]
                ),

                "country": (
                    detail.get("country")
                    or channel.get("country")
                ),

                "categories": (
                    detail.get("categories")
                    or channel.get("categories")
                ),

                "logo": detail.get("logo"),

                "url": stream.get("url"),

                "quality": stream.get(
                    "quality"
                ),

                "rank": stream.get(
                    "rank"
                ),

                "referrer": stream.get(
                    "referrer"
                ),

                "user_agent": stream.get(
                    "user_agent"
                ),

                "status": health.get(
                    "status"
                ),

                "score": health.get(
                    "score"
                ),

                "latency_ms": health.get(
                    "latency_ms"
                ),

                "uptime": health.get(
                    "uptime"
                ),

                "codec": media.get(
                    "video_codec"
                ),

                "nexus_relevance":
                    channel["relevance"]
            })

    # Hanya pertahankan stream yang benar-benar layak
    results = [
        x for x in results
        if x.get("url")
        and str(x.get("status", "")).lower() == "online"
        and x.get("nexus_relevance", 0) >= 60
    ]

    # Nexus sendiri sudah punya rank stream.
    # Kita prioritaskan relevance channel,
    # lalu rank/health.
    # Exact match saja untuk query utama.
    # Channel turunan seperti "BBC News Pashto"
    # tidak ikut mencampur hasil utama.
    exact = [
        x for x in results
        if normalize(x.get("name")) == normalize(query)
    ]

    if exact:
        results = exact

    results.sort(
        key=lambda x: (
            float(x.get("rank") or 0),
            float(x.get("score") or 0)
        ),
        reverse=True
    )

    return results[:limit]


if __name__ == "__main__":
    import sys

    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:
        print(
            'Pemakaian: '
            'python providers/nexus.py "BBC News"'
        )
        raise SystemExit(1)

    print(
        f"Mencari Nexus: {query}\n"
    )

    results = search(query)

    print(
        f"Ditemukan: {len(results)} stream\n"
    )

    for i, item in enumerate(
        results,
        1
    ):
        print(
            f"[{i}] "
            f"{item.get('name')}"
        )

        print(
            f"    Relevance : "
            f"{item.get('nexus_relevance')}"
        )

        print(
            f"    Quality   : "
            f"{item.get('quality')}"
        )

        print(
            f"    Status    : "
            f"{item.get('status')}"
        )

        print(
            f"    Health    : "
            f"{item.get('score')}"
        )

        print(
            f"    Rank      : "
            f"{item.get('rank')}"
        )

        print(
            f"    URL       : "
            f"{item.get('url')}"
        )

        print()

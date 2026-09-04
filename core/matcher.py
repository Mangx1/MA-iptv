import re
from urllib.parse import urlsplit, urlunsplit


def normalize_name(name):
    if not name:
        return ""

    name = str(name).lower()

    name = re.sub(
        r"\(?\b(2160p|1080p|720p|576p|540p|480p|360p|4k|uhd|hd|sd|hevc|h264|h265)\b\)?",
        " ",
        name,
        flags=re.I
    )

    name = re.sub(r"[^a-z0-9]+", " ", name)

    return re.sub(r"\s+", " ", name).strip()


def canonical_url(url):
    if not url:
        return ""

    try:
        p = urlsplit(url)

        return urlunsplit((
            p.scheme.lower(),
            p.netloc.lower(),
            p.path,
            p.query,
            ""
        ))

    except Exception:
        return str(url)


def dedupe_streams(streams):

    seen = set()
    result = []

    for stream in streams:

        url = canonical_url(stream.get("url"))

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)
        result.append(stream)

    return result


def filter_streams(streams):

    result = []

    for stream in streams:

        url = str(stream.get("url") or "").lower()
        status = str(stream.get("status") or "").lower()

        if not url.startswith(("http://", "https://")):
            continue

        if status in ("offline", "timeout"):
            continue

        result.append(stream)

    return result


def relevance_score(query, name):

    q = normalize_name(query)
    n = normalize_name(name)

    if not q or not n:
        return 0

    # EXACT
    if n == q:
        return 100

    # Nama diawali query
    if n.startswith(q + " "):
        return 90

    # Query muncul sebagai bagian nama
    if q in n:
        score = 70

        # Variasi wilayah
        regional = (
            "europe",
            "north america",
            "south america",
            "latin america",
            "asia",
            "asia pacific",
            "africa",
            "uk",
            "usa",
            "us"
        )

        if any(x in n for x in regional):
            score -= 10

        # Variasi bahasa
        languages = (
            "pashto",
            "arabic",
            "persian",
            "urdu",
            "hindi",
            "bengali"
        )

        if any(x in n for x in languages):
            score -= 20

        return score

    # Semua kata query harus ada
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


def group_channels(streams):

    groups = {}

    for stream in streams:

        name = (
            stream.get("name")
            or stream.get("title")
            or stream.get("channel")
            or "Unknown"
        )

        key = normalize_name(name)

        if not key:
            continue

        if key not in groups:

            groups[key] = {
                "name": name,
                "streams": []
            }

        groups[key]["streams"].append(stream)

    return list(groups.values())


def rank_groups(groups, query):

    for group in groups:

        group["relevance"] = relevance_score(
            query,
            group["name"]
        )

    groups.sort(
        key=lambda g: (
            g.get("relevance", 0),
            max(
                (
                    s.get("ma_score", 0)
                    for s in g.get("streams", [])
                ),
                default=0
            )
        ),
        reverse=True
    )

    return groups

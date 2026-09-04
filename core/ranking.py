def number(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def is_hls(url):
    return str(url or "").lower().split("?")[0].endswith(".m3u8")


def is_dash(url):
    return str(url or "").lower().split("?")[0].endswith(".mpd")


def quality_score(quality):
    q = str(quality or "").lower()

    if "2160" in q or "4k" in q:
        return 20

    if "1080" in q:
        return 16

    if "720" in q:
        return 11

    if "576" in q:
        return 7

    if "480" in q:
        return 4

    return 0


def calculate_score(stream):
    score = 0.0

    source = str(stream.get("source", "")).lower()
    status = str(stream.get("status", "")).lower()
    url = stream.get("url", "")

    # =========================
    # SOURCE TRUST
    # =========================

    if source == "iptv nexus":
        score += 35

    elif source == "free-tv":
        score += 28

    elif source == "freecast":
        score += 25

    elif source == "iptv-org":
        score += 15

    else:
        score += 5

    # =========================
    # HEALTH
    # =========================

    if status == "online":
        score += 30

    elif status in ("blocked", "geo-blocked"):
        score -= 5

    elif status in ("offline", "timeout"):
        score -= 30

    # =========================
    # NEXUS HEALTH SCORE
    # =========================

    health_score = number(stream.get("score"))

    if health_score > 0:
        score += health_score * 0.20

    # =========================
    # NEXUS RANK
    # =========================

    rank = number(stream.get("rank"))

    if rank > 0:
        score += rank * 0.15

    # =========================
    # UPTIME
    # =========================

    uptime = number(stream.get("uptime"))

    if uptime > 0:
        score += uptime * 0.05

    # =========================
    # QUALITY
    # =========================

    score += quality_score(stream.get("quality"))

    # =========================
    # FORMAT
    # =========================

    if is_hls(url):
        score += 8

    elif is_dash(url):
        score += 3

    # =========================
    # LATENCY
    # =========================

    latency = number(stream.get("latency_ms"))

    if latency > 0:

        if latency < 500:
            score += 10

        elif latency < 1000:
            score += 7

        elif latency < 2000:
            score += 4

        elif latency < 4000:
            score += 1

    return round(max(score, 0), 2)


def rank_streams(streams):

    for stream in streams:
        stream["ma_score"] = calculate_score(stream)

    return sorted(
        streams,
        key=lambda x: x.get("ma_score", 0),
        reverse=True
    )

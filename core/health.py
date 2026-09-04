import requests
from urllib.parse import urlsplit


HEADERS = {
    "User-Agent": "MA-IPTV/1.0"
}


def check_stream(url, timeout=8):
    if not url:
        return {
            "status": "invalid",
            "http": None,
        }

    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            stream=True,
            allow_redirects=True
        )

        content_type = (
            r.headers.get("content-type", "")
            .lower()
        )

        final_url = r.url.lower()

        if r.status_code >= 400:
            return {
                "status": "offline",
                "http": r.status_code,
                "content_type": content_type,
            }

        # HLS
        if (
            ".m3u8" in final_url
            or "mpegurl" in content_type
            or "vnd.apple.mpegurl" in content_type
        ):
            return {
                "status": "online",
                "http": r.status_code,
                "type": "hls",
                "content_type": content_type,
            }

        # DASH
        if (
            ".mpd" in final_url
            or "dash+xml" in content_type
        ):
            return {
                "status": "online",
                "http": r.status_code,
                "type": "dash",
                "content_type": content_type,
            }

        return {
            "status": "reachable",
            "http": r.status_code,
            "type": "unknown",
            "content_type": content_type,
        }

    except requests.Timeout:
        return {
            "status": "timeout",
            "http": None,
        }

    except requests.RequestException as e:
        return {
            "status": "offline",
            "http": None,
            "error": str(e),
        }


if __name__ == "__main__":
    import sys

    url = " ".join(sys.argv[1:]).strip()

    if not url:
        print("Pemakaian:")
        print("python core/health.py URL")
        raise SystemExit(1)

    print("Checking:")
    print(url)
    print()

    result = check_stream(url)

    for key, value in result.items():
        print(f"{key}: {value}")

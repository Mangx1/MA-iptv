import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from providers import iptv_org
from providers import nexus

from core.matcher import (
    dedupe_streams,
    filter_streams,
    group_channels,
    rank_groups
)

from core.ranking import rank_streams


def search(query, limit_per_provider=20):

    all_streams = []

    # =========================
    # IPTV-ORG
    # =========================

    try:

        results = iptv_org.search(
            query,
            limit=limit_per_provider
        )

        all_streams.extend(results)

        print(
            f"[IPTV-Org] {len(results)} stream"
        )

    except Exception as e:

        print(f"[IPTV-Org] ERROR: {e}")


    # =========================
    # IPTV NEXUS
    # =========================

    try:

        results = nexus.search(
            query,
            limit=limit_per_provider
        )

        all_streams.extend(results)

        print(
            f"[Nexus] {len(results)} stream"
        )

    except Exception as e:

        print(f"[Nexus] ERROR: {e}")


    # =========================
    # FILTER
    # =========================

    all_streams = filter_streams(
        all_streams
    )


    # =========================
    # DEDUPE URL
    # =========================

    all_streams = dedupe_streams(
        all_streams
    )


    # =========================
    # RANK
    # =========================

    all_streams = rank_streams(
        all_streams
    )


    return all_streams


def grouped_search(query):

    streams = search(query)

    groups = group_channels(
        streams
    )

    # Rank ulang stream dalam masing-masing
    # channel group.

    for group in groups:

        group["streams"] = rank_streams(
            group["streams"]
        )

    # Channel dengan stream terbaik di atas

    groups = rank_groups(groups, query)

    return groups


if __name__ == "__main__":

    query = " ".join(
        sys.argv[1:]
    ).strip()

    if not query:

        print(
            'Pemakaian: '
            'python core/aggregator.py "BBC News"'
        )

        raise SystemExit(1)


    print("=" * 70)
    print(
        f"MA-IPTV SEARCH: {query}"
    )
    print("=" * 70)
    print()


    groups = grouped_search(
        query
    )


    print()
    print(
        f"CHANNEL GROUP: {len(groups)}"
    )
    print()


    for i, group in enumerate(
        groups,
        1
    ):

        print(
            f"===== CHANNEL #{i} ====="
        )

        print(
            f"NAME: {group['name']}"
        )

        print(
            f"STREAMS: {len(group['streams'])}"
        )

        print()


        for j, stream in enumerate(
            group["streams"],
            1
        ):

            print(
                f"  [{j}] "
                f"{stream.get('name') or stream.get('title')}"
            )

            print(
                f"      SOURCE  : "
                f"{stream.get('source')}"
            )

            print(
                f"      QUALITY : "
                f"{stream.get('quality')}"
            )

            print(
                f"      STATUS  : "
                f"{stream.get('status')}"
            )

            print(
                f"      HEALTH  : "
                f"{stream.get('score')}"
            )

            print(
                f"      LATENCY : "
                f"{stream.get('latency_ms')}"
            )

            print(
                f"      RANK    : "
                f"{stream.get('rank')}"
            )

            print(
                f"      MA SCORE: "
                f"{stream.get('ma_score')}"
            )

            print(
                f"      URL     : "
                f"{stream.get('url')}"
            )

            print()

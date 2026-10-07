"""Build data/catalog.jsonl from the public Wikipedia movie dataset.

Source: https://github.com/prust/wikipedia-movie-data (pinned commit below).
The filter keeps US releases from 2000 to 2023 that have a usable synopsis,
at least one genre and a cast list, which gives a catalog of about 5,000 titles.

    python scripts/build_catalog.py
"""
import json
import pathlib
import urllib.parse
import urllib.request

COMMIT = "cef043a7263498604cd4b26feb84af059a950391"
URL = f"https://raw.githubusercontent.com/prust/wikipedia-movie-data/{COMMIT}/movies.json"
OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "catalog.jsonl"

MIN_YEAR = 2000
MIN_EXTRACT_WORDS = 40


def main() -> None:
    with urllib.request.urlopen(URL, timeout=120) as resp:
        movies = json.load(resp)

    seen, rows = set(), []
    for m in movies:
        extract = " ".join((m.get("extract") or "").split())
        if (
            m.get("year", 0) < MIN_YEAR
            or len(extract.split()) < MIN_EXTRACT_WORDS
            or not m.get("genres")
            or not m.get("cast")
            or not m.get("href")
            or m["href"] in seen
        ):
            continue
        seen.add(m["href"])
        rows.append(
            {
                # The Wikipedia page slug doubles as a stable, readable id.
                "id": urllib.parse.unquote(m["href"]),
                "title": m["title"],
                "year": m["year"],
                "genres": m["genres"],
                "cast": m["cast"],
                "extract": extract,
            }
        )

    rows.sort(key=lambda r: (r["year"], r["title"], r["id"]))
    with OUT.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} titles to {OUT}")


if __name__ == "__main__":
    main()

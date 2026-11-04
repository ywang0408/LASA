"""Build top-100 city tourism table from public Euromonitor 2018 (Wikipedia).

Run from repo root:
  python3 scripts/build_top100_tourism_table.py

Writes:
  data/top100_international_visitors.csv  (committed reference)
  src/lasa_pilot/top100_international_visitors.xlsx
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CSV_OUT = REPO / "data" / "top100_international_visitors.csv"
XLSX_OUT = REPO / "src" / "lasa_pilot" / "top100_international_visitors.xlsx"

# Euromonitor international arrivals 2018 — Wikipedia "List of cities by international visitors"
# https://en.wikipedia.org/wiki/List_of_cities_by_international_visitors (accessed 2025)
RAW_ROWS: list[tuple[int, str, str, int]] = [
    (1, "Hong Kong", "Hong Kong", 29262700),
    (2, "Bangkok", "Thailand", 24177500),
    (3, "London", "United Kingdom", 19233000),
    (4, "Macau", "Macau", 18931400),
    (5, "Singapore", "Singapore", 18551200),
    (6, "Paris", "France", 17560200),
    (7, "Dubai", "United Arab Emirates", 15920700),
    (8, "New York City", "United States", 13600000),
    (9, "Kuala Lumpur", "Malaysia", 13434300),
    (10, "Istanbul", "Turkey", 13433000),
    (11, "Delhi", "India", 12645300),
    (12, "Antalya", "Turkey", 12438800),
    (13, "Shenzhen", "China", 12202100),
    (14, "Mumbai", "India", 10590100),
    (15, "Phuket", "Thailand", 10550700),
    (16, "Rome", "Italy", 10065400),
    (17, "Tokyo", "Japan", 9985100),
    (18, "Pattaya", "Thailand", 9606400),
    (19, "Taipei", "Taiwan", 9597800),
    (20, "Mecca", "Saudi Arabia", 9565200),
    (21, "Guangzhou", "China", 9004800),
    (22, "Prague", "Czech Republic", 8948600),
    (23, "Medina", "Saudi Arabia", 8547200),
    (24, "Seoul", "South Korea", 8431400),
    (25, "Amsterdam", "Netherlands", 8354200),
    (26, "Agra", "India", 8138200),
    (27, "Miami", "United States", 8121300),
    (28, "Osaka", "Japan", 7861500),
    (29, "Los Angeles", "United States", 7500000),
    (30, "Shanghai", "China", 7483500),
    (31, "Ho Chi Minh City", "Vietnam", 7200000),
    (32, "Denpasar", "Indonesia", 7185600),
    (33, "Barcelona", "Spain", 6714500),
    (34, "Las Vegas", "United States", 6591300),
    (35, "Milan", "Italy", 6481300),
    (36, "Chennai", "India", 6422800),
    (37, "Vienna", "Austria", 6410300),
    (38, "Johor Bahru", "Malaysia", 6396000),
    (39, "Jaipur", "India", 6383400),
    (40, "Cancún", "Mexico", 6041000),
    (41, "Berlin", "Germany", 5959400),
    (42, "Cairo", "Egypt", 5754500),
    (43, "Athens", "Greece", 5728400),
    (44, "Orlando", "United States", 5553600),
    (45, "Moscow", "Russia", 5510000),
    (46, "Venice", "Italy", 5502500),
    (47, "Madrid", "Spain", 5440100),
    (48, "Ha Long", "Vietnam", 5294800),
    (49, "Riyadh", "Saudi Arabia", 5267500),
    (50, "Dublin", "Ireland", 5213400),
    (51, "Florence", "Italy", 5059900),
    (52, "Hanoi", "Vietnam", 4687000),
    (53, "Toronto", "Canada", 4510300),
    (54, "Johannesburg", "South Africa", 4120800),
    (55, "Sydney", "Australia", 4090600),
    (56, "Munich", "Germany", 4066600),
    (57, "Jakarta", "Indonesia", 4033000),
    (58, "Beijing", "China", 4002400),
    (59, "Saint Petersburg", "Russia", 3996000),
    (60, "Brussels", "Belgium", 3942000),
    (61, "Jerusalem", "Israel", 3930000),
    (62, "Budapest", "Hungary", 3822800),
    (63, "Lisbon", "Portugal", 3539400),
    (64, "Dammam", "Saudi Arabia", 3498900),
    (65, "Penang Island", "Malaysia", 3437100),
    (66, "Heraklion", "Greece", 3371800),
    (67, "Kyoto", "Japan", 3294200),
    (68, "Zhuhai", "China", 3259700),
    (69, "Vancouver", "Canada", 3212100),
    (70, "Chiang Mai", "Thailand", 3196000),
    (71, "Copenhagen", "Denmark", 3069700),
    (72, "San Francisco", "United States", 2901000),
    (73, "Melbourne", "Australia", 2889000),
    (74, "Krakow", "Poland", 2850000),
    (75, "Marrakesh", "Morocco", 2838100),
    (76, "Kolkata", "India", 2826500),
    (77, "Cebu City", "Philippines", 2805100),
    (78, "Auckland", "New Zealand", 2798900),
    (79, "Tel Aviv", "Israel", 2777000),
    (80, "Guilin", "China", 2747000),
    (81, "Honolulu", "United States", 2737300),
    (82, "Hurghada", "Egypt", 2735700),
    (83, "Warsaw", "Poland", 2732000),
    (84, "Muğla", "Turkey", 2723800),
    (85, "Buenos Aires", "Argentina", 2685700),
    (86, "Chiba", "Japan", 2683900),
    (87, "Frankfurt", "Germany", 2636000),
    (88, "Stockholm", "Sweden", 2604600),
    (89, "Lima", "Peru", 2535400),
    (90, "Da Nang", "Vietnam", 2505000),
    (91, "Batam", "Indonesia", 2492600),
    (92, "Nice", "France", 2466800),
    (93, "Fukuoka", "Japan", 2436900),
    (94, "Abu Dhabi", "United Arab Emirates", 2402800),
    (95, "Jeju", "South Korea", 2349200),
    (96, "Porto", "Portugal", 2341300),
    (97, "Rhodes", "Greece", 2337700),
    (98, "Rio de Janeiro", "Brazil", 2278300),
    (99, "Krabi", "Thailand", 2255300),
    (100, "Bangalore", "India", 2239200),
]

# Mastercard 2016 supplemental (hosts / hubs not in Euromonitor top 100)
SUPPLEMENTAL: list[tuple[str, str, int, str]] = [
    ("Boston", "United States", 1740000, "Mastercard Global Destinations Cities Index 2016 (Wikipedia)"),
    ("Mexico City", "Mexico", 2980000, "Mastercard 2016 (Wikipedia)"),
    ("Bogota", "Colombia", 1260000, "Mastercard 2016 (Wikipedia)"),
    ("Montreal", "Canada", 2240000, "Mastercard 2016 (Wikipedia)"),
    ("Guadalajara", "Mexico", 0, "Not in top 100; placeholder — replace if LASA provides a figure"),
    ("Guatemala City", "Guatemala", 0, "Not in top 100; placeholder — replace if LASA provides a figure"),
]

SOURCE_NOTE = (
    "Euromonitor international arrivals 2018 via Wikipedia "
    "List_of_cities_by_international_visitors. "
    "Supplemental rows for select LASA-relevant cities from Mastercard 2016 where noted."
)


def model_city_key(city: str) -> str:
    return " ".join(city.strip().split())


def main() -> None:
    top100 = pd.DataFrame(
        RAW_ROWS,
        columns=["rank_euromonitor_2018", "city", "country", "international_arrivals"],
    )
    top100["model_city_key"] = top100["city"].map(model_city_key)
    top100["data_source"] = "Euromonitor 2018 (Wikipedia)"

    supp = pd.DataFrame(
        [
            {
                "rank_euromonitor_2018": None,
                "city": city,
                "country": country,
                "international_arrivals": arrivals,
                "model_city_key": model_city_key(city),
                "data_source": source,
            }
            for city, country, arrivals, source in SUPPLEMENTAL
        ]
    )

    combined = pd.concat([top100, supp], ignore_index=True)
    combined = combined.drop_duplicates(subset=["model_city_key"], keep="first")

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(CSV_OUT, index=False)

    meta = pd.DataFrame({"field": ["description", "source"], "value": [SOURCE_NOTE, CSV_OUT.name]})
    XLSX_OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(XLSX_OUT, engine="openpyxl") as writer:
        meta.to_excel(writer, sheet_name="README", index=False)
        top100.to_excel(writer, sheet_name="top100_euromonitor_2018", index=False)
        supp.to_excel(writer, sheet_name="supplemental_cities", index=False)
        combined.to_excel(writer, sheet_name="lookup_combined", index=False)

    print("Wrote", CSV_OUT)
    print("Wrote", XLSX_OUT)


if __name__ == "__main__":
    main()

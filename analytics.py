
import os
import re
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "search_logs.txt")

CHART_FILE = os.path.join(BASE_DIR, "search_analytics.png")
ZIPF_FILE = os.path.join(BASE_DIR, "zipf_chart.png")

# Read the search history
if not os.path.exists(LOG_FILE):
    print("No search history found. Search on the website first.")
    raise SystemExit

with open(LOG_FILE, "r", encoding="utf-8") as file:
    searches = [
        line.strip().lower()
        for line in file
        if line.strip()
    ]

if not searches:
    print("No search terms available yet.")
    raise SystemExit

# Count words across all search queries
word_counts = Counter()

for search in searches:
    words = re.findall(r"\b[\w'-]+\b", search)
    word_counts.update(words)

if not word_counts:
    print("No searchable words found.")
    raise SystemExit

popular = word_counts.most_common(10)

terms = [word for word, count in popular]
counts = [count for word, count in popular]
ranks = list(range(1, len(popular) + 1))

# Chart 1: Most popular search terms
fig, ax = plt.subplots(figsize=(10, 5))

ax.barh(terms[::-1], counts[::-1])
ax.set_title("Top Search Terms", fontsize=15, pad=14)
ax.set_xlabel("Number of Occurrences")
ax.set_ylabel("Search Term")
ax.grid(axis="x", linestyle="--", alpha=0.3)
ax.set_axisbelow(True)

fig.tight_layout()
fig.savefig(CHART_FILE, dpi=160, bbox_inches="tight")
plt.close(fig)

# Chart 2: Frequency by rank (Zipf-style)
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(ranks, counts, marker="o", linewidth=2, label="Observed frequency")

# Reference curve: frequency proportional to 1 / rank
if counts:
    reference = [counts[0] / rank for rank in ranks]
    ax.plot(
        ranks,
        reference,
        linestyle="--",
        linewidth=1.5,
        label="1 / rank reference"
    )

ax.set_title("Search Frequency by Rank", fontsize=15, pad=14)
ax.set_xlabel("Rank (most frequent first)")
ax.set_ylabel("Number of Occurrences")
ax.set_xticks(ranks)
ax.grid(True, linestyle="--", alpha=0.3)
ax.legend()

fig.tight_layout()
fig.savefig(ZIPF_FILE, dpi=160, bbox_inches="tight")
plt.close(fig)

# Print dashboard metrics in the terminal
total_queries = len(searches)
unique_terms = len(word_counts)
top_term, top_count = popular[0]

print("\nSEARCH ANALYTICS SUMMARY")
print("-" * 32)
print(f"Total queries: {total_queries}")
print(f"Unique search terms: {unique_terms}")
print(f"Most popular term: {top_term} ({top_count} occurrences)")

print("\nTop 10 Search Terms:")
for rank, (word, count) in enumerate(popular, start=1):
    print(f"{rank}. {word}: {count}")

print("\nCharts updated successfully:")
print("- search_analytics.png")
print("- zipf_chart.png")


import os
import subprocess
import sys
import re
import time
from collections import Counter
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
def update_analytics_charts():
    try:
        subprocess.run(
            [sys.executable, "analytics.py"],
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as error:
        print("Analytics update failed:")
        print(error.stderr)
@app.route("/search_analytics.png")
def search_analytics_image():
    return send_from_directory(".", "search_analytics.png")


@app.route("/zipf_chart.png")
def zipf_chart_image():
    return send_from_directory(".", "zipf_chart.png")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")

documents = {}
inverted_index = {}
document_words = {}

def tokenize(text):
    return re.findall(r"\b[a-z0-9]+\b", text.lower())

def build_index():
    documents.clear()
    inverted_index.clear()
    document_words.clear()

    if not os.path.isdir(DOCUMENTS_DIR):
        return

    for filename in os.listdir(DOCUMENTS_DIR):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(DOCUMENTS_DIR, filename)

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        words = tokenize(content)
        documents[filename] = content
        document_words[filename] = Counter(words)

        for word in set(words):
            inverted_index.setdefault(word, set()).add(filename)

def search_documents(query):
    start_time = time.perf_counter()
    stop_words = {"a", "an", "the", "with", "and", "or", "is", "for"}
    query_words = [
        word for word in tokenize(query)
        if word not in stop_words
    ]

    scores = {}

    for word in query_words:
        for filename in inverted_index.get(word, set()):
            scores[filename] = (
                scores.get(filename, 0)
                + document_words[filename][word]
            )

    ranked = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0])
    )

    results = []

    for filename, score in ranked:
        content = documents[filename]
        title = content.strip().splitlines()[0] if content.strip() else filename

        results.append({
            "title": title,
            "filename": filename,
            "score": score,
            "snippet": " ".join(content.split())[:120]
        })

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "query": query,
        "total_results": len(results),
        "search_time_ms": round(elapsed_ms, 3),
        "results": results
    }

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Please enter a search term."
        }), 400

    log_path = os.path.join(BASE_DIR, "search_logs.txt")

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(query + "\n")

    update_analytics_charts()

    return jsonify(search_documents(query))
@app.route("/api/reindex", methods=["POST"])
def reindex():
    build_index()

    return jsonify({
        "message": "Search index rebuilt successfully.",
        "total_documents": len(documents),
        "unique_terms": len(inverted_index)
    })

@app.route("/api/stats")
def stats():
    log_path = os.path.join(BASE_DIR, "search_logs.txt")

    total_searches = 0

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as log_file:
            total_searches = sum(
                1 for line in log_file if line.strip()
            )

    return jsonify({
        "total_documents": len(documents),
        "unique_terms": len(inverted_index),
        "total_searches": total_searches
    })



@app.route("/api/analytics")
def analytics():
    log_path = os.path.join(BASE_DIR, "search_logs.txt")
    search_counts = Counter()
    total_queries = 0

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as log_file:
            for line in log_file:
                query = line.strip()

                if not query:
                    continue

                total_queries += 1
                search_counts.update(tokenize(query))

    top_terms = [
        {"term": word, "count": count}
        for word, count in search_counts.most_common(10)
    ]

    most_popular = top_terms[0] if top_terms else None

    return jsonify({
        "total_searches": total_queries,
        "unique_terms": len(search_counts),
        "most_popular_term": most_popular,
        "top_terms": top_terms,
        "total_documents": len(documents)
    })


if __name__ == "__main__":
    build_index()
    print(f"Indexed {len(documents)} documents.")
    app.run(debug=True)

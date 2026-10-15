
# import os

# folder = "documents"

# for filename in os.listdir(folder):
#     file_path = os.path.join(folder, filename)

#     with open(file_path, "r", encoding="utf-8") as file:
#         content = file.read()

#     print("File:", filename)
#     print("Content:", content)
#     print("-" * 30)

# import os

# folder = "documents"
# inverted_index = {}

# for filename in os.listdir(folder):
#     if not filename.endswith(".txt"):
#         continue

#     file_path = os.path.join(folder, filename)

#     with open(file_path, "r", encoding="utf-8") as file:
#         content = file.read().lower()

#     words = content.split()

#     for word in words:
#         word = word.strip(".,!?():;\"'")

#         if word == "":
#             continue

#         if word not in inverted_index:
#             inverted_index[word] = []

#         if filename not in inverted_index[word]:
#             inverted_index[word].append(filename)

# print("INVERTED INDEX")
# print("-" * 30)

# for word, files in sorted(inverted_index.items()):
#     print(word, "->", files)

# import os

# folder = "documents"
# inverted_index = {}

# for filename in os.listdir(folder):
#     if not filename.endswith(".txt"):
#         continue

#     path = os.path.join(folder, filename)

#     with open(path, "r", encoding="utf-8") as file:
#         content = file.read().lower()

#     for word in content.split():
#         word = word.strip(".,!?():;\"'")

#         if word:
#             if word not in inverted_index:
#                 inverted_index[word] = []

#             if filename not in inverted_index[word]:
#                 inverted_index[word].append(filename)

# query = input("Search for a product: ").lower().strip()

# words = query.split()
# results = set()

# for word in words:
#     word = word.strip(".,!?():;\"'")

#     if word in inverted_index:
#         results.update(inverted_index[word])

# if results:
#     print("\nMatching documents:")

#     for filename in sorted(results):
#         print("-", filename)
# else:
#     print("No matching documents found.")

# import os
# from collections import Counter

# folder = "documents"
# inverted_index = {}
# document_words = {}

# for filename in os.listdir(folder):
#     if not filename.endswith(".txt"):
#         continue

#     path = os.path.join(folder, filename)

#     with open(path, "r", encoding="utf-8") as file:
#         content = file.read().lower()

#     words = [
#         word.strip(".,!?():;\"'")
#         for word in content.split()
#     ]
#     words = [word for word in words if word]

#     document_words[filename] = Counter(words)

#     for word in set(words):
#         inverted_index.setdefault(word, set()).add(filename)

# query = input("Search for a product: ").lower().strip()
# query_words = query.split()
# scores = {}

# for word in query_words:
#     word = word.strip(".,!?():;\"'")

#     for filename in inverted_index.get(word, set()):
#         scores[filename] = (
#             scores.get(filename, 0)
#             + document_words[filename][word]
#         )

# ranked_results = sorted(
#     scores.items(),
#     key=lambda item: (-item[1], item[0])
# )

# if ranked_results:
#     print("\nRanked results:")

#     for filename, score in ranked_results:
#         print(f"{filename} | Score: {score}")
# else:
#     print("No matching documents found.")


import os
import time
from collections import Counter

folder = "documents"
inverted_index = {}
document_words = {}
document_content = {}

# Load documents and build the inverted index
for filename in os.listdir(folder):
    if not filename.endswith(".txt"):
        continue

    path = os.path.join(folder, filename)

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    document_content[filename] = content

    words = [
        word.strip(".,!?():;\"'").lower()
        for word in content.split()
    ]
    words = [word for word in words if word]

    document_words[filename] = Counter(words)

    for word in set(words):
        inverted_index.setdefault(word, set()).add(filename)

# Display index statistics
print(f"Documents indexed: {len(document_content)}")
print(f"Unique terms indexed: {len(inverted_index)}")

stop_words = {"a", "an", "the", "with", "and", "or", "is", "for"}

# Continuous search loop
while True:
    query = input(
        "\nSearch for a product (or type 'exit'): "
    ).lower().strip()

    if query == "exit":
        print("Search engine closed.")
        break

    if not query:
        print("Please enter a search term.")
        continue

    # Save search history
    with open("search_logs.txt", "a", encoding="utf-8") as log_file:
        log_file.write(query + "\n")

    # Clean query
    query_words = [
        word.strip(".,!?():;\"'").lower()
        for word in query.split()
    ]
    query_words = [
        word for word in query_words
        if word and word not in stop_words
    ]

    if not query_words:
        print("Please enter a meaningful search term.")
        continue

    # Measure search time
    start_time = time.perf_counter()

    # Calculate relevance scores
    scores = {}

    for word in query_words:
        for filename in inverted_index.get(word, set()):
            scores[filename] = (
                scores.get(filename, 0)
                + document_words[filename][word]
            )

    # Filter and rank results
    min_score = 1
    scores = {
        filename: score
        for filename, score in scores.items()
        if score >= min_score
    }

    ranked_results = sorted(
        scores.items(),
        key=lambda item: (-item[1], item[0])
    )

    end_time = time.perf_counter()
    search_time = (end_time - start_time) * 1000

    print(f"\nSearch time: {search_time:.3f} ms")
    print(f"Total results found: {len(ranked_results)}")

    if ranked_results:
        print("\nRanked search results:")

        for filename, score in ranked_results:
            content = document_content[filename]
            snippet = " ".join(content.split())[:120]

            title = content.strip().split("\n")[0]

            print(f"\nTitle: {title}")
            print(f"Document: {filename}")
            print(f"Relevance Score: {score}")
            print(f"Snippet: {snippet}")
            print("-" * 40)
    else:
        print("No matching documents found.")

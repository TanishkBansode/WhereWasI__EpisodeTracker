from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import csv
import numpy as np
from collections import Counter
import re
import nltk

nltk.download("wordnet")
nltk.download("stopwords")


def cosine_similarity(vector1, vector2):
    intersection = set(vector1.keys()) & set(vector2.keys())
    dot_product = sum(vector1[x] * vector2[x] for x in intersection)
    magnitude1 = np.sqrt(sum(vector1[x] ** 2 for x in vector1.keys()))
    magnitude2 = np.sqrt(sum(vector2[x] ** 2 for x in vector2.keys()))
    if not magnitude1 or not magnitude2:
        return 0
    return dot_product / (magnitude1 * magnitude2)


def preprocess_text(text):
    
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    
    words = text.split()

    
    stop_words = {
        "the",
        "and",
        "in",
        "of",
        "to",
        "is",
        "a",
        "with",
        "on",
        "as",
        "for",
        "at",
    }
    words = [w for w in words if w not in stop_words]

    
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w) for w in words]

    
    return " ".join(words)


def get_episode_data(filename):
    
    with open(filename, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        episodes = []
        for row in reader:
            episode_data = {}
            episode_data["episode_number"] = int(row["Episode No."])
            episode_data["episode_name"] = preprocess_text(row["Episode Name"])
            episode_data["plot"] = preprocess_text(row["Plot"])
            episode_data["characters"] = preprocess_text(row["Characters Appeared"])
            episode_data["characters"] = episode_data["characters"].split(", ")
            episodes.append(episode_data)
    return episodes


def get_query_vector(query, vocabulary):
    
    words = preprocess_text(query).split()
    word_counts = Counter(words)
    query_vector = {}
    for word in vocabulary:
        query_vector[word] = word_counts.get(word, 0)
    return query_vector


def get_corpus_vectors(episodes, vocabulary):
    
    corpus_vectors = {}
    for episode in episodes:
        episode_number = episode["episode_number"]
        corpus_vectors[episode_number] = {}
        for word in vocabulary:
            corpus_vectors[episode_number][word] = episode["plot"].count(word)
    return corpus_vectors


def search_episodes(query, episodes, vocabulary):
    
    query_vector = get_query_vector(query, vocabulary)
    corpus_vectors = get_corpus_vectors(episodes, vocabulary)
    similarities = {}
    for episode in episodes:
        episode_number = episode["episode_number"]
        episode_name = episode["episode_name"]
        corpus_vector = corpus_vectors[episode_number]
        similarity = cosine_similarity(query_vector, corpus_vector)
        similarities[episode_number] = (episode_name, similarity)
    
    return sorted(similarities.items(), key=lambda x: x[1][1], reverse=True)


episodes = get_episode_data("demon_slayer.csv")
vocabulary = set(word for episode in episodes for word in episode["plot"].split())
results = search_episodes("Zenitsu fights while sleeping", episodes, vocabulary)
for episode_number, (episode_name, similarity) in results:
    print(f"Episode {episode_number}: {episode_name} (similarity {similarity:.2f})")

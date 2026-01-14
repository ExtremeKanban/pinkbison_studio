import faiss
import numpy as np
import requests
import os
import json


class MemoryStore:
    """
    Optimized hybrid memory architecture:
    - Stores text in JSON
    - Stores embeddings in embeddings.npy
    - Rebuilds FAISS index from stored embeddings (fast)
    - Never re-embeds text except when adding new memory
    """

    def __init__(self, project_name: str = "default_project", dim: int = 384):
        self.project_name = project_name
        self.dim = dim

        # Project-specific paths
        self.index_path = f"{project_name}_memory.index"
        self.texts_path = f"{project_name}_memory_texts.json"
        self.embeddings_path = f"{project_name}_embeddings.npy"

        # Load or initialize text store
        if os.path.exists(self.texts_path):
            with open(self.texts_path, "r", encoding="utf-8") as f:
                self.text_store = json.load(f)
        else:
            self.text_store = []

        # Load or initialize embeddings
        if os.path.exists(self.embeddings_path):
            self.embeddings = np.load(self.embeddings_path)
        else:
            self.embeddings = np.zeros((0, dim), dtype="float32")

        # Load or create FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(dim)
            if len(self.embeddings) > 0:
                self.index.add(self.embeddings)

    # ---------------------------------------------------------
    # Embedding function (only used when adding new memory)
    # ---------------------------------------------------------
    def embed(self, text: str) -> np.ndarray:
        url = "http://localhost:8001/v1/embeddings"
        payload = {
            "input": text,
            "model": "BAAI/bge-small-en-v1.5"
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if "data" not in data:
            raise ValueError(f"Embedding server error: {data}")

        return np.array(data["data"][0]["embedding"], dtype="float32")

    # ---------------------------------------------------------
    # Add memory (fast)
    # ---------------------------------------------------------
    def add(self, text: str) -> None:
        embedding = self.embed(text)

        # Append text
        self.text_store.append(text)

        # Append embedding
        self.embeddings = np.vstack([self.embeddings, embedding])

        # Add to FAISS index
        self.index.add(np.array([embedding]))

        self.save()

    # ---------------------------------------------------------
    # Search memory (deduped)
    # ---------------------------------------------------------
    def search(self, query: str, k: int = 5) -> list[str]:
        if len(self.text_store) == 0:
            return []

        query_emb = self.embed(query)
        distances, indices = self.index.search(np.array([query_emb]), k)

        seen = set()
        results = []

        for idx in indices[0]:
            if idx < len(self.text_store) and idx not in seen:
                seen.add(idx)
                results.append(self.text_store[idx])

        return results

    # ---------------------------------------------------------
    # Return all memory entries
    # ---------------------------------------------------------
    def get_all(self) -> list[tuple[int, str]]:
        return list(enumerate(self.text_store))

    # ---------------------------------------------------------
    # Delete memory (instant)
    # ---------------------------------------------------------
    def delete(self, idx: int) -> None:
        if idx < 0 or idx >= len(self.text_store):
            raise IndexError("Memory index out of range.")

        # Remove text
        del self.text_store[idx]

        # Only delete embedding if embeddings exist
        if len(self.embeddings) > 0:
            if idx < len(self.embeddings):
                self.embeddings = np.delete(self.embeddings, idx, axis=0)
            else:
                # Embeddings are out of sync — rebuild safely
                self.embeddings = np.zeros((0, self.dim), dtype="float32")

        # Rebuild FAISS index from stored embeddings
        self.index = faiss.IndexFlatL2(self.dim)
        if len(self.embeddings) > 0:
            self.index.add(self.embeddings)

        self.save()


    # ---------------------------------------------------------
    # Clear memory (instant)
    # ---------------------------------------------------------
    def clear(self) -> None:
        self.text_store = []
        self.embeddings = np.zeros((0, self.dim), dtype="float32")
        self.index = faiss.IndexFlatL2(self.dim)
        self.save()

    # ---------------------------------------------------------
    # Save everything
    # ---------------------------------------------------------
    def save(self) -> None:
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)

        # Save texts
        with open(self.texts_path, "w", encoding="utf-8") as f:
            json.dump(self.text_store, f, ensure_ascii=False, indent=2)

        # Save embeddings
        np.save(self.embeddings_path, self.embeddings)

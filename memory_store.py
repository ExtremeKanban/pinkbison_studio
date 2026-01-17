"""
Memory store with unified storage paths.
"""

import faiss
import numpy as np
import requests
import json
import shutil
from pathlib import Path
from config.settings import MODEL_CONFIG
from core.storage_paths import ProjectPaths, LegacyPaths


class MemoryStore:
    """
    Optimized hybrid memory architecture with unified storage.
    
    Storage location: project_state/<project>/memory/
    - index.faiss
    - texts.json
    - embeddings.npy
    """

    def __init__(self, project_name: str = "default_project", dim: int = 384):
        self.project_name = project_name
        self.dim = dim
        self.embeddings_url = MODEL_CONFIG.embeddings_url
        self.embeddings_model = MODEL_CONFIG.embeddings_model

        # Get unified paths
        self.paths = ProjectPaths.for_project(project_name)
        self.paths.ensure_directories()
        
        # Migrate from legacy location if needed
        self._migrate_from_legacy()
        
        # Use new unified paths
        self.index_path = str(self.paths.memory_index)
        self.texts_path = str(self.paths.memory_texts)
        self.embeddings_path = str(self.paths.memory_embeddings)

        # Load or initialize text store
        if Path(self.texts_path).exists():
            with open(self.texts_path, "r", encoding="utf-8") as f:
                self.text_store = json.load(f)
        else:
            self.text_store = []

        # Load or initialize embeddings
        if Path(self.embeddings_path).exists():
            self.embeddings = np.load(self.embeddings_path)
        else:
            self.embeddings = np.zeros((0, dim), dtype="float32")

        # Load or create FAISS index
        if Path(self.index_path).exists():
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(dim)
            if len(self.embeddings) > 0:
                self.index.add(self.embeddings)

    def _migrate_from_legacy(self) -> None:
            """
            Migrate memory files from legacy locations to unified structure.
            
            Legacy locations:
            - project_root/PROJECT_memory.index
            - project_root/PROJECT_memory_texts.json
            - project_root/PROJECT_embeddings.npy
            
            New location:
            - project_state/PROJECT/memory/
            """
            legacy_index = LegacyPaths.memory_index(self.project_name)
            legacy_texts = LegacyPaths.memory_texts(self.project_name)
            legacy_embeddings = LegacyPaths.memory_embeddings(self.project_name)
            
            # Check if migration needed
            if not legacy_index.exists():
                return  # No legacy files to migrate
            
            # Check if already migrated
            if self.paths.memory_index.exists():
                return  # Already in new location
            
            print(f"[MemoryStore] Migrating {self.project_name} memory to unified storage...")
            
            # Copy files to new location
            if legacy_index.exists():
                shutil.copy2(legacy_index, self.paths.memory_index)
                print(f"  ✓ Migrated index: {legacy_index} → {self.paths.memory_index}")
            
            if legacy_texts.exists():
                shutil.copy2(legacy_texts, self.paths.memory_texts)
                print(f"  ✓ Migrated texts: {legacy_texts} → {self.paths.memory_texts}")
            
            if legacy_embeddings.exists():
                shutil.copy2(legacy_embeddings, self.paths.memory_embeddings)
                print(f"  ✓ Migrated embeddings: {legacy_embeddings} → {self.paths.memory_embeddings}")
            
            print(f"[MemoryStore] Migration complete for {self.project_name}")

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding using configured embeddings server"""
        payload = {
            "input": text,
            "model": self.embeddings_model
        }

        response = requests.post(self.embeddings_url, json=payload)
        data = response.json()

        if "data" not in data:
            raise ValueError(f"Embedding server error: {data}")

        return np.array(data["data"][0]["embedding"], dtype="float32")

    def add(self, text: str) -> None:
        """Add text to memory with embedding"""
        embedding = self.embed(text)

        # Append text
        self.text_store.append(text)

        # Append embedding
        self.embeddings = np.vstack([self.embeddings, embedding])

        # Add to FAISS index
        self.index.add(np.array([embedding]))

        self.save()

    def search(self, query: str, k: int = 5) -> list[str]:
        """Search memory with deduplication"""
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

    def get_all(self) -> list[tuple[int, str]]:
        """Return all memory entries with indices"""
        return list(enumerate(self.text_store))

    def delete(self, idx: int) -> None:
        """Delete memory entry and rebuild index"""
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

    def clear(self) -> None:
        """Clear all memory"""
        self.text_store = []
        self.embeddings = np.zeros((0, self.dim), dtype="float32")
        self.index = faiss.IndexFlatL2(self.dim)
        self.save()

    def save(self) -> None:
        """Save all memory components to unified location"""
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)

        # Save texts
        with open(self.texts_path, "w", encoding="utf-8") as f:
            json.dump(self.text_store, f, ensure_ascii=False, indent=2)

        # Save embeddings
        np.save(self.embeddings_path, self.embeddings)
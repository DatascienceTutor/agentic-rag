import json
import math
import hashlib
from typing import List, Dict, Any
from collections import Counter

class CustomBM25Encoder:
    """
    A pure Python implementation of a BM25 encoder for Pinecone that avoids C++ dependencies.
    """
    def __init__(self, b: float = 0.75, k1: float = 1.2):
        self.b = b
        self.k1 = k1
        self.doc_freqs: Dict[int, int] = {}
        self.idf: Dict[int, float] = {}
        self.doc_len: List[int] = []
        self.avgdl: float = 0
        self.N: int = 0

    def _hash_term(self, term: str) -> int:
        """Hashes a string term into a stable 32-bit unsigned integer (Pinecone requirement)."""
        # Pinecone requires unsigned 32-bit integers for indices
        hash_bytes = hashlib.md5(term.encode('utf-8')).digest()
        return int.from_bytes(hash_bytes[:4], byteorder='big')

    def _tokenize(self, text: str) -> List[int]:
        # Simple whitespace/punctuation tokenizer
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return [self._hash_term(t) for t in tokens]

    def fit(self, corpus: List[str]):
        """Trains the BM25 model on the provided corpus."""
        self.N = len(corpus)
        total_len = 0
        
        for text in corpus:
            tokens = self._tokenize(text)
            self.doc_len.append(len(tokens))
            total_len += len(tokens)
            
            # Count document frequencies
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                
        self.avgdl = total_len / self.N if self.N > 0 else 0
        
        # Calculate IDF
        for token, freq in self.doc_freqs.items():
            # Standard BM25 IDF formulation
            idf = math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))
            self.idf[token] = idf

    def encode_queries(self, queries: str) -> Dict[str, Any]:
        """Encodes a single query string into Pinecone sparse vector format."""
        if isinstance(queries, list):
            queries = queries[0] # LangChain might pass a list
            
        tokens = self._tokenize(queries)
        counts = Counter(tokens)
        
        indices = []
        values = []
        
        for token, count in counts.items():
            if token in self.idf:
                # Query term weight (simplified)
                weight = count * self.idf[token]
                indices.append(token)
                values.append(weight)
                
        return {"indices": indices, "values": values}

    def encode_documents(self, documents: str) -> Dict[str, Any]:
        """Encodes a document string into Pinecone sparse vector format."""
        if isinstance(documents, list):
            documents = documents[0]
            
        tokens = self._tokenize(documents)
        counts = Counter(tokens)
        
        indices = []
        values = []
        
        doc_len = len(tokens)
        
        for token, count in counts.items():
            if token in self.idf:
                # Standard BM25 term weighting
                term_weight = self.idf[token] * (count * (self.k1 + 1)) / (count + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl))
                indices.append(token)
                values.append(term_weight)
                
        return {"indices": indices, "values": values}

    def dump(self, path: str):
        """Saves the trained model to disk."""
        data = {
            "b": self.b,
            "k1": self.k1,
            "doc_freqs": self.doc_freqs,
            "idf": self.idf,
            "doc_len": self.doc_len,
            "avgdl": self.avgdl,
            "N": self.N
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path: str):
        """Loads a trained model from disk."""
        with open(path, 'r') as f:
            data = json.load(f)
            
        self.b = data["b"]
        self.k1 = data["k1"]
        # JSON converts int keys to strings, need to convert back
        self.doc_freqs = {int(k): v for k, v in data["doc_freqs"].items()}
        self.idf = {int(k): v for k, v in data["idf"].items()}
        self.doc_len = data["doc_len"]
        self.avgdl = data["avgdl"]
        self.N = data["N"]
        return self

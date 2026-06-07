from __future__ import annotations

from app.embeddings.local_hash_provider import LocalHashEmbeddingProvider



def test_local_hash_embedding_is_deterministic() -> None:
    provider = LocalHashEmbeddingProvider(dimension=16)

    first = provider.embed_text("September 194J short deposit")
    second = provider.embed_text("September 194J short deposit")

    assert first == second
    assert len(first) == 16



def test_local_hash_embedding_handles_blank_text() -> None:
    provider = LocalHashEmbeddingProvider(dimension=8)

    vector = provider.embed_text("   ")

    assert len(vector) == 8
    assert all(value == 0.0 for value in vector)



def test_local_hash_embedding_batch_shape() -> None:
    provider = LocalHashEmbeddingProvider(dimension=12)

    vectors = provider.embed_batch(["missing PAN", "short deposit", ""])

    assert len(vectors) == 3
    assert all(len(vector) == 12 for vector in vectors)

"""Integration tests — RAG chatbot (Week 8 · Day 3)."""

from __future__ import annotations


SAMPLE_NOTES = b"""
# Machine Learning Notes
Recursion is when a function calls itself with a smaller subproblem.
Base case stops the recursion. Merge sort uses divide and conquer.
Neural networks learn weights via backpropagation and gradient descent.
"""


def test_upload_list_and_chat(client):
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", SAMPLE_NOTES, "text/plain")},
    )
    assert upload.status_code == 200
    doc = upload.json()
    doc_id = doc["document"]["document_id"]
    assert doc_id
    assert doc["document"]["num_chunks"] >= 1

    listing = client.get("/api/documents")
    assert listing.status_code == 200
    ids = [d["document_id"] for d in listing.json()["documents"]]
    assert doc_id in ids

    chat = client.post(
        "/api/documents/chat",
        json={
            "question": "What is recursion?",
            "document_id": doc_id,
        },
    )
    assert chat.status_code == 200
    answer = chat.json()
    assert answer.get("answer")
    assert len(answer["answer"]) > 0


def test_search_documents(client):
    client.post(
        "/api/documents/upload",
        files={"file": ("ml.txt", b"Gradient descent optimizes loss functions.", "text/plain")},
    )
    search = client.get("/api/documents/search", params={"q": "gradient descent"})
    assert search.status_code == 200
    assert "results" in search.json()

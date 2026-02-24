import asyncio
import os
import sys
import tempfile
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_settings():
    s = MagicMock()
    s.azure_search_endpoint = "https://test.search.windows.net"
    s.azure_search_key = "test-key"
    s.azure_search_index = "test-index"
    s.azure_openai_api_key = "test-key"
    s.azure_openai_endpoint = "https://test.openai.azure.com"
    s.azure_openai_api_version = "2024-12-01-preview"
    s.azure_openai_embedding_deployment = "text-embedding-3-small"
    return s


def make_search_result(content, source, domain, score=0.9):
    return {"content": content, "source": source, "domain": domain, "@search.score": score}


@contextmanager
def rag_patches(mock_client):
    with patch("tools.rag_tool.get_settings", return_value=make_settings()), \
         patch("tools.rag_tool.SearchClient", return_value=mock_client), \
         patch("tools.rag_tool.AzureKeyCredential"):
        from tools.rag_tool import RAGTool
        yield RAGTool


def make_builder(mock_openai=None, mock_search=None):
    with patch("tools.index_builder.get_settings", return_value=make_settings()), \
         patch("tools.index_builder.SearchIndexClient"), \
         patch("tools.index_builder.SearchClient", return_value=mock_search or MagicMock()), \
         patch("tools.index_builder.AzureKeyCredential"), \
         patch("tools.index_builder.AzureOpenAI", return_value=mock_openai or MagicMock()):
        from tools.index_builder import IndexBuilder
        return IndexBuilder()


def temp_md(content, suffix=".md"):
    f = tempfile.NamedTemporaryFile(suffix=suffix, mode="w", delete=False)
    f.write(content)
    f.close()
    return f.name


def run(coro):
    return asyncio.run(coro)


# ── RAGTool ───────────────────────────────────────────────────────────────────

def test_retrieve_returns_list():
    mock_client = MagicMock()
    mock_client.search.return_value = [make_search_result("Refunds in 5-7 days.", "billing.md", "billing")]
    with rag_patches(mock_client) as RAGTool:
        assert isinstance(run(RAGTool().retrieve("refund policy")), list)


def test_retrieve_result_has_required_keys():
    mock_client = MagicMock()
    mock_client.search.return_value = [make_search_result("Refunds in 5-7 days.", "billing.md", "billing")]
    with rag_patches(mock_client) as RAGTool:
        results = run(RAGTool().retrieve("refund policy"))
    assert results
    for r in results:
        assert {"content", "source", "domain", "score"} <= r.keys()


def test_retrieve_calls_search():
    mock_client = MagicMock()
    mock_client.search.return_value = []
    with rag_patches(mock_client) as RAGTool:
        run(RAGTool().retrieve("test query"))
    mock_client.search.assert_called_once()


def test_retrieve_domain_filter():
    mock_client = MagicMock()
    mock_client.search.return_value = []
    with rag_patches(mock_client) as RAGTool:
        run(RAGTool(domain="billing").retrieve("refund policy"))
    assert "billing" in str(mock_client.search.call_args[1].get("filter", ""))


def test_retrieve_no_filter_without_domain():
    mock_client = MagicMock()
    mock_client.search.return_value = []
    with rag_patches(mock_client) as RAGTool:
        run(RAGTool().retrieve("general question"))
    assert mock_client.search.call_args[1].get("filter") is None


def test_retrieve_top_k():
    mock_client = MagicMock()
    mock_client.search.return_value = []
    with rag_patches(mock_client) as RAGTool:
        run(RAGTool().retrieve("test", top_k=3))
    assert mock_client.search.call_args[1].get("top") == 3


@pytest.mark.parametrize("query,domain", [
    ("What is the refund policy?", "billing"),
    ("How do I fix a 429 error?", "technical"),
    ("How do I enable 2FA?", "account"),
    ("What platforms do you support?", "general"),
])
def test_retrieval_per_domain(query, domain):
    mock_client = MagicMock()
    mock_client.search.return_value = [make_search_result(f"Answer about {domain}.", f"{domain}.md", domain)]
    with rag_patches(mock_client) as RAGTool:
        results = run(RAGTool(domain=domain).retrieve(query))
    assert results and results[0]["domain"] == domain


# ── IndexBuilder ──────────────────────────────────────────────────────────────

def test_chunk_document_headers():
    path = temp_md("## Refund Policy\nRefunds in 5-7 days.\n\n## Payment Methods\nVisa and Mastercard.", "_billing.md")
    try:
        docs = make_builder().chunk_document(path)
        titles = [d["title"] for d in docs]
        assert len(docs) == 2
        assert "Refund Policy" in titles and "Payment Methods" in titles
    finally:
        os.unlink(path)


def test_chunk_document_paragraphs():
    path = temp_md("We are a software company.\n\nWe support all platforms.\n\nContact us.", "_general.md")
    try:
        assert len(make_builder().chunk_document(path)) == 3
    finally:
        os.unlink(path)


@pytest.mark.parametrize("domain", ["billing", "technical", "account", "general"])
def test_chunk_document_domain_detection(domain):
    path = temp_md("Some content.", f"_{domain}_docs.md")
    try:
        assert make_builder().chunk_document(path)[0]["domain"] == domain
    finally:
        os.unlink(path)


def test_chunk_document_default_domain():
    path = temp_md("Random content.", "_unrecognized_file.md")
    try:
        assert make_builder().chunk_document(path)[0]["domain"] == "general"
    finally:
        os.unlink(path)


def test_chunk_document_required_fields():
    path = temp_md("## Section 1\nContent here.", "_billing_guide.md")
    try:
        for doc in make_builder().chunk_document(path):
            assert {"id", "content", "domain", "source", "title"} <= doc.keys()
    finally:
        os.unlink(path)


def test_chunk_document_unique_ids():
    path = temp_md("## Section 1\nContent 1.\n\n## Section 2\nContent 2.", "_billing_guide.md")
    try:
        ids = [d["id"] for d in make_builder().chunk_document(path)]
        assert len(ids) == len(set(ids))
    finally:
        os.unlink(path)


def test_chunk_document_source_is_filename():
    path = temp_md("Some content.", "_billing_guide.md")
    try:
        assert make_builder().chunk_document(path)[0]["source"] == os.path.basename(path)
    finally:
        os.unlink(path)


def test_generate_embeddings_shape():
    mock_emb = MagicMock()
    mock_emb.embedding = [0.1] * 1536
    mock_openai = MagicMock()
    mock_openai.embeddings.create.return_value.data = [mock_emb, mock_emb]
    result = make_builder(mock_openai=mock_openai).generate_embeddings(["hello", "world"])
    assert len(result) == 2 and len(result[0]) == 1536


def test_upload_documents_adds_vectors():
    mock_emb = MagicMock()
    mock_emb.embedding = [0.5] * 1536
    mock_openai = MagicMock()
    mock_openai.embeddings.create.return_value.data = [mock_emb]
    mock_search = MagicMock()
    builder = make_builder(mock_openai=mock_openai, mock_search=mock_search)
    docs = [{"id": "1", "content": "test content", "domain": "billing", "source": "test.md", "title": "Test"}]
    builder.upload_documents(docs)
    mock_search.upload_documents.assert_called_once()
    uploaded = mock_search.upload_documents.call_args[1]["documents"]
    assert "content_vector" in uploaded[0]
    assert uploaded[0]["content_vector"] == [0.5] * 1536

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SimpleField,
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from config.settings import get_settings
import os
import uuid

EMBEDDING_DIMS = 1536
BATCH_SIZE = 100

DOMAIN_KEYWORDS = ["billing", "technical", "account", "general"]


class IndexBuilder:
    def __init__(self):
        settings = get_settings()
        credential = AzureKeyCredential(settings.azure_search_key)
        self.index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential,
        )
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=credential,
        )
        self.openai_client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
        )
        self.embedding_deployment = settings.azure_openai_embedding_deployment
        self.index_name = settings.azure_search_index

    def create_index(self):
        """Create the search index with vector search config."""
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="myHnsw"),
            ],
            profiles=[
                VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw"),
            ],
        )

        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=EMBEDDING_DIMS,
                vector_search_profile_name="myHnswProfile",
            ),
            SimpleField(name="domain", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="source", type=SearchFieldDataType.String),
            SearchableField(name="title", type=SearchFieldDataType.String),
        ]

        index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
        self.index_client.create_or_update_index(index)
        print('Index created or updated successfully.')

    def chunk_document(self, filepath: str) -> list[dict]:
        """Read a markdown file and split into chunks with metadata."""
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        filename = os.path.basename(filepath)
        source = filename

        domain = "general"
        for keyword in DOMAIN_KEYWORDS:
            if keyword in filename.lower():
                domain = keyword
                break

        # Split by ## headers; fall back to paragraph splitting
        raw_chunks = []
        if "\n## " in text or text.startswith("## "):
            sections = text.split("\n## ")
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                lines = section.strip().splitlines()
                title = lines[0].lstrip("# ").strip() if lines else f"Section {i}"
                content = "\n".join(lines[1:]).strip() if len(lines) > 1 else title
                raw_chunks.append({"raw_title": title, "raw_content": content})
        else:
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for i, para in enumerate(paragraphs):
                raw_chunks.append({"raw_title": f"{filename} part {i + 1}", "raw_content": para})

        documents = []
        for i, chunk in enumerate(raw_chunks):
            documents.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source}#{i}")),
                "content": chunk["raw_content"],
                "domain": domain,
                "source": source,
                "title": chunk["raw_title"],
            })

        return documents

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        response = self.openai_client.embeddings.create(
            input=texts,
            model=self.embedding_deployment,
        )
        return [item.embedding for item in response.data]

    def upload_documents(self, documents: list[dict]):
        """Upload chunked + embedded documents to the index."""
        for batch_start in range(0, len(documents), BATCH_SIZE):
            batch = documents[batch_start : batch_start + BATCH_SIZE]
            texts = [doc["content"] for doc in batch]
            vectors = self.generate_embeddings(texts)
            for doc, vector in zip(batch, vectors):
                doc["content_vector"] = vector
            self.search_client.upload_documents(documents=batch)


if __name__ == "__main__":
    import glob

    builder = IndexBuilder()

    print("Creating index...")
    builder.create_index()

    kb_dir = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base")
    md_files = glob.glob(os.path.join(kb_dir, "*.md"))

    if not md_files:
        print(f"No markdown files found in {kb_dir}")
    else:
        all_documents = []
        for filepath in md_files:
            print(f"Processing {os.path.basename(filepath)}...")
            docs = builder.chunk_document(filepath)
            all_documents.extend(docs)
            print(f"  -> {len(docs)} chunks")

        print(f"Uploading {len(all_documents)} documents...")
        builder.upload_documents(all_documents)
        print("Done.")

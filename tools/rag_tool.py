from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential
from config.settings import get_settings
import structlog

logger = structlog.get_logger()


class RAGTool:
    def __init__(self, domain: str = None):
        settings = get_settings()
        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_key),
        )
        self.domain = domain

    async def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """
        Hybrid search (semantic + keyword) with optional domain filtering.

        TODO:
        - Build a VectorizableTextQuery for vector search
        - Add domain filter if self.domain is set
        - Call self.client.search() with both text and vector
        - Return list of dicts with: content, source, domain, score
        - Log the retrieval
        """
        pass
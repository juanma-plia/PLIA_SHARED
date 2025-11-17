from google.cloud import firestore
from google.cloud.firestore import AsyncClient
from google.api_core.exceptions import GoogleAPIError, NotFound
from typing import Any, Optional, List, Dict, Tuple
import logging
import asyncio

logger = logging.getLogger(__name__)


class FirestoreService:
    """Cliente Firestore async seguro y correctamente inicializado."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self._client: Optional[AsyncClient] = None
        self._is_initialized = False

    async def init(self):
        """Inicializa el cliente async correctamente."""
        if not self._is_initialized:
            self._client = firestore.AsyncClient(project=self.project_id)
            self._is_initialized = True
            logger.info(
                f"[Firestore] Client initialized for project: {self.project_id}"
            )

    @property
    def client(self) -> AsyncClient:
        """
        Devuelve el cliente Firestore ya inicializado.
        Si no está inicializado → ERROR explícito y claro.
        """
        if self._client is None:
            raise RuntimeError(
                "Firestore client not initialized. Call await firestore.init() on startup."
            )
        return self._client

    async def get_document(
        self, collection: str, doc_id: str
    ) -> Optional[Dict[str, Any]]:
        try:
            doc_ref = self.client.collection(collection).document(doc_id)
            doc = await doc_ref.get()

            if doc.exists:
                logger.debug(f"[Firestore] Document retrieved: {collection}/{doc_id}")
                return doc.to_dict()

            logger.warning(f"[Firestore] Document not found: {collection}/{doc_id}")
            return None

        except NotFound:
            logger.warning(f"[Firestore] Document not found: {collection}/{doc_id}")
            return None
        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in get_document: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] get_document error: {e}")
            raise

    async def query_documents(
        self,
        collection: str,
        filters: Optional[List[Tuple[str, str, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        try:
            query = self.client.collection(collection)

            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)

            if order_by:
                query = query.order_by(order_by)

            if limit:
                query = query.limit(limit)

            docs = query.stream()
            return [doc.to_dict() async for doc in docs]

        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in query_documents: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] query_documents error: {e}")
            raise

    async def query_documents_in(
        self,
        collection: str,
        field: str,
        values: List[str],
        order_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            if not values:
                return []

            all_results = []

            for i in range(0, len(values), 10):
                chunk = values[i : i + 10]
                query = self.client.collection(collection).where(field, "in", chunk)

                if order_by:
                    query = query.order_by(order_by)

                docs = query.stream()
                all_results.extend([doc.to_dict() async for doc in docs])

            return all_results

        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in query_documents_in: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] query_documents_in error: {e}")
            raise

    async def close(self):
        """Limpia referencias del cliente."""
        if self._is_initialized:
            logger.info("[Firestore] Client released")
            self._client = None
            self._is_initialized = False


_firestore_service: Optional[FirestoreService] = None
_lock = asyncio.Lock()


async def get_firestore_service(project_id="plia-ai"):
    async with _lock:
        global _firestore_service
        if _firestore_service is None:
            _firestore_service = FirestoreService(project_id)
            await _firestore_service.init()
    return _firestore_service

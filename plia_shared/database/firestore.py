from google.cloud import firestore
from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core.exceptions import (
    GoogleAPIError,
    NotFound,
    ResourceExhausted,
    DeadlineExceeded,
)
from typing import Any, Optional, List, Dict, Tuple
import logging
import asyncio
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)

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
                    query = query.where(filter=FieldFilter(field, op, value))

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
        max_retries: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Query documents con operador 'in', dividiendo en chunks y ejecutando en paralelo.
        Incluye retry automático con exponential backoff usando tenacity (async).

        Args:
            collection: Nombre de la colección
            field: Campo a filtrar
            values: Lista de valores para el filtro 'in'
            order_by: Campo por el cual ordenar (opcional)
            max_retries: Número máximo de reintentos (default: 3)
        """
        if not values:
            return []

        chunks = [values[i : i + 10] for i in range(0, len(values), 10)]

        async def fetch_chunk_with_retry(chunk, chunk_index: int):
            """Fetch un chunk con retry automático usando AsyncRetrying"""

            retryer = AsyncRetrying(
                stop=stop_after_attempt(max_retries),
                wait=wait_exponential(multiplier=0.1, min=0.1, max=10),
                retry=retry_if_exception_type(
                    (
                        ResourceExhausted,
                        DeadlineExceeded,
                        GoogleAPIError,
                    )
                ),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=True,
            )

            async def _fetch():
                """Función interna que hace el fetch real"""
                query = self.client.collection(collection).where(
                    filter=FieldFilter(field, "in", chunk)
                )
                if order_by:
                    query = query.order_by(order_by)

                docs = query.stream()
                results = [doc.to_dict() async for doc in docs]

                return results

            try:
                async for attempt in retryer:
                    with attempt:
                        return await _fetch()
            except RetryError as e:
                logger.error(
                    f"[Firestore] Chunk {chunk_index} failed after {max_retries} attempts: {e.last_attempt.exception()}"
                )
                raise e.last_attempt.exception()

        try:
            results = await asyncio.gather(
                *(fetch_chunk_with_retry(chunk, i) for i, chunk in enumerate(chunks))
            )
        except Exception as e:
            logger.error(
                f"[Firestore] query_documents_in failed: {type(e).__name__}: {e}"
            )
            raise

        all_results = [doc for chunk_results in results for doc in chunk_results]
        return all_results

    async def create_document(
        self, collection: str, doc_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea un nuevo documento en la colección."""
        try:
            doc_ref = self.client.collection(collection).document(doc_id)
            await doc_ref.set(data)
            logger.info(f"[Firestore] Document created: {collection}/{doc_id}")
            return data
        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in create_document: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] create_document error: {e}")
            raise

    async def update_document(
        self, collection: str, doc_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza un documento existente."""
        try:
            doc_ref = self.client.collection(collection).document(doc_id)
            await doc_ref.update(data)
            logger.info(f"[Firestore] Document updated: {collection}/{doc_id}")
            return data
        except NotFound:
            logger.warning(
                f"[Firestore] Document not found for update: {collection}/{doc_id}"
            )
            raise
        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in update_document: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] update_document error: {e}")
            raise

    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Elimina un documento de la colección."""
        try:
            doc_ref = self.client.collection(collection).document(doc_id)
            await doc_ref.delete()
            logger.info(f"[Firestore] Document deleted: {collection}/{doc_id}")
            return True
        except GoogleAPIError as e:
            logger.error(f"[Firestore] API error in delete_document: {e}")
            raise
        except Exception as e:
            logger.error(f"[Firestore] delete_document error: {e}")
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

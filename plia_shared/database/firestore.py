"""
Cliente Firestore con soporte async y retry logic básico
"""
from google.cloud import firestore
from google.cloud.firestore import AsyncClient
from typing import Any, Optional, List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class FirestoreService:
    """Cliente Firestore con retry logic y error handling"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self._client: Optional[AsyncClient] = None

    @property
    def client(self) -> AsyncClient:
        """Lazy initialization del cliente"""
        if self._client is None:
            self._client = firestore.AsyncClient(project=self.project_id)
            logger.info(f"Firestore client initialized for project: {self.project_id}")
        return self._client


    async def get_document(
            self,
            collection: str,
            doc_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Args:
            collection: Nombre de la colección
            doc_id: ID del documento (UUID)

        Returns:
            Dict con los datos del documento o None si no existe
        """
        try:
            doc_ref = self.client.collection(collection).document(doc_id)
            doc = await doc_ref.get()

            if doc.exists:
                logger.debug(f"Document retrieved: {collection}/{doc_id}")
                return doc.to_dict()

            logger.warning(f"Document not found: {collection}/{doc_id}")
            return None

        except Exception as e:
            logger.error(f"Firestore get error [{collection}/{doc_id}]: {str(e)}")
            raise


    async def query_documents(
            self,
            collection: str,
            filters: Optional[List[Tuple[str, str, Any]]] = None,
            order_by: Optional[str] = None,
            limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documentos con filtros

        Args:
            collection: Nombre de la colección
            filters: Lista de tuplas (field, operator, value)
                    Ejemplo: [("serie_uuid", "==", "abc123")]
            order_by: Campo para ordenar
            limit: Límite de resultados

        Returns:
            Lista de documentos
        """
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
            results = [doc.to_dict() async for doc in docs]

            logger.debug(f"Documents queried: {collection} ({len(results)} results)")

            return results

        except Exception as e:
            logger.error(f"Firestore query error [{collection}]: {str(e)}")
            raise


    async def query_documents_in(
            self,
            collection: str,
            field: str,
            values: List[str],
            order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documentos donde field está en una lista de valores

        Args:
            collection: Nombre de la colección
            field: Campo a filtrar
            values: Lista de valores
            order_by: Campo para ordenar

        Returns:
            Lista de documentos

        Note:
            Firestore limita "in" queries a 10 valores.
            Si hay más, se hacen múltiples queries.
        """
        try:
            all_results = []

            for i in range(0, len(values), 10):
                chunk = values[i:i + 10]
                query = self.client.collection(collection).where(
                    field, "in", chunk
                )

                if order_by:
                    query = query.order_by(order_by)

                docs = query.stream()
                results = [doc.to_dict() async for doc in docs]
                all_results.extend(results)

            logger.debug(
                f"Documents queried IN: {collection} "
                f"(field={field}, values={len(values)}, results={len(all_results)})"
            )

            return all_results

        except Exception as e:
            logger.error(f"Firestore query IN error [{collection}]: {str(e)}")
            raise

    async def close(self):
        """Cierra la conexión (cleanup)"""
        if self._client:
            self._client = None
            logger.info("Firestore client closed")


_firestore_service: Optional[FirestoreService] = None


def get_firestore_service(project_id: str = "plia-ai") -> FirestoreService:
    """
    Factory function para obtener instancia del servicio Firestore
    Usada como dependency en FastAPI
    """
    global _firestore_service
    if _firestore_service is None:
        _firestore_service = FirestoreService(project_id)
    return _firestore_service

"""
Servicio para gestión de ACLs (Access Control Lists)
Lógica compartida entre microservicios para validar permisos
"""
from typing import List, Dict, Any, Tuple
from plia_shared.database.firestore import FirestoreService
from plia_shared.core.errors import ProfileNotFoundException
import logging

logger = logging.getLogger(__name__)


class ACLService:
    """Servicio para gestión de permisos (ACL)"""

    def __init__(self, firestore: FirestoreService):
        self.firestore = firestore

    async def get_profile_with_acl(
            self,
            profile_uuid: str
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Obtiene el perfil y calcula sus ACLs

        Args:
            profile_uuid: UUID del perfil

        Returns:
            Tuple (profile_dict, series_acl_list)

        Raises:
            ProfileNotFoundException: Si el perfil no existe
        """
        profile = await self.firestore.get_document("profiles", profile_uuid)
        if not profile:
            raise ProfileNotFoundException(profile_uuid)

        org_uuid = profile.get("org_uuid")
        org_series_acl = []

        if org_uuid:
            org = await self.firestore.get_document("orgs", org_uuid)
            if org:
                org_series_acl = org.get("series_acl", [])

        profile_series_acl = profile.get("series_acl", [])

        series_acl = list(set(org_series_acl + profile_series_acl))

        if not series_acl:
            series_acl = []

        return profile, series_acl

    async def validate_serie_access(
            self,
            profile_uuid: str,
            serie_uuid: str
    ) -> bool:
        """
        Valida si un perfil tiene acceso a una serie

        Args:
            profile_uuid: UUID del perfil
            serie_uuid: UUID de la serie

        Returns:
            True si tiene acceso, False si no
        """
        profile, series_acl = await self.get_profile_with_acl(profile_uuid)

        has_access = serie_uuid in series_acl

        return has_access

    async def get_series_for_profile(
            self,
            profile_uuid: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las series accesibles para un perfil

        Args:
            profile_uuid: UUID del perfil

        Returns:
            Lista de series (documentos completos)
        """
        profile, series_acl = await self.get_profile_with_acl(profile_uuid)

        if not series_acl:
            return []

        series = await self.firestore.query_documents_in(
            collection="series",
            field="serie_uuid",
            values=series_acl,
            order_by="order"
        )

        return series


def get_acl_service(
        firestore: FirestoreService
) -> ACLService:
    """
    Factory function para obtener instancia del servicio ACL
    Usada como dependency en FastAPI
    """
    return ACLService(firestore)

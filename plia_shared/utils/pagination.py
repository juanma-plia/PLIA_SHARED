"""
Utilidades de paginación reutilizables para todos los microservicios.
"""
from typing import List, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parámetros de paginación estándar para query params"""

    page: int = Field(default=1, ge=1, description="Número de página (1-based)")
    page_size: int = Field(
        default=25, ge=1, le=100, description="Items por página (máx: 100)"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Response paginada genérica.
    Usar con List[YourModel] para type safety.
    """

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        # Para que funcione con herencia
        arbitrary_types_allowed = True


def paginate_list(items: List[T], page: int, page_size: int) -> tuple[List[T], int]:
    """
    Pagina una lista en memoria.

    Args:
        items: Lista completa de items
        page: Número de página (1-based)
        page_size: Tamaño de página

    Returns:
        Tuple con (items_de_la_pagina, total_items)

    Example:
        >>> all_items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> paginated, total = paginate_list(all_items, page=2, page_size=3)
        >>> paginated
        [4, 5, 6]
        >>> total
        10
    """
    total = len(items)
    offset = (page - 1) * page_size
    paginated = items[offset : offset + page_size]
    return paginated, total


def calculate_total_pages(total_items: int, page_size: int) -> int:
    """
    Calcula el número total de páginas.

    Args:
        total_items: Total de items
        page_size: Tamaño de página

    Returns:
        Número total de páginas

    Example:
        >>> calculate_total_pages(100, 25)
        4
        >>> calculate_total_pages(101, 25)
        5
        >>> calculate_total_pages(0, 25)
        0
    """
    if total_items == 0:
        return 0
    return (total_items + page_size - 1) // page_size


from typing import List
from fastapi import APIRouter, Header
from schemas.models import CategorySchema

router = APIRouter(prefix="/categories", tags=["Categories"])

CATEGORIES_DB = [
    CategorySchema(
        id="cat-pasteles-autor",
        name="Pasteles de Autor",
        slug="pasteles-de-autor",
        description="Creaciones exclusivas de nuestra chef pastelera con ingredientes de origen.",
        image="https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
        displayOrder=1,
    ),
    CategorySchema(
        id="cat-tartas-finas",
        name="Tartas Finas",
        slug="tartas-finas",
        description="Masa sablée crujiente, cremas infusionadas y frutas de estación seleccionadas.",
        image="https://images.unsplash.com/photo-1519869325930-281384150729?auto=format&fit=crop&w=800&q=80",
        displayOrder=2,
    ),
    CategorySchema(
        id="cat-macarons",
        name="Macarons & Petits Fours",
        slug="macarons-petits-fours",
        description="Delicadeza parisina elaborada con harina de almendras y ganaches infusionadas.",
        image="https://images.unsplash.com/photo-1569864321318-64445eb07464?auto=format&fit=crop&w=800&q=80",
        displayOrder=3,
    ),
    CategorySchema(
        id="cat-panaderia",
        name="Viennoiserie & Panadería",
        slug="viennoiserie-panaderia",
        description="Croissants de mantequilla francesa pura y masa madre de fermentación lenta.",
        image="https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80",
        displayOrder=4,
    ),
    CategorySchema(
        id="cat-sin-gluten",
        name="Línea Saludable & Sin Gluten",
        slug="saludable-sin-gluten",
        description="Postres libres de gluten y opciones veganas sin comprometer el sabor sublime.",
        image="https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=800&q=80",
        displayOrder=5,
    ),
]

@router.get("", response_model=List[CategorySchema])
def list_categories(x_tenant_id: str = Header(default="default-atelier")):
    return sorted(CATEGORIES_DB, key=lambda c: c.displayOrder)

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Header
from schemas.models import ProductSchema, PaginatedProductsResponse, ProductVariantSchema

router = APIRouter(prefix="/products", tags=["Products"])

PRODUCTS_DB = [
    ProductSchema(
        id="prod-opera-noir",
        name="Gâteau Opéra Grand Cru",
        slug="gateau-opera-grand-cru",
        tagline="Bizcocho Joconde, ganache de chocolate Guanaja 70% y crema de café arábica.",
        description="El clásico francés reinterpretado con capas milimétricas de bizcocho Joconde bañado en café espresso, ganache sedosa de chocolate negro Grand Cru y glaseado espejo.",
        price=38.0,
        discountedPrice=34.0,
        categoryId="cat-pasteles-autor",
        images=[
            "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=800&q=80",
        ],
        ingredients=["Harina de almendras", "Café arábica de origen", "Chocolate Valrhona 70%", "Mantequilla AOP", "Huevos de campo"],
        allergens=["Gluten", "Lácteos", "Huevos", "Frutos secos"],
        calories=420,
        isGlutenFree=False,
        isVegan=False,
        isCustomizable=True,
        rating=4.9,
        reviewsCount=128,
        stockStatus="in_stock",
        prepTimeMinutes=45,
        featured=True,
        variants=[
            ProductVariantSchema(id="var-op-6p", name="6 a 8 Porciones", portions=8, price=38.0, sku="OP-08P", isAvailable=True),
            ProductVariantSchema(id="var-op-12p", name="12 a 14 Porciones", portions=14, price=62.0, sku="OP-14P", isAvailable=True),
            ProductVariantSchema(id="var-op-ind", name="Porción Individual", portions=1, price=6.5, sku="OP-IND", isAvailable=True),
        ],
    ),
    ProductSchema(
        id="prod-tartaleta-frutos-rojos",
        name="Tartelette Framboise & Pistache",
        slug="tartelette-framboise-pistache",
        tagline="Sablée crocante, crema diplomática de pistacho siciliano y frambuesas frescas.",
        description="Base de masa sablée crujiente rellena con crema diplomática ligera infusionada con pasta de pistacho de Bronte DOP y frambuesas silvestres frescas.",
        price=29.5,
        categoryId="cat-tartas-finas",
        images=["https://images.unsplash.com/photo-1519869325930-281384150729?auto=format&fit=crop&w=800&q=80"],
        ingredients=["Frambuesas frescas", "Pistachos de Sicilia", "Mantequilla francesa", "Vainilla Bourbon de Madagascar"],
        allergens=["Gluten", "Lácteos", "Huevos", "Pistacho"],
        calories=340,
        isGlutenFree=False,
        isVegan=False,
        isCustomizable=False,
        rating=4.8,
        reviewsCount=94,
        stockStatus="in_stock",
        prepTimeMinutes=30,
        featured=True,
        variants=[
            ProductVariantSchema(id="var-tf-6p", name="Mediana (6 porciones)", portions=6, price=29.5, sku="TF-06P", isAvailable=True),
            ProductVariantSchema(id="var-tf-ind", name="Individual", portions=1, price=5.8, sku="TF-IND", isAvailable=True),
        ],
    ),
    ProductSchema(
        id="prod-macarons-prestige",
        name="Coffret Prestige 12 Macarons",
        slug="coffret-prestige-macarons",
        tagline="Selección de autor: Vainilla Bourbon, Maracuyá, Caramelo Salado, Pistacho y Frambuesa.",
        description="Caja de regalo de lujo con 12 macarons artesanales elaborados con almendras de California, merengue italiano impecable y rellenos cremosos.",
        price=24.0,
        categoryId="cat-macarons",
        images=["https://images.unsplash.com/photo-1569864321318-64445eb07464?auto=format&fit=crop&w=800&q=80"],
        ingredients=["Harina de almendra fina", "Claras de huevo", "Chocolate blanco y negro", "Frutas naturales"],
        allergens=["Huevos", "Lácteos", "Frutos secos (Almendra, Pistacho)"],
        calories=95,
        isGlutenFree=True,
        isVegan=False,
        isCustomizable=True,
        rating=5.0,
        reviewsCount=215,
        stockStatus="in_stock",
        prepTimeMinutes=15,
        featured=True,
        variants=[
            ProductVariantSchema(id="var-mac-12", name="Caja x 12 unidades", portions=12, price=24.0, sku="MAC-12", isAvailable=True),
            ProductVariantSchema(id="var-mac-24", name="Caja x 24 unidades", portions=24, price=44.0, sku="MAC-24", isAvailable=True),
        ],
    ),
    ProductSchema(
        id="prod-croissant-almendras",
        name="Croissant aux Amandes Pur Beurre",
        slug="croissant-aux-amandes",
        tagline="Hojaldre laminado artesanal con frangipane y láminas de almendra tostada.",
        description="Croissant de masa madre horneado dos veces con crema frangipane de almendras y terminado con azúcar glas nevada.",
        price=4.8,
        categoryId="cat-panaderia",
        images=["https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=800&q=80"],
        ingredients=["Harina de fuerza", "Mantequilla francesa AOP", "Crema de almendras", "Almendras fileteadas"],
        allergens=["Gluten", "Lácteos", "Huevos", "Almendras"],
        calories=390,
        isGlutenFree=False,
        isVegan=False,
        isCustomizable=False,
        rating=4.9,
        reviewsCount=310,
        stockStatus="in_stock",
        prepTimeMinutes=10,
        featured=False,
        variants=[
            ProductVariantSchema(id="var-cr-1", name="Pieza individual", portions=1, price=4.8, sku="CR-IND", isAvailable=True),
        ],
    ),
    ProductSchema(
        id="prod-cheesecake-vasco",
        name="Basque Burnt Cheesecake con Vainilla",
        slug="basque-burnt-cheesecake",
        tagline="Centro ultra cremoso casi fundente y corteza caramelizada irresistible.",
        description="La célebre tarta de queso al estilo Donostia, horneada a alta temperatura con un corazón sedoso con vainilla Bourbon pura.",
        price=36.0,
        categoryId="cat-pasteles-autor",
        images=["https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=800&q=80"],
        ingredients=["Queso crema de alta gama", "Nata fresca 38%", "Huevos camperos", "Azúcar de caña", "Vainilla Bourbon"],
        allergens=["Lácteos", "Huevos"],
        isGlutenFree=True,
        isVegan=False,
        isCustomizable=True,
        rating=4.9,
        reviewsCount=180,
        stockStatus="in_stock",
        prepTimeMinutes=40,
        featured=True,
        variants=[
            ProductVariantSchema(id="var-ch-8p", name="Mediana (8-10 porciones)", portions=10, price=36.0, sku="CH-10P", isAvailable=True),
        ],
    ),
    ProductSchema(
        id="prod-tarta-maracuya-vegan",
        name="Tarta Cacao & Maracuyá (Vegan)",
        slug="tarta-cacao-maracuya-vegan",
        tagline="100% de origen vegetal: mousse de chocolate amargo y coulis de maracuyá.",
        description="Base de frutos secos y dátiles Medjool, mousse aterciopelada de chocolate negro 72% y coulis fresco de fruta de la pasión.",
        price=32.0,
        categoryId="cat-sin-gluten",
        images=["https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=800&q=80"],
        ingredients=["Dátiles Medjool", "Nueces pecán", "Chocolate 72%", "Leche de coco", "Maracuyá fresco"],
        allergens=["Frutos secos"],
        calories=290,
        isGlutenFree=True,
        isVegan=True,
        isCustomizable=False,
        rating=4.7,
        reviewsCount=63,
        stockStatus="in_stock",
        prepTimeMinutes=30,
        featured=False,
        variants=[
            ProductVariantSchema(id="var-veg-8p", name="8 porciones", portions=8, price=32.0, sku="VEG-08P", isAvailable=True),
        ],
    ),
]

@router.get("", response_model=PaginatedProductsResponse)
def list_products(
    categoryId: Optional[str] = Query(None),
    isGlutenFree: Optional[bool] = Query(None),
    isVegan: Optional[bool] = Query(None),
    featured: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    x_tenant_id: str = Header(default="default-atelier"),
):
    results = PRODUCTS_DB

    if categoryId:
        results = [p for p in results if p.categoryId == categoryId]
    if isGlutenFree is not None:
        results = [p for p in results if p.isGlutenFree == isGlutenFree]
    if isVegan is not None:
        results = [p for p in results if p.isVegan == isVegan]
    if featured is not None:
        results = [p for p in results if p.featured == featured]
    if search:
        q = search.lower()
        results = [p for p in results if q in p.name.lower() or q in p.description.lower()]

    total = len(results)
    start = (page - 1) * pageSize
    end = start + pageSize
    items = results[start:end]
    totalPages = (total + pageSize - 1) // pageSize if pageSize else 1

    return PaginatedProductsResponse(
        items=items,
        total=total,
        page=page,
        pageSize=pageSize,
        totalPages=totalPages,
    )

@router.get("/{product_id}", response_model=ProductSchema)
def get_product_by_id(product_id: str, x_tenant_id: str = Header(default="default-atelier")):
    for p in PRODUCTS_DB:
        if p.id == product_id or p.slug == product_id:
            return p
    raise HTTPException(status_code=404, detail="Producto no encontrado en el catálogo de la pastelería.")

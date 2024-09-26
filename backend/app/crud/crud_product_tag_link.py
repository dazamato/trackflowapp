from sqlmodel import Session, select
from app.models.product_tag_link_model import ProductTagLink
from fastapi.encoders import jsonable_encoder

def create_product_tag_link(session: Session, product_tag_link_in: ProductTagLink) -> ProductTagLink:
    session.add(product_tag_link_in)
    session.commit()
    session.refresh(product_tag_link_in)
    return product_tag_link_in

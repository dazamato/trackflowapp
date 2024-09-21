from app.models.base import Field, Relationship, SQLModel
import uuid

class ProductTagLink(SQLModel, table=True):
    product_id: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key="product.id", primary_key=True, ondelete="CASCADE")
    product_tag_id: uuid.UUID = Field(default_factory=uuid.uuid4, foreign_key="producttag.id", primary_key=True, ondelete="CASCADE")

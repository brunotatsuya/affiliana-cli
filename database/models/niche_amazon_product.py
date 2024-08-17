from sqlmodel import Field, SQLModel


class NicheAmazonProduct(SQLModel, table=True):

    __tablename__ = "niches_amazon_products"

    niche_id: int = Field(foreign_key="niches.id", primary_key=True)
    amazon_product_asin: str = Field(
        foreign_key="amazon_products.asin", primary_key=True
    )

import inject
from sqlmodel import select
from sqlalchemy.orm import joinedload

from app.exceptions import NotFoundError
from app.interfaces.dtos.amazon_product_snapshot import AmazonProductSnapshot
from database.connection import DatabaseConnection
from database.models import AmazonProduct
from .niches_repository import NichesRepository
from .base_repository import BaseRepository


class AmazonProductsRepository(BaseRepository):
    """
    Repository class for managing Amazon products in the database.
    """

    @inject.autoparams()
    def __init__(self, conn: DatabaseConnection, niches_repo: NichesRepository):
        super().__init__(conn)
        self.niches_repo = niches_repo

    def find_amazon_product(self, asin: str) -> AmazonProduct | None:
        """
        Finds an Amazon product by its ASIN.

        Args:
            asin (str): The ASIN of the product to find.

        Returns:
            AmazonProduct: The found Amazon product object.
            None: If no product is found.
        """
        with self.conn.session() as session:
            statement = (
                select(AmazonProduct)
                .options(joinedload(AmazonProduct.niches))
                .where(AmazonProduct.asin == asin)
            )
            return session.exec(statement).first()

    def upsert_amazon_product(self, snapshot: AmazonProductSnapshot, niche_id: int):
        """
        Inserts or updates an Amazon product into the database.

        Args:
            snapshot (AmazonProductSnapshot): The snapshot containing product data to insert.
            niche_id (int): The ID of the niche associated with the product.

        Returns:
            AmazonProduct: The inserted Amazon product object.

        Raises:
            NotFoundError: If an error occurs during the insertion process.
        """
        # Find the niche
        db_niche = self.niches_repo.find_niche_by_id(niche_id)
        if not db_niche:
            raise NotFoundError(f"Niche with ID {niche_id} not found.")

        with self.conn.session() as session:

            # Check if the product already exists in the database
            product = self.find_amazon_product(snapshot.asin)

            # If not exists, then create a new product
            if not product:
                product = AmazonProduct(
                    asin=snapshot.asin,
                    title=snapshot.title,
                    is_sponsored=snapshot.is_sponsored,
                    price_usd=snapshot.price_usd,
                    rating=snapshot.rating,
                    reviews=snapshot.reviews,
                    bought_last_month=snapshot.bought_last_month,
                    seen_at=snapshot.seen_at,
                )
                session.add(product)
            # If exists, then update the product
            else:
                product.title = snapshot.title
                product.is_sponsored = snapshot.is_sponsored
                product.price_usd = snapshot.price_usd
                product.rating = snapshot.rating
                product.reviews = snapshot.reviews
                product.bought_last_month = snapshot.bought_last_month
                product.seen_at = snapshot.seen_at

            # Associate the product with the niche if not already associated
            if db_niche not in product.niches:
                product.niches.append(db_niche)

            try:
                session.add(product)
                session.commit()
                session.refresh(product)
                return product
            except Exception as e:
                session.rollback()
                raise e

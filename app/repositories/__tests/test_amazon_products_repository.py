from datetime import datetime
import inject
import pytest
from sqlmodel import select, delete

from app.interfaces.dtos.amazon_product_snapshot import AmazonProductSnapshot
from app.repositories.amazon_products_repository import AmazonProductsRepository
from database.connection import DatabaseConnection
from database.models import AmazonProduct, NicheAmazonProduct, Niche


class TestAmazonProductsRepository:

    @pytest.fixture(scope="class")
    def database_connection(self):
        return inject.instance(DatabaseConnection)

    @pytest.fixture(scope="class")
    def amazon_products_repository(self):
        return AmazonProductsRepository()

    @pytest.fixture
    def niche(self, database_connection: DatabaseConnection):

        with database_connection.session() as session:
            niche = session.exec(
                select(Niche).where(Niche.name == "Test Niche")
            ).first()
            if not niche:
                niche = Niche(
                    name="Test Niche",
                    created_at=datetime.now(),
                )
                session.add(niche)
                session.commit()
                session.refresh(niche)
            return niche

    @pytest.fixture(autouse=True)
    def clean_tables(self, database_connection: DatabaseConnection):
        yield
        with database_connection.session() as session:
            session.exec(delete(NicheAmazonProduct))
            session.exec(delete(AmazonProduct))
            session.exec(delete(Niche))
            session.commit()

    def test_should_return_existing_amazon_product_when_searching_by_asin(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
    ):
        # Create a new Amazon product in the database
        product = AmazonProduct(
            asin="B07H8L85PS",
            title="Test Product",
            price_usd=100.0,
            is_sponsored=True,
            seen_at=datetime.now(),
        )

        with database_connection.session() as session:
            session.add(product)
            session.commit()

            # Find the product by ASIN
            searched_product = amazon_products_repository.find_amazon_product(
                product.asin
            )

            # Assert
            assert searched_product == product

    def test_should_return_none_when_searching_non_existing_amazon_product_asin(
        self, amazon_products_repository: AmazonProductsRepository
    ):
        # Find a product that doesn't exist
        searched_product = amazon_products_repository.find_amazon_product("9999")

        # Assert
        assert searched_product is None

    def test_should_insert_new_amazon_product_into_database(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
        amazon_product_snapshot: AmazonProductSnapshot,
        niche: Niche,
    ):
        # Insert a new Amazon product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Find the inserted product in the database
        with database_connection.session() as session:
            product = session.exec(
                select(AmazonProduct).where(
                    AmazonProduct.asin == amazon_product_snapshot.asin
                )
            ).first()

            # Assert
            assert product.title == amazon_product_snapshot.title
            assert product.is_sponsored == amazon_product_snapshot.is_sponsored
            assert product.price_usd == amazon_product_snapshot.price_usd
            assert product.rating == amazon_product_snapshot.rating
            assert product.reviews == amazon_product_snapshot.reviews
            assert (
                product.bought_last_month == amazon_product_snapshot.bought_last_month
            )
            assert product.seen_at == amazon_product_snapshot.seen_at

    def test_should_update_existing_amazon_product_in_database(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
        amazon_product_snapshot: AmazonProductSnapshot,
        niche: Niche,
    ):
        # Insert a new Amazon product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        amazon_product_snapshot.bought_last_month = 2000
        amazon_product_snapshot.reviews = 2000
        amazon_product_snapshot.rating = 4.8
        amazon_product_snapshot.price_usd = 120.0
        amazon_product_snapshot.seen_at = datetime(2024, 1, 1)

        # Update the inserted product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Find the updated product in the database
        with database_connection.session() as session:
            product = session.exec(
                select(AmazonProduct).where(
                    AmazonProduct.asin == amazon_product_snapshot.asin
                )
            ).first()

            # Assert
            assert product.title == amazon_product_snapshot.title
            assert product.is_sponsored == amazon_product_snapshot.is_sponsored
            assert product.price_usd == amazon_product_snapshot.price_usd
            assert product.rating == amazon_product_snapshot.rating
            assert product.reviews == amazon_product_snapshot.reviews
            assert (
                product.bought_last_month == amazon_product_snapshot.bought_last_month
            )
            assert product.seen_at == amazon_product_snapshot.seen_at

    def test_should_not_insert_new_product_if_product_exists(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
        amazon_product_snapshot: AmazonProductSnapshot,
        niche: Niche,
    ):
        # Insert a new Amazon product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Insert the same product again
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Find the inserted product in the database
        with database_connection.session() as session:
            products = session.exec(select(AmazonProduct)).all()

            # Assert
            assert len(products) == 1

    def test_should_associate_amazon_product_with_niche(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
        amazon_product_snapshot: AmazonProductSnapshot,
        niche: Niche,
    ):
        # Insert a new Amazon product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Find the inserted product in the database
        with database_connection.session() as session:
            product = session.exec(
                select(AmazonProduct).where(
                    AmazonProduct.asin == amazon_product_snapshot.asin
                )
            ).first()

            # Assert
            assert product.niches[0].id == niche.id

    def test_should_not_associate_amazon_product_with_niche_twice(
        self,
        database_connection: DatabaseConnection,
        amazon_products_repository: AmazonProductsRepository,
        amazon_product_snapshot: AmazonProductSnapshot,
        niche: Niche,
    ):
        # Insert a new Amazon product
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Insert the same product again
        amazon_products_repository.upsert_amazon_product(
            amazon_product_snapshot, niche.id
        )

        # Find the inserted product in the database
        with database_connection.session() as session:
            product = session.exec(
                select(AmazonProduct).where(
                    AmazonProduct.asin == amazon_product_snapshot.asin
                )
            ).first()

            # Assert
            assert len(product.niches) == 1

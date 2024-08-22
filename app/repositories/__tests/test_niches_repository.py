from datetime import datetime
import inject
import pytest
from sqlmodel import select, delete

from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission
from app.repositories.niches_repository import NichesRepository
from database.connection import DatabaseConnection
from database.models import Niche


class TestNichesRepository:

    @pytest.fixture(scope="class")
    def database_connection(self):
        return inject.instance(DatabaseConnection)

    @pytest.fixture(scope="class")
    def niches_repository(self):
        return NichesRepository()

    @pytest.fixture(autouse=True)
    def clean_niche_table(self, database_connection: DatabaseConnection):
        yield
        with database_connection.session() as session:
            session.exec(delete(Niche))
            session.commit()

    def test_should_return_existing_niche_when_searching_by_id(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niche in the database
        niche = Niche(name="Test Niche", created_at=datetime.now())

        with database_connection.session() as session:
            session.add(niche)
            session.commit()

            # Find the niche by ID
            searched_niche = niches_repository.find_niche_by_id(niche.id)

            # Assert
            assert searched_niche == niche

    def test_should_return_none_when_searching_non_existing_niche_id(
        self, niches_repository: NichesRepository
    ):
        # Find a niche that doesn't exist
        searched_niche = niches_repository.find_niche_by_id(9999)

        # Assert
        assert searched_niche is None

    def test_should_return_existing_niche_when_searching_by_name(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niche in the database
        niche = Niche(name="Test Niche", created_at=datetime.now())

        with database_connection.session() as session:
            session.add(niche)
            session.commit()
            session.refresh(niche)

            # Find the niche by name
            searched_niche = niches_repository.find_niche("Test Niche")

            # Assert
            assert searched_niche == niche

    def test_should_return_none_when_searching_non_existing_niche_name(
        self, niches_repository: NichesRepository
    ):
        # Find a niche that doesn't exist
        searched_niche = niches_repository.find_niche("Non Existing Niche")

        # Assert
        assert searched_niche is None

    def test_should_insert_new_niche_when_creating_with_a_new_name(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Insert a new niche
        niche = niches_repository.find_or_insert_niche("Test Niche")

        # Assert
        with database_connection.session() as session:
            searched_niche = session.exec(
                select(Niche).where(Niche.id == niche.id)
            ).first()
            assert searched_niche == niche

    def test_should_return_existing_niche_when_creating_with_an_existing_name(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niche in the database
        niche = Niche(name="Test Niche", created_at=datetime.now())

        with database_connection.session() as session:
            session.add(niche)
            session.commit()

            # Insert the existing niche
            existing_niche = niches_repository.find_or_insert_niche("Test Niche")

            # Select the existing niches with the provided name
            niches = session.exec(select(Niche).where(Niche.name == "Test Niche")).all()

            # Assert
            assert existing_niche == niche
            assert len(niches) == 1

    def test_should_return_all_niches_names_when_getting_all(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niches in the database
        niche1 = Niche(name="Test Niche 1", created_at=datetime.now())
        niche2 = Niche(name="Test Niche 2", created_at=datetime.now())

        with database_connection.session() as session:
            session.add(niche1)
            session.add(niche2)
            session.commit()

            # Get all niches
            niches = niches_repository.get_all_niches_names()

            # Assert
            assert niches == ["Test Niche 1", "Test Niche 2"]

    def test_should_return_empty_list_when_no_niches_exist_and_getting_all_niches_names(
        self,
        niches_repository: NichesRepository,
    ):
        # Get all niches
        niches = niches_repository.get_all_niches_names()

        # Assert
        assert niches == []

    def test_should_return_only_niches_names_with_no_amazon_commission_rate_when_getting_those(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niches in the database
        niche1 = Niche(name="Test Niche 1", created_at=datetime.now())
        niche2 = Niche(
            name="Test Niche 2", created_at=datetime.now(), amazon_commission_rate=3
        )
        niche3 = Niche(name="Test Niche 3", created_at=datetime.now())
        niche4 = Niche(
            name="Test Niche 4", created_at=datetime.now(), amazon_commission_rate=4.5
        )
        niche5 = Niche(name="Test Niche 5", created_at=datetime.now())

        with database_connection.session() as session:
            session.add(niche1)
            session.add(niche2)
            session.add(niche3)
            session.add(niche4)
            session.add(niche5)
            session.commit()

            # Get all niches
            niches = niches_repository.get_niches_names_with_no_amazon_commission_rate()

            # Assert
            assert niches == ["Test Niche 1", "Test Niche 3", "Test Niche 5"]

    def test_should_return_empty_list_when_getting_niches_names_with_no_commission_rate_and_all_niches_have_commission(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        # Create a new niches in the database
        niche1 = Niche(
            name="Test Niche 1", created_at=datetime.now(), amazon_commission_rate=3
        )
        niche2 = Niche(
            name="Test Niche 2", created_at=datetime.now(), amazon_commission_rate=4.5
        )

        with database_connection.session() as session:
            session.add(niche1)
            session.add(niche2)
            session.commit()

            # Get all niches
            niches = niches_repository.get_niches_names_with_no_amazon_commission_rate()

            # Assert
            assert niches == []

    def test_should_update_niche_commission_rate_for_every_commission_provided(
        self,
        database_connection: DatabaseConnection,
        niches_repository: NichesRepository,
    ):
        commissions_fetched = [
            NicheAmazonCommission(niche="Cat toys", category="Pets", commission_rate=4.5),
            NicheAmazonCommission(niche="Chef knives", category="Kitchen", commission_rate=2.5),
        ]

        # Create a new niches in the database
        niche1 = Niche(name="Cat toys", created_at=datetime.now())
        niche2 = Niche(
            name="Chef knives", created_at=datetime.now(), amazon_commission_rate=4.5
        )

        with database_connection.session() as session:
            session.add(niche1)
            session.add(niche2)
            session.commit()

            # Update commission rates
            niches_repository.update_niches_amazon_commission_rates(commissions_fetched)

            # Get and assert
            db_niche1 = niches_repository.find_niche("Cat toys")
            db_niche2 = niches_repository.find_niche("Chef knives")

            assert db_niche1.amazon_commission_rate == 4.5
            assert db_niche2.amazon_commission_rate == 2.5

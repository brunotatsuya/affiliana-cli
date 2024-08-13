from datetime import datetime
import inject
import pytest
from sqlmodel import select, delete

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

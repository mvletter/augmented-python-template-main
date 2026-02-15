import glob

import pytest
from pytest_alembic import create_alembic_fixture, tests


alembic_fixture = create_alembic_fixture({"file": "alembic.ini"})


@pytest.mark.skipif(not glob.glob("migrations/versions/*.py"), reason="No migrations available yet.")
def test_single_head_revision_history(alembic_fixture) -> None:
    """
    Tests that there are not multiple alembic HEAD versions.
    """
    tests.test_single_head_revision(alembic_fixture)


def test_model_definitions_match_ddl(alembic_fixture) -> None:
    """
    Test that our model definitions are equal accross migrations.
    """
    tests.test_model_definitions_match_ddl(alembic_fixture)


def test_upgrade(alembic_fixture) -> None:
    """
    Test that we can upgrade from base to HEAD in alembic without issue.
    """
    tests.test_upgrade(alembic_fixture)


def test_up_down_consistency(alembic_fixture) -> None:
    """
    Test that we can downgrade from HEAD to base without issue.
    """
    tests.test_up_down_consistency(alembic_fixture)

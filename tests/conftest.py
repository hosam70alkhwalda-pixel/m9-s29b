"""pytest configuration for the Stretch Thu autograder."""

from __future__ import annotations

import os
import sys

import pytest
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add the repo root to sys.path so `from retrieval.x import ...` resolves.
# (Per the Autograder Test Path Rule: '..', NOT '../starter/'. Starter
# becomes the repo root when this template is forked.)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def neo4j_driver():
    load_dotenv()
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "testtest")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    yield driver
    driver.close()


@pytest.fixture(scope="session")
def embedder():
    """Reuse a single SentenceTransformer instance across tests."""
    from retrieval.embed import get_embedder
    return get_embedder()

import pytest
import os
import json
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

# Set temporary database paths for testing
os.environ["DB_PATH"] = "./data/test_sqlite.db"
os.environ["VECTOR_STORE_PATH"] = "./data/test_vector_store"
os.environ["DATA_DIR"] = "./data/test_data"

from main import (
    app, init_db, get_user, get_all_documents, get_db_connection,
    verify_document_access as check_document_access,
    get_allowed_document_ids as get_authorized_doc_ids,
    ingest_document, get_vector_store,
    detect_query_intent, run_agent_workflow
)

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup test directories
    test_data_dir = Path("./data/test_data")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    (test_data_dir / "raw").mkdir(parents=True, exist_ok=True)
    
    # Initialize DB
    init_db()
    
    yield
    
    # Clean up test databases
    db_file = Path("./data/test_sqlite.db")
    if db_file.exists():
        db_file.unlink()
        
    shutil.rmtree("./data/test_vector_store", ignore_errors=True)
    shutil.rmtree("./data/test_data", ignore_errors=True)

def test_database_seeding():
    # Verify default users seeded
    admin = get_user("admin")
    assert admin is not None
    assert admin["role"] == "Admin"
    assert admin["department"] == "General"
    
    alice = get_user("alice")
    assert alice is not None
    assert alice["role"] == "HR"
    assert alice["department"] == "HR"

def test_rbac_access_checks():
    # Test document metadata check function
    public_doc = {"access_level": "Public", "department": "HR", "allowed_roles": ["Admin", "HR"]}
    internal_doc = {"access_level": "Internal", "department": "Finance", "allowed_roles": ["Admin", "Finance"]}
    confidential_doc = {"access_level": "Confidential", "department": "HR", "allowed_roles": ["Admin", "HR"]}
    restricted_doc = {"access_level": "Restricted", "department": "Finance", "allowed_roles": ["Admin", "Finance"]}
    
    # 1. Admin accesses everything
    assert check_document_access("Admin", "General", public_doc) is True
    assert check_document_access("Admin", "General", restricted_doc) is True
    
    # 2. Public / Internal access
    assert check_document_access("Engineering", "Engineering", public_doc) is True
    assert check_document_access("Engineering", "Engineering", internal_doc) is True
    
    # 3. Confidential access
    # Allowed role checks
    assert check_document_access("HR", "Marketing", confidential_doc) is True
    # Department checks
    assert check_document_access("Marketing", "HR", confidential_doc) is True
    # Non-authorized
    assert check_document_access("Engineering", "Engineering", confidential_doc) is False
    
    # 4. Restricted access (Role must match explicitly, department doesn't bypass)
    assert check_document_access("Finance", "Marketing", restricted_doc) is True
    assert check_document_access("Marketing", "Finance", restricted_doc) is False

def test_query_routing_intent():
    assert detect_query_intent("Where can I find the employee handbook and vacation policies?") == "HR"
    assert detect_query_intent("What is the Q2 gross revenue and profit margin?") == "Finance"
    assert detect_query_intent("Audit logs and IP address of security incident logs") == "Security"
    assert detect_query_intent("What coding standards do we follow for python?") == "General"

def test_rbac_pre_filtering_and_ingestion():
    # Create a dummy test file
    test_file = Path("./data/test_data/raw/test_doc.txt")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("This is a sensitive salary statement of John Doe. Salary is $100,000.")
        
    doc_id = ingest_document(
        file_path=test_file,
        department="HR",
        access_level="Confidential",
        allowed_roles=["Admin", "HR"],
        owner="admin"
    )
    
    all_docs = get_all_documents()
    # Find test document
    test_doc_meta = next((d for d in all_docs if d["document_id"] == doc_id), None)
    assert test_doc_meta is not None
    
    # Test allowed doc ID list compilation
    # Alice (HR) is authorized
    alice_allowed = get_authorized_doc_ids("HR", "HR")
    assert doc_id in alice_allowed
    
    # Bob (Finance) is NOT authorized
    bob_allowed = get_authorized_doc_ids("Finance", "Finance")
    assert doc_id not in bob_allowed

def test_api_endpoints():
    # Test Auth Login API
    res = client.post("/api/v1/auth/login", json={"username": "alice", "password": "alice123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test fetch me details
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "alice"
    
    # Test list docs
    res_docs = client.get("/api/v1/documents", headers=headers)
    assert res_docs.status_code == 200
    assert len(res_docs.json()) > 0

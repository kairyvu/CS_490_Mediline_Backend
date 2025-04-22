import os
from dotenv import load_dotenv
def test_using_test_db(db_engine):
    load_dotenv()
    assert db_engine.url.database == os.getenv("MYSQL_TEST_DATABASE")
import unittest
import pandas as pd
import os
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import DeclarativeBase
from tabular_enhancement_tool.core import ODBCEnhancer


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    role = Column(String)


class TestSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.db_url = "sqlite:///test_sql.db"
        self.engine = create_engine(self.db_url)
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        # Populate test data
        from sqlalchemy.orm import sessionmaker

        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.add(User(id="01", name="Alice", role="Admin"))
        session.add(User(id="02", name="Bob", role="User"))
        session.commit()
        session.close()

        self.df = pd.DataFrame(
            {"id": ["01", "02", "03"], "name": ["Alice", "Bob", "Charlie"]}
        )
        self.mapping = ["id"]

    def tearDown(self):
        self.engine.dispose()
        if os.path.exists("test_sql.db"):
            try:
                os.remove("test_sql.db")
            except Exception:
                pass

    def test_sqlalchemy_enhancer_orm_success(self):
        enhancer = ODBCEnhancer(self.db_url, self.mapping, model=User)
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn("odbc_response", df_enhanced.columns)
        self.assertEqual(df_enhanced.loc[0, "odbc_response"]["role"], "Admin")
        self.assertEqual(df_enhanced.loc[1, "odbc_response"]["role"], "User")
        self.assertTrue(pd.isna(df_enhanced.loc[2, "odbc_response"]))
        self.assertTrue(pd.isna(df_enhanced.loc[0, "exception_summary"]))

    def test_sqlalchemy_enhancer_core_success(self):
        enhancer = ODBCEnhancer(self.db_url, self.mapping, table_name="users")
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn("odbc_response", df_enhanced.columns)
        self.assertEqual(df_enhanced.loc[0, "odbc_response"]["role"], "Admin")
        self.assertEqual(df_enhanced.loc[1, "odbc_response"]["role"], "User")
        self.assertTrue(pd.isna(df_enhanced.loc[2, "odbc_response"]))

    def test_sqlalchemy_enhancer_error(self):
        # Invalid table name - should raise NoSuchTableError during init
        from sqlalchemy.exc import NoSuchTableError

        with self.assertRaises(NoSuchTableError):
            ODBCEnhancer(self.db_url, self.mapping, table_name="non_existent")


if __name__ == "__main__":
    unittest.main()

import unittest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
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
        self.db_path = os.path.join(os.path.dirname(__file__), "test_sql.db")
        self.db_url = f"sqlite:///{self.db_path}"
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
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_sqlalchemy_enhancer_orm_success(self):
        enhancer = ODBCEnhancer(self.db_url, self.mapping, model=User)
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn("role", df_enhanced.columns)
        self.assertEqual(df_enhanced.loc[0, "role"], "Admin")
        self.assertEqual(df_enhanced.loc[1, "role"], "User")
        self.assertTrue(pd.isna(df_enhanced.loc[2, "role"]))
        self.assertTrue(pd.isna(df_enhanced.loc[0, "exception_summary"]))

    def test_sqlalchemy_enhancer_orm_no_flatten(self):
        enhancer = ODBCEnhancer(
            self.db_url, self.mapping, model=User, flatten_response=False
        )
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn("odbc_response", df_enhanced.columns)
        self.assertEqual(df_enhanced.loc[0, "odbc_response"]["role"], "Admin")

    def test_sqlalchemy_enhancer_core_success(self):
        enhancer = ODBCEnhancer(self.db_url, self.mapping, table_name="users")
        df_enhanced = enhancer.process_dataframe(self.df)

        self.assertEqual(len(df_enhanced), 3)
        self.assertIn("role", df_enhanced.columns)
        self.assertEqual(df_enhanced.loc[0, "role"], "Admin")
        self.assertEqual(df_enhanced.loc[1, "role"], "User")
        self.assertTrue(pd.isna(df_enhanced.loc[2, "role"]))

    def test_sqlalchemy_enhancer_error(self):
        # Invalid table name - should raise NoSuchTableError during init
        from sqlalchemy.exc import NoSuchTableError

        with self.assertRaises(NoSuchTableError):
            ODBCEnhancer(self.db_url, self.mapping, table_name="non_existent")

    def test_sqlalchemy_enhancer_row_error(self):
        # Test exception handling in _process_row
        enhancer = ODBCEnhancer(self.db_url, self.mapping, model=User)
        # Mock Session to raise exception during execution
        # We need the mock to NOT raise when called, but when used as context manager or inside
        mock_session_obj = MagicMock()
        # Mock the __enter__ method to return a mock session, then mock its execute to fail
        mock_session_obj.__enter__.return_value = mock_session_obj
        mock_session_obj.execute.side_effect = Exception("Database error")
        with patch(
            "tabular_enhancement_tool.core.Session", return_value=mock_session_obj
        ):
            res = enhancer._process_row(0, self.df.iloc[0])
            self.assertEqual(res["exception_summary"], "Database error")
            self.assertIsNone(res["response"])

    def test_odbcenhancer_missing_mapping(self):
        """Test default mapping if None is provided."""
        enhancer = ODBCEnhancer(self.db_url, None, table_name="users")
        self.assertEqual(enhancer.mapping, [])

    def test_sqlalchemy_enhancer_no_model_no_table(self):
        # Trigger ValueError: Either 'model' or 'table_name' must be provided.
        # We need to bypass the check in __init__ or manually create an object
        enhancer = ODBCEnhancer(self.db_url, self.mapping, table_name="users")
        enhancer._table = None
        enhancer.model = None
        res = enhancer._process_row(0, self.df.iloc[0])
        self.assertEqual(
            res["exception_summary"], "Either 'model' or 'table_name' must be provided."
        )

    def test_base_enhancer_not_implemented(self):
        from tabular_enhancement_tool.core import BaseEnhancer

        base = BaseEnhancer()
        with self.assertRaises(NotImplementedError):
            base._process_row(0, pd.Series())


if __name__ == "__main__":
    unittest.main()

from sqlalchemy import create_engine, insert, Column, MetaData, Table
from sqlalchemy.engine import URL
from sqlalchemy.dialects import postgresql, mysql
import logging

logger = logging.getLogger(__name__)


class SQLConnector:
    def __init__(self, config: dict):

        if config["type"] == "postgresql":
            drivername = "postgresql+psycopg"
        elif config["type"] == "mysql":
            drivername = "mysql+pymysql"

        url = URL.create(
            drivername=drivername,
            username=config["username"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
            database=config["database"],
        )

        connection_args = {}
        if "certificate" in config:
            connection_args["ssl"] = {"ca": config["certificate"]}

        self.engine = create_engine(url, connect_args=connection_args, execution_options={
                                    "isolation_level": "AUTOCOMMIT"})
        self.metadata = MetaData()

    def insert(self, table: str, data: list, schema: str = None) -> int | None:
        """Insert data into the specified table.
        Args:
            schema (str): The name of the schema to which the table belongs.
            table (str): The name of the table into which to insert data.
            data (list): A list of dictionaries representing the rows and data to insert.
        Returns:
            int | None: The number of rows inserted, or None if no data is provided.
        """
        if not data:
            return

        columns = list(data[0].keys())

        table_obj = Table(table, self.metadata, *
                          [Column(col) for col in columns], schema=schema)

        dialect = self.engine.dialect.name
        if dialect == "postgresql":
            stmt = postgresql.insert(table_obj).values(
                data).on_conflict_do_nothing()
        elif dialect == "mysql":
            stmt = mysql.insert(table_obj).values(data).prefix_with("IGNORE")
        else:
            logger.warning(
                f"Unsupported database dialect '{dialect}'. Defaulting to standard insert without conflict handling.")
            stmt = insert(table_obj).values(data)

        try:
            with self.engine.begin() as conn:
                result = conn.execute(stmt)
                return result.rowcount
        except Exception as e:
            if "duplicate" in str(e).lower():
                logger.warning(
                    f"Duplicate entry error while inserting into {table}: {e}")
                return result.rowcount if result else None
            raise

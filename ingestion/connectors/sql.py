from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)


class SQLConnector:
    def __init__(self, config: dict):

        if config["type"] == "postgresql":
            url = URL.create(
                drivername="postgresql+psycopg",
                username=config["username"],
                password=config["password"],
                host=config["host"],
                port=config["port"],
                database=config["database"],
            )
        elif config["type"] == "mysql":
            url = URL.create(
                drivername="mysql+pymysql",
                username=config["username"],
                password=config["password"],
                host=config["host"],
                port=config["port"],
                database=config["database"],
            )

        connection_args = {}
        if "certificate" in config:
            connection_args["ssl"] = {"ca": config["certificate"]}

        self.engine = create_engine(url, connect_args=connection_args)

    def insert(self, table: str, data: list) -> int | None:
        """Insert data into the specified table.
        Args:
            table (str): The name of the table into which to insert data.
            data (list): A list of dictionaries representing the rows and data to insert.
        Returns:
            int | None: The number of rows inserted, or None if no data is provided.
        """
        if not data:
            return

        columns = list(data[0].keys())
        column_names = ",".join(columns)
        placeholders = ",".join([f":{col}" for col in columns])

        query = text(f"""
            INSERT INTO {table} ({column_names})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """)

        with self.engine.begin() as conn:
            result = conn.execute(query, data)
            return result.rowcount

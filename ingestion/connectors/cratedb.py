from crate import client
import logging

logger = logging.getLogger(__name__)


class CrateDBConnector:
    def __init__(self, config: dict):
        self.connection = client.connect(
            f"https://{config['host']}:{config['port']}",
            username=config["username"],
            password=config["password"],
        )

    def insert(self, table: str, data: list) -> int | None:
        if not data:
            return

        columns = list(data[0].keys())
        column_names = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in columns])

        query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        rows = [[row[col] for col in columns] for row in data]

        cursor = self.connection.cursor()
        try:
            cursor.executemany(query, rows)
            return cursor.rowcount
        finally:
            cursor.close()
            self.connection.close()

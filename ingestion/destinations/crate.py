import logging
from utils.destinations_registry import register_destination
from crate import client

logger = logging.getLogger(__name__)


@register_destination("crate")
def insert_cratedb(config, data):
    if not data:
        return

    connection = client.connect(
        config["host"],
        username=config["username"],
        password=config["password"],
    )

    cursor = connection.cursor()

    table = config["table"]

    columns = list(data[0].keys())
    column_names = ", ".join(columns)

    placeholders = ", ".join(["?"] * len(columns))

    query = f"""
        INSERT INTO {table} ({column_names})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING
    """

    values = [
        tuple(row.get(col) for col in columns)
        for row in data
    ]

    cursor.executemany(query, values)

    connection.commit()

    inserted = cursor.rowcount

    skipped = len(values) - inserted
    if skipped > 0:
        logger.warning(f"Skipped {skipped} duplicate rows in {table}")
    cursor.close()
    connection.close()

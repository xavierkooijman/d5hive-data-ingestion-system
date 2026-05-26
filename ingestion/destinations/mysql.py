import logging
import pymysql
from utils.destinations_registry import register_destination

logger = logging.getLogger(__name__)


@register_destination("mysql")
def insert_mysql(config, data):
    if not data:
        return

    conn_params = {
        "host": config["host"],
        "port": config["port"],
        "user": config["username"],
        "password": config["password"],
        "database": config["database"],
    }

    if "certificate" in config:
        conn_params["ssl_ca"] = config["certificate"]

    conn = pymysql.connect(**conn_params)

    cursor = conn.cursor()
    table = config["table"]

    columns = list(data[0].keys())
    column_names = ",".join(columns)
    placeholders = ",".join(["%s"] * len(columns))

    query = f"""
        INSERT IGNORE INTO {table} ({column_names})
        VALUES ({placeholders})
    """

    values = [
        tuple(row.get(col) for col in columns)
        for row in data
    ]

    cursor.executemany(query, values)

    conn.commit()

    inserted = cursor.rowcount
    skipped = len(values) - inserted
    if skipped > 0:
        logger.warning(f"Skipped {skipped} duplicate rows in {table}")
    cursor.close()
    conn.close()

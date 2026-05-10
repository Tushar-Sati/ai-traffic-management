import pandas as pd
import mysql.connector

from config import Config

CSV_PATH = "dataset/sample_traffic_data.csv"
COLUMNS = [
    "date", "time", "location", "lat", "lng", "weather", "traffic_density",
    "vehicle_count", "speed", "road_condition", "accident"
]


def main():
    df = pd.read_csv(CSV_PATH)
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM traffic_records")
    existing = cur.fetchone()[0]
    if existing:
        print(f"traffic_records already has {existing} rows. Skipping import.")
        cur.close()
        conn.close()
        return

    sql = """
        INSERT INTO traffic_records
        (date, time, location, lat, lng, weather, traffic_density, vehicle_count, speed, road_condition, accident)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    rows = [tuple(row[col] for col in COLUMNS) for _, row in df.iterrows()]
    cur.executemany(sql, rows)
    conn.commit()
    print(f"Imported {cur.rowcount} sample records.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()

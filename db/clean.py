import psycopg2
import time
import requests
import re

def create_table():
    conn = psycopg2.connect(
        dbname="dblang", user="postgres", password="admin", host="localhost"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS poimdm (
            id SERIAL PRIMARY KEY,
            hashed_maid TEXT,
            lat DOUBLE PRECISION,
            lon DOUBLE PRECISION,
            list_poi_name TEXT,
            list_unique_geo_behaviour TEXT,
            many_geo_behaviour TEXT,
            city TEXT
        )
    """)
    print("✅ Table 'poimdm' created or exists")
    conn.commit()
    cur.close()
    conn.close()

def insert_csv():
    conn = psycopg2.connect(
        dbname="dblang", user="postgres", password="admin", host="localhost"
    )
    cur = conn.cursor()
    with open(r"C:\Users\barun\cobaaja\db\df5_with_poi_and_geo_behaviour.csv", "r", encoding="utf-8") as f:
        next(f)  # Skip header
        cur.copy_expert("""
            COPY poimdm(hashed_maid, lat, lon, list_poi_name, list_unique_geo_behaviour, many_geo_behaviour)
            FROM STDIN WITH CSV
        """, f)
    print("✅ CSV data inserted")
    conn.commit()
    cur.close()
    conn.close()

def clean_city_name(name):
    if not name:
        return None
    name = name.strip()
    replacements = {
        "Daerah Khusus Ibukota Jakarta": "Jakarta",
        "Daerah Khusus Yogyakarta": "Yogyakarta"
    }
    for pattern, replacement in replacements.items():
        if name.lower().startswith(pattern.lower()):
            return replacement
    name = re.sub(r"^(Kota|Kab(?:\.|upaten)?|Kab|Daerah Khusus(?: Ibukota)?)\s+", "", name, flags=re.IGNORECASE)
    return name.strip()

def reverse_geocode(lat, lon):
    try:
        resp = requests.get("https://nominatim.openstreetmap.org/reverse", params={
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
            "addressdetails": 1
        }, headers={"User-Agent": "poimdm-geocoder"})
        data = resp.json()
        raw_city = data.get("address", {}).get("city") or \
                   data.get("address", {}).get("town") or \
                   data.get("address", {}).get("village") or \
                   data.get("address", {}).get("county")
        return clean_city_name(raw_city)
    except Exception as e:
        print(f"Reverse geocode error at ({lat}, {lon}): {e}")
        return None

def update_city_column():
    conn = psycopg2.connect(
        dbname="dblang", user="postgres", password="admin", host="localhost"
    )
    cur = conn.cursor()
    cur.execute("SELECT id, lat, lon FROM poimdm WHERE city IS NULL OR city = ''")
    rows = cur.fetchall()
    for row in rows:
        id_, lat, lon = row
        city = reverse_geocode(lat, lon)
        time.sleep(1)  
        if city:
            cur.execute("UPDATE poimdm SET city = %s WHERE id = %s", (city, id_))
            print(f"✅ Updated id {id_} with city: {city}")
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()
    insert_csv()
    update_city_column()

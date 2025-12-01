import sqlite3
DB_NAME = "artes.db"
TABLE_NAME = "artes"
def verify_artes_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        print(f"Verificando la base de datos: {DB_NAME}")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\nTablas en '{DB_NAME}': {tables}")
        if (TABLE_NAME,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            count_in_db = cursor.fetchone()[0]
            print(f"\nNúmero total de registros en la tabla '{TABLE_NAME}': {count_in_db}")
            cursor.execute(f"SELECT pmid, title_e, journal, subtopic FROM {TABLE_NAME} LIMIT 5;")
            sample_rows = cursor.fetchall()
            print(f"\nPrimeros 5 registros de la tabla '{TABLE_NAME}' (incluyendo subtema):")
            for row in sample_rows:
                print(row)
            cursor.execute(f"SELECT subtopic, COUNT(*) FROM {TABLE_NAME} GROUP BY subtopic")
            subtopic_counts = cursor.fetchall()
            print("\nResumen de registros por subtema:")
            if subtopic_counts:
                for row in subtopic_counts:
                    print(f"- {row[0]}: {row[1]} registros")
            else:
                print("No se encontraron subtemas.")
        else:
            print(f"\nLa tabla '{TABLE_NAME}' no se encontró en '{DB_NAME}'.")
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn:
            conn.close()
            print("\nConexión a la base de datos cerrada.")
if __name__ == "__main__":
    verify_artes_database()

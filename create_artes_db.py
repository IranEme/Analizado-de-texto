import pandas as pd
import sqlite3
import re
DATA_FILEPATH = "artwork_data.csv"
DB_NAME = "artes.db"
ARTWORKS_TABLE_NAME = "artes"
KEYWORDS_TABLE_NAME = "subtopic_keywords"
subtopic_map = {
    "Painting": ["paint", "canvas", "panel", "oil", "acrylic", "tempera", "mural", "gouache"],
    "Sculpture": ["sculpture", "bronze", "steel", "stone", "marble", "wood", "metal", "clay", "statue", "installation"],
    "Works on Paper": ["paper", "ink", "graphite", "charcoal", "watercolor", "drawing", "pencil", "pen", "pastel", "crayon"],
    "Print": ["print", "etching", "lithograph", "screenprint", "engraving", "woodcut", "monotype", "aquatint"],
    "Photography": ["photograph", "gelatin", "albumen", "daguerreotype", "silver"],
    "Design": ["design", "architectural", "architecture"],
    "Textile": ["textile", "tapestry", "fabric", "silk", "wool", "cotton"]
}
def categorize_medium(medium):
    if not isinstance(medium, str):
        return "Other"
    medium_lower = medium.lower()
    for subtopic, keywords in subtopic_map.items():
        if any(re.search(r'\b' + keyword + r'\b', medium_lower) for keyword in keywords):
            return subtopic
    return "Other"
def create_database():
    try:
        print(f"Cargando datos desde {DATA_FILEPATH}...")
        df = pd.read_csv(DATA_FILEPATH, low_memory=False)
        print(f"Total de registros cargados: {len(df)}")
    except FileNotFoundError:
        print(f"Error: El archivo de datos '{DATA_FILEPATH}' no fue encontrado.")
        return
    relevant_columns = {
        'id': 'pmid',
        'title': 'title_e',
        'medium': 'journal'
    }
    if not all(col in df.columns for col in relevant_columns.keys()):
        print("Error: El archivo CSV no contiene las columnas esperadas (id, title, medium).")
        return
    artes_df = df[list(relevant_columns.keys())].copy()
    artes_df.rename(columns=relevant_columns, inplace=True)
    print("Clasificando obras en subtemas...")
    artes_df['subtopic'] = artes_df['journal'].apply(categorize_medium)
    artes_df.dropna(subset=['title_e', 'pmid'], inplace=True)
    artes_df.fillna("", inplace=True)
    artes_df['pmid'] = artes_df['pmid'].astype(int)
    print(f"Procesando {len(artes_df)} registros de arte...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {ARTWORKS_TABLE_NAME}")
    cursor.execute(f"""
        CREATE TABLE {ARTWORKS_TABLE_NAME} (
            pmid INTEGER PRIMARY KEY,
            title_e TEXT NOT NULL,
            journal TEXT,
            subtopic TEXT
        )
    """)
    artes_df.to_sql(ARTWORKS_TABLE_NAME, conn, if_exists='append', index=False)
    print(f"Datos de arte insertados en la tabla '{ARTWORKS_TABLE_NAME}'.")
    cursor.execute(f"DROP TABLE IF EXISTS {KEYWORDS_TABLE_NAME}")
    cursor.execute(f"""
        CREATE TABLE {KEYWORDS_TABLE_NAME} (
            keyword TEXT PRIMARY KEY,
            subtopic TEXT NOT NULL
        )
    """)
    keyword_data = []
    for subtopic, keywords in subtopic_map.items():
        for keyword in keywords:
            keyword_data.append((keyword, subtopic))
    cursor.executemany(f"INSERT INTO {KEYWORDS_TABLE_NAME} (keyword, subtopic) VALUES (?, ?)", keyword_data)
    print(f"Diccionario de datos insertado en la tabla '{KEYWORDS_TABLE_NAME}'.")
    conn.commit()
    cursor.execute(f"SELECT subtopic, COUNT(*) FROM {ARTWORKS_TABLE_NAME} GROUP BY subtopic ORDER BY COUNT(*) DESC")
    subtopic_counts = cursor.fetchall()
    print("\nResumen de registros por subtema en la base de datos:")
    for row in subtopic_counts:
        print(f"- {row[0]}: {row[1]} registros")
    conn.close()
    print("\nBase de datos cerrada.")
if __name__ == "__main__":
    create_database()
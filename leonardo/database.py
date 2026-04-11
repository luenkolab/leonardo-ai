import sqlite3
import json


DB_NAME = "leonardo.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            prompt TEXT,
            concept_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("PRAGMA table_info(concepts)")
    concept_columns = [row[1] for row in cursor.fetchall()]
    if "is_favorite" not in concept_columns:
        cursor.execute("ALTER TABLE concepts ADD COLUMN is_favorite INTEGER DEFAULT 0")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept_id INTEGER NOT NULL,
            image_type TEXT NOT NULL,
            prompt TEXT,
            image_data BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("PRAGMA table_info(project_images)")
    image_columns = [row[1] for row in cursor.fetchall()]
    if "is_favorite" not in image_columns:
        cursor.execute("ALTER TABLE project_images ADD COLUMN is_favorite INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


def save_concept(title, category, prompt, concept_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO concepts (
            title, category, prompt, concept_json
        )
        VALUES (?, ?, ?, ?)
    """, (
        title,
        category,
        prompt,
        json.dumps(concept_data, ensure_ascii=False),
    ))

    concept_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return concept_id


def get_concepts(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, category, created_at, is_favorite
        FROM concepts
        ORDER BY is_favorite DESC, created_at DESC, id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_concept(concept_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM concepts WHERE id = ?", (concept_id,))

    conn.commit()
    conn.close()


def get_concept_by_id(concept_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT concept_json FROM concepts WHERE id = ?",
        (concept_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        import json
        return json.loads(row[0])

    return None


def save_image_asset(concept_id, image_type, prompt, image_bytes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO project_images (concept_id, image_type, prompt, image_data)
        VALUES (?, ?, ?, ?)
    """, (
        concept_id,
        image_type,
        prompt,
        image_bytes,
    ))

    conn.commit()
    conn.close()


def get_images_for_concept(concept_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, image_type, prompt, image_data, created_at, is_favorite
        FROM project_images
        WHERE concept_id = ?
        ORDER BY is_favorite DESC, created_at DESC, id DESC
    """, (concept_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_image_asset(image_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM project_images WHERE id = ?", (image_id,))

    conn.commit()
    conn.close()


def toggle_concept_favorite(concept_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE concepts
        SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (concept_id,))

    conn.commit()
    conn.close()


def toggle_image_favorite(image_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE project_images
        SET is_favorite = CASE WHEN is_favorite = 1 THEN 0 ELSE 1 END
        WHERE id = ?
    """, (image_id,))

    conn.commit()
    conn.close()


def get_all_images():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, concept_id, image_type, prompt, image_data, created_at, is_favorite
        FROM project_images
        ORDER BY is_favorite DESC, created_at DESC, id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_favorite_images():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, concept_id, image_type, prompt, image_data, created_at, is_favorite
        FROM project_images
        WHERE is_favorite = 1
        ORDER BY created_at DESC, id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_images_by_type(image_type):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, concept_id, image_type, prompt, image_data, created_at, is_favorite
        FROM project_images
        WHERE image_type = ?
        ORDER BY is_favorite DESC, created_at DESC, id DESC
    """, (image_type,))

    rows = cursor.fetchall()
    conn.close()
    return rows
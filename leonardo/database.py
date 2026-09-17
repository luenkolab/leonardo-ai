import sqlite3
import json
from pathlib import Path

from categories import normalize_category, require_category_key
from i18n import DEFAULT_LANGUAGE, normalize_language


DB_PATH = Path(__file__).resolve().parent / "leonardo.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate_legacy_concept_categories(cursor):
    """Idempotently replace only explicitly mapped legacy category identifiers."""
    cursor.execute("SELECT id, category FROM concepts ORDER BY id")
    migrated = []
    unresolved = []
    for concept_id, stored_category in cursor.fetchall():
        canonical_category = normalize_category(stored_category)
        if canonical_category is None:
            unresolved.append((concept_id, stored_category))
            continue
        if canonical_category != stored_category:
            cursor.execute(
                "UPDATE concepts SET category = ? WHERE id = ?",
                (canonical_category, concept_id),
            )
            migrated.append((concept_id, stored_category, canonical_category))
    return migrated, unresolved


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
    if "concept_language" not in concept_columns:
        cursor.execute("ALTER TABLE concepts ADD COLUMN concept_language TEXT")
    if "is_published" not in concept_columns:
        cursor.execute(
            "ALTER TABLE concepts "
            "ADD COLUMN is_published INTEGER NOT NULL DEFAULT 0"
        )

    migrate_legacy_concept_categories(cursor)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concept_translations (
            concept_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            translated_content TEXT NOT NULL
                CHECK (json_valid(translated_content)),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (concept_id, language_code),
            FOREIGN KEY (concept_id)
                REFERENCES concepts(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engineering_parameter_sets (
            concept_id INTEGER PRIMARY KEY,
            parameters_json TEXT NOT NULL
                CHECK (json_valid(parameters_json)),
            source_language TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (concept_id)
                REFERENCES concepts(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("PRAGMA table_info(engineering_parameter_sets)")
    engineering_parameter_columns = [row[1] for row in cursor.fetchall()]
    if "source_language" not in engineering_parameter_columns:
        cursor.execute(
            "ALTER TABLE engineering_parameter_sets ADD COLUMN source_language TEXT"
        )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS engineering_parameter_translations (
            concept_id INTEGER NOT NULL,
            language_code TEXT NOT NULL,
            translated_json TEXT NOT NULL CHECK (json_valid(translated_json)),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (concept_id, language_code),
            FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
        )
    """)

    cursor.execute(
        """
        UPDATE concepts
        SET concept_language = 'en'
        WHERE id = 19
          AND title = 'AquaClean Station'
          AND concept_language IS NULL
        """
    )
    cursor.execute(
        """
        UPDATE concepts
        SET concept_language = 'ru'
        WHERE id = 23
          AND title = 'Модульная система аварийных мостов'
          AND concept_language IS NULL
        """
    )

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


def save_concept(
    title,
    category,
    prompt,
    concept_data,
    concept_language=DEFAULT_LANGUAGE,
):
    category = require_category_key(category)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO concepts (
            title, category, prompt, concept_json, concept_language
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        category,
        prompt,
        json.dumps(concept_data, ensure_ascii=False),
        normalize_language(concept_language),
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


def get_concept_language(concept_id):
    """Return the stored language code, or None for a legacy concept."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT concept_language FROM concepts WHERE id = ?",
        (concept_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return None
    return normalize_language(row[0])


def get_concept_prompt(concept_id):
    """Return the original user prompt stored with a concept."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prompt FROM concepts WHERE id = ?", (concept_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def set_concept_published(concept_id, is_published):
    """Set Marketplace publication state without copying concept content."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE concepts SET is_published = ? WHERE id = ?",
        (1 if is_published else 0, concept_id),
    )
    changed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def is_concept_published(concept_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_published FROM concepts WHERE id = ?",
        (concept_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False


def get_published_concepts():
    """Return only explicitly published concepts for Marketplace mapping."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, category, concept_json, concept_language, created_at
        FROM concepts
        WHERE is_published = 1
        ORDER BY created_at DESC, id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_published_concept_by_id(concept_id):
    """Return one published concept row, or None when absent/unpublished."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, category, concept_json, concept_language, created_at
        FROM concepts
        WHERE id = ? AND is_published = 1
        """,
        (concept_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_concept_translation(concept_id, language_code):
    """Return parsed cached translation content, or None when absent."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT translated_content
        FROM concept_translations
        WHERE concept_id = ? AND language_code = ?
        """,
        (concept_id, normalize_language(language_code)),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        value = json.loads(row[0])
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Stored concept translation is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Stored concept translation must be a JSON object")
    return value


def save_concept_translation(concept_id, language_code, translated_content):
    """Atomically insert or replace one concept/language translation."""
    serialized = json.dumps(translated_content, ensure_ascii=False)
    parsed = json.loads(serialized)
    if not isinstance(parsed, dict):
        raise ValueError("Concept translation must be a JSON object")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO concept_translations (
            concept_id, language_code, translated_content
        )
        VALUES (?, ?, ?)
        ON CONFLICT(concept_id, language_code) DO UPDATE SET
            translated_content = excluded.translated_content,
            updated_at = CURRENT_TIMESTAMP
        """,
        (concept_id, normalize_language(language_code), serialized),
    )
    conn.commit()
    conn.close()


def get_engineering_parameter_set(concept_id):
    """Return one concept-owned engineering parameter set, if it exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT parameters_json
        FROM engineering_parameter_sets
        WHERE concept_id = ?
        """,
        (concept_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None
    try:
        value = json.loads(row[0])
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Stored engineering parameter set is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Stored engineering parameter set must be a JSON object")
    return value


def get_engineering_parameter_set_source_language(concept_id):
    """Return the source language recorded for an engineering parameter set."""
    conn = get_connection()
    row = conn.execute(
        "SELECT source_language FROM engineering_parameter_sets WHERE concept_id = ?",
        (concept_id,),
    ).fetchone()
    conn.close()
    return normalize_language(row[0] if row and row[0] else DEFAULT_LANGUAGE)


def save_engineering_parameter_set(concept_id, parameter_set, source_language=None):
    """Atomically persist one structured parameter set for a concept."""
    serialized = json.dumps(parameter_set, ensure_ascii=False)
    parsed = json.loads(serialized)
    if not isinstance(parsed, dict):
        raise ValueError("Engineering parameter set must be a JSON object")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO engineering_parameter_sets (
            concept_id, parameters_json, source_language
        )
        VALUES (?, ?, ?)
        ON CONFLICT(concept_id) DO UPDATE SET
            parameters_json = excluded.parameters_json,
            source_language = COALESCE(
                excluded.source_language,
                engineering_parameter_sets.source_language
            ),
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            concept_id,
            serialized,
            normalize_language(source_language) if source_language else None,
        ),
    )
    cursor.execute(
        "DELETE FROM engineering_parameter_translations WHERE concept_id = ?",
        (concept_id,),
    )
    conn.commit()
    conn.close()


def get_engineering_parameter_translation(concept_id, language_code):
    """Return a cached engineering parameter translation, if available."""
    conn = get_connection()
    row = conn.execute(
        """
        SELECT translated_json
        FROM engineering_parameter_translations
        WHERE concept_id = ? AND language_code = ?
        """,
        (concept_id, normalize_language(language_code)),
    ).fetchone()
    conn.close()
    if not row:
        return None
    value = json.loads(row[0])
    if not isinstance(value, dict):
        raise ValueError("Engineering parameter translation must be a JSON object")
    return value


def save_engineering_parameter_translation(concept_id, language_code, translated):
    """Atomically cache one translated engineering parameter set."""
    serialized = json.dumps(translated, ensure_ascii=False)
    if not isinstance(json.loads(serialized), dict):
        raise ValueError("Engineering parameter translation must be a JSON object")
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO engineering_parameter_translations (
            concept_id, language_code, translated_json
        )
        VALUES (?, ?, ?)
        ON CONFLICT(concept_id, language_code) DO UPDATE SET
            translated_json = excluded.translated_json,
            updated_at = CURRENT_TIMESTAMP
        """,
        (concept_id, normalize_language(language_code), serialized),
    )
    conn.commit()
    conn.close()


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


def get_images_for_concept_by_types(concept_id, image_types):
    """Return concept-owned image records for the requested slot types."""
    requested_types = tuple(image_types)
    if concept_id is None or not requested_types:
        return []

    placeholders = ", ".join("?" for _ in requested_types)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT id, concept_id, image_type, prompt, image_data, created_at, is_favorite
        FROM project_images
        WHERE concept_id = ?
          AND image_type IN ({placeholders})
        ORDER BY created_at DESC, id DESC
        """,
        (concept_id, *requested_types),
    )

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

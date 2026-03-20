import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from bot.config import DATABASE_URL
from bot.services.embeddings import embedder

logger = logging.getLogger(__name__)

# Кэш для mapping строковых состояний на id
_difficulty_cache = None

def _get_difficulty_map():
    global _difficulty_cache
    if _difficulty_cache is None:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM psychological_difficulties")
        _difficulty_cache = {row[1].lower(): row[0] for row in cur.fetchall()}
        cur.close()
        conn.close()
    return _difficulty_cache

def get_difficulty_id(difficulty_name: str):
    if not difficulty_name:
        return None
    name_lower = difficulty_name.lower()
    return _get_difficulty_map().get(name_lower)

def get_recommendations(content_type: str, query_text: str, difficulty_name: str = None, limit: int = 5):
    """
    content_type: 'book' или 'movie'
    """
    # 1. Получаем эмбеддинг запроса
    query_embedding = embedder.get_embedding(query_text)

    # 2. Получаем difficulty_id (если задано)
    difficulty_id = get_difficulty_id(difficulty_name) if difficulty_name else None

    # 3. Определяем таблицу и поля
    if content_type == 'book':
        table = 'books'
        title_field = 'title'
        author_field = 'author'
        id_field = 'id'
        diff_table = 'books_difficulties'
        fk_field = 'book_id'
    elif content_type == 'movie':
        table = 'movies'
        title_field = 'title'
        author_field = 'director'
        id_field = 'id'
        diff_table = 'movies_difficulty'
        fk_field = 'movies_id'
    else:
        raise ValueError("content_type must be 'book' or 'movie'")

    # 4. SQL запрос
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if difficulty_id is not None:
        # Ищем только контент, связанный с указанной сложностью
        query = f"""
        SELECT 
            {id_field},
            {title_field},
            {author_field},
            description,
            1 - (embedding <=> %s::vector) as similarity
        FROM {table}
        JOIN {diff_table} ON {table}.{id_field} = {diff_table}.{fk_field}
        WHERE {diff_table}.difficulty_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """
        cur.execute(query, (query_embedding, difficulty_id, query_embedding, limit))
    else:
        # Без фильтрации по сложности
        query = f"""
        SELECT 
            {id_field},
            {title_field},
            {author_field},
            description,
            1 - (embedding <=> %s::vector) as similarity
        FROM {table}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """
        cur.execute(query, (query_embedding, query_embedding, limit))

    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def format_recommendations(results, content_type):
    """Форматирует результаты в читаемый текст для Telegram"""
    if not results:
        return "К сожалению, ничего не нашлось. Попробуйте переформулировать запрос."

    if content_type == 'book':
        title_key = 'title'
        author_key = 'author'
        type_name = "книг"
    else:
        title_key = 'title'
        author_key = 'director'
        type_name = "фильмов"

    response = f"📚 **Вот несколько {type_name}, которые могут вам подойти:**\n\n"
    for idx, r in enumerate(results, 1):
        title = r[title_key]
        author = r.get(author_key)
        desc = r.get('description', '')
        similarity = r.get('similarity', 0)  # можно не показывать

        response += f"{idx}. **{title}**"
        if author:
            response += f" — {author}"
        response += f"\n   {desc[:200]}...\n\n"
    return response
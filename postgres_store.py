import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg
from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata
from psycopg.rows import tuple_row
from psycopg.types.json import Json
from pydantic import BaseModel

from request_context import RequestContext
from sample_widget import SampleWidget

class ThreadData(BaseModel):
    thread: ThreadMetadata

class ItemData(BaseModel):
    item: ThreadItem

class AttachmentData(BaseModel):
    attachment: Attachment

class SampleWidgetData(BaseModel):
    widget: SampleWidget

class PostgresStore(Store[RequestContext]):
    """Chat data store backed by Render Postgres."""

    def __init__(self) -> None:
        conninfo = os.getenv("DATABASE_URL")
        if not conninfo:
            raise RuntimeError(
                "DATABASE_URL must be set to connect to Render Postgres."
            )
        self._conninfo: str = conninfo
        self._init_schema()

    @contextmanager
    def _connection(self) -> Iterator[psycopg.Connection]:
        with psycopg.connect(self._conninfo) as conn:
            yield conn

    def _init_schema(self) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS threads (
                        id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        data JSONB NOT NULL,
                        PRIMARY KEY (id, user_id)
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS items (
                        id TEXT PRIMARY KEY,
                        thread_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        data JSONB NOT NULL
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS attachments (
                        id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        data JSONB NOT NULL,
                        PRIMARY KEY (id, user_id)
                    )
                    """
                )

                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS items_thread_user_created_idx
                        ON items (thread_id, user_id, created_at DESC)
                    """
                )

                cur.execute(
                    """
                    CREATE INDEX IF NOT EXISTS threads_user_created_idx
                        ON threads (user_id, created_at DESC)
                    """
                )
            conn.commit()

    async def load_thread(
        self, thread_id: str, context: RequestContext
    ) -> ThreadMetadata:
        user_id = context.user_id

        with self._connection() as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    "SELECT data FROM threads WHERE id = %s AND user_id = %s",
                    (thread_id, user_id),
                )
                row = cur.fetchone()
                if row is None:
                    raise NotFoundError(f"Thread {thread_id} not found")
                return ThreadData.model_validate(row[0]).thread

    async def save_thread(
        self, thread: ThreadMetadata, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO threads (id, user_id, created_at, data)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id, user_id)
                    DO UPDATE SET created_at = EXCLUDED.created_at, data = EXCLUDED.data
                    """,
                    (
                        thread.id,
                        context.user_id,
                        thread.created_at,
                        Json(
                            ThreadData(thread=thread).model_dump(
                                mode="json", round_trip=True
                            )
                        ),
                    ),
                )
            conn.commit()

    async def save_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO items (id, thread_id, user_id, created_at, data)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data,
                        created_at = EXCLUDED.created_at
                    """,
                    (
                        item.id,
                        thread_id,
                        context.user_id,
                        item.created_at,
                        Json(
                            ItemData(item=item).model_dump(
                                mode="json", round_trip=True
                            )
                        ),
                    ),
                )
            conn.commit()

    async def load_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> ThreadItem:
        with self._connection() as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT data
                    FROM items
                    WHERE id = %s AND thread_id = %s AND user_id = %s
                    """,
                    (item_id, thread_id, context.user_id),
                )
                row = cur.fetchone()
                if row is None:
                    raise NotFoundError(
                        f"Item {item_id} not found in thread {thread_id}"
                    )
                return ItemData.model_validate(row[0]).item

    async def delete_thread(
        self, thread_id: str, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM items WHERE thread_id = %s AND user_id = %s",
                    (thread_id, context.user_id),
                )
                cur.execute(
                    "DELETE FROM threads WHERE id = %s AND user_id = %s",
                    (thread_id, context.user_id),
                )
            conn.commit()

    async def delete_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM attachments WHERE id = %s AND user_id = %s",
                    (attachment_id, context.user_id),
                )
            conn.commit()

    async def delete_thread_item(
        self, thread_id: str, item_id: str, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM items
                    WHERE id = %s AND thread_id = %s AND user_id = %s
                    """,
                    (item_id, thread_id, context.user_id),
                )
            conn.commit()
    async def add_thread_item(
        self, thread_id: str, item: ThreadItem, context: RequestContext
    ) -> None:
        # For compatibility; implement as alias for save_item.
        await self.save_item(thread_id, item, context)

    async def load_attachment(
        self, attachment_id: str, context: RequestContext
    ) -> Attachment:
        with self._connection() as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                cur.execute(
                    """
                    SELECT data
                    FROM attachments
                    WHERE id = %s AND user_id = %s
                    """,
                    (attachment_id, context.user_id),
                )
                row = cur.fetchone()
                if row is None:
                    raise NotFoundError(
                        f"Attachment {attachment_id} not found"
                    )
                return Attachment.model_validate(row[0]['attachment'])

    async def save_attachment(
        self, attachment: Attachment, context: RequestContext
    ) -> None:
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO attachments (id, user_id, data)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id, user_id)
                    DO UPDATE SET data = EXCLUDED.data
                    """,
                    (
                        attachment.id,
                        context.user_id,
                        Json({"attachment": attachment.model_dump(mode="json", round_trip=True)}),
                    ),
                )
            conn.commit()

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: RequestContext
    ) -> Page[ThreadItem]:
        with self._connection() as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                # Pagination support
                order_clause = "ASC" if order == "asc" else "DESC"

                if after:
                    cur.execute(
                        f"""
                        SELECT data FROM items
                        WHERE thread_id = %s AND user_id = %s AND id > %s
                        ORDER BY created_at {order_clause} LIMIT %s
                        """,
                        (thread_id, context.user_id, after, limit + 1)
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT data FROM items
                        WHERE thread_id = %s AND user_id = %s
                        ORDER BY created_at {order_clause} LIMIT %s
                        """,
                        (thread_id, context.user_id, limit + 1)
                    )
                rows = cur.fetchall()
                items = [ItemData.model_validate(row[0]).item for row in rows]

                # Check if there are more items
                has_more = len(items) > limit
                if has_more:
                    items = items[:limit]

                next_cursor = items[-1].id if items and has_more else None
                return Page(data=items, has_more=has_more, after=next_cursor)

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: RequestContext
    ) -> Page[ThreadMetadata]:
        with self._connection() as conn:
            with conn.cursor(row_factory=tuple_row) as cur:
                order_clause = "ASC" if order == "asc" else "DESC"

                if after:
                    cur.execute(
                        f"""
                        SELECT data FROM threads
                        WHERE user_id = %s AND id > %s
                        ORDER BY created_at {order_clause} LIMIT %s
                        """,
                        (context.user_id, after, limit + 1)
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT data FROM threads
                        WHERE user_id = %s
                        ORDER BY created_at {order_clause} LIMIT %s
                        """,
                        (context.user_id, limit + 1)
                    )
                rows = cur.fetchall()
                threads = [ThreadData.model_validate(row[0]).thread for row in rows]

                # Check if there are more threads
                has_more = len(threads) > limit
                if has_more:
                    threads = threads[:limit]

                next_cursor = threads[-1].id if threads and has_more else None
                return Page(data=threads, has_more=has_more, after=next_cursor)
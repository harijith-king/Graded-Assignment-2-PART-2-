"""
singleton_demo.py
Assignment 2 - Task 2.3c
Thread-safe Singleton implementation of DatabaseConnection using the
double-checked locking pattern.
"""

import threading


class DatabaseConnection:
    """
    Ensures exactly ONE DatabaseConnection instance exists for the entire
    application lifecycle, even when multiple threads try to obtain it
    at the same time.

    ------------------------------------------------------------------
    WHY NAIVE LAZY INITIALIZATION IS UNSAFE UNDER CONCURRENCY
    ------------------------------------------------------------------
    A naive (non-thread-safe) lazy Singleton looks like this:

        class DatabaseConnection:
            _instance = None

            @classmethod
            def get_instance(cls):
                if cls._instance is None:          # <-- Thread A checks: None -> True
                    cls._instance = cls()           # <-- Thread B ALSO checks: None -> True
                return cls._instance                #     (before A finishes assigning!)

    The race condition: Thread A and Thread B can both execute the line
    `if cls._instance is None:` at nearly the same moment, before either
    thread has finished constructing and assigning the new instance. The
    CPU can freely interleave/context-switch between threads at that
    point. Both threads see `_instance` as None, so BOTH proceed to call
    `cls()` and construct a brand new DatabaseConnection object. Whichever
    assignment happens last "wins" and becomes `cls._instance` - meaning
    two separate connection objects were created (and one is silently
    discarded/leaked), which completely violates the Singleton guarantee
    of "exactly one instance."

    ------------------------------------------------------------------
    THE FIX: DOUBLE-CHECKED LOCKING
    ------------------------------------------------------------------
    We check `_instance is None` twice: once WITHOUT the lock (fast path,
    so we don't pay the cost of acquiring a lock on every single call once
    the instance already exists), and once again INSIDE the lock (to
    guarantee that only one thread can actually create the instance).
    """

    _instance = None
    _lock = threading.Lock()  # one lock, shared by all threads/instances of this class

    def __new__(cls, *args, **kwargs):
        # ---- First check (no lock held) ----
        # Fast path: if the singleton already exists, skip locking
        # entirely. This matters because acquiring a lock on every call
        # would be wasteful once the instance has already been created.
        if cls._instance is None:
            # ---- Acquire the lock before touching shared state ----
            with cls._lock:
                # ---- Second check (lock held) - the "double check" ----
                # Without this inner check, two threads that BOTH passed
                # the first "if cls._instance is None" check (before
                # either got the lock) would each still create their own
                # instance, one right after another, once each acquires
                # the lock in turn. This inner check ensures that only
                # the FIRST thread to actually hold the lock creates the
                # instance - every other thread that was blocked waiting
                # for the lock will find `cls._instance` already set once
                # it's their turn, and will skip creation.
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._connection = instance._create_connection()
                    cls._instance = instance  # publish the fully-built instance
        return cls._instance

    def _create_connection(self):
        """
        Stand-in for real connection setup (e.g. psycopg2.connect(...),
        a SQLAlchemy engine, or a pooled connection handle). Kept as a
        placeholder string here so this file runs standalone without
        requiring an actual database.
        """
        return "SHARED_DATABASE_CONNECTION_OBJECT"

    def get_connection(self):
        """Returns the single shared connection object (Task 2.3c requirement)."""
        return self._connection


# ==========================================
# Demonstration / self-test
# ==========================================

if __name__ == "__main__":
    results = {}

    def worker(index: int) -> None:
        db = DatabaseConnection()
        results[index] = db

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    distinct_instances = {id(obj) for obj in results.values()}
    print(f"Threads spawned: {len(threads)}")
    print(f"Distinct DatabaseConnection instances created: {len(distinct_instances)}")
    print(f"Shared connection object: {DatabaseConnection().get_connection()}")

    assert len(distinct_instances) == 1, "Singleton violated: multiple instances were created!"
    print("PASS: exactly one DatabaseConnection instance was created across all threads.")

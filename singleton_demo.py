"""
Task 2.3c
"""

import threading
class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()  # one lock, shared by all threads/instances of this class
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Acquire the lock before touching shared state
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._connection = instance._create_connection()
                    cls._instance = instance  # publish the fully-built instance
        return cls._instance

    def _create_connection(self):
        return "SHARED_DATABASE_CONNECTION_OBJECT"
    def get_connection(self):
        return self._connection

#=================================
# Testing
#=================================
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

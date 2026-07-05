"""
Assignment 2 - Task 2.3d
Observer pattern: MarksUpdateNotifier (subject) notifies EmailNotifier and AuditLogNotifier (observers) whenever a student's marks are updated.
"""
from abc import ABC, abstractmethod
from typing import List
# Observer interface
class Observer(ABC):
    """Any class that wants to be notified of a marks update implements this."""

    @abstractmethod
    def update(self, student_id: int, new_marks: float) -> None:
        raise NotImplementedError
    
# Subject: MarksUpdateNotifier
class MarksUpdateNotifier:
    def __init__(self) -> None:
        self._observers: List[Observer] = []
    def register_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    def deregister_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
    def notify_observers(self, student_id: int, new_marks: float) -> None:
        for observer in self._observers:
            observer.update(student_id, new_marks)
class EmailNotifier(Observer):
    """Sends the student (or relevant staff) an email when marks change."""

    def update(self, student_id: int, new_marks: float) -> None:
        # Placeholder for real email-sending logic (e.g. an SMTP call or
        # a call to a third-party email API).
        print(f"[EmailNotifier] Emailing student {student_id}: your new marks are {new_marks}.")
class AuditLogNotifier(Observer):
    """Records an audit trail entry whenever marks are changed."""

    def update(self, student_id: int, new_marks: float) -> None:
        # Placeholder for a real audit log write (e.g. an INSERT into an
        # AuditLog table, or a write to a logging/SIEM service).
        print(f"[AuditLogNotifier] AUDIT: student_id={student_id} marks changed to {new_marks}.")

# =========================================
# Admin Panel usage example
# ==========================================

class AdminPanel:
    def __init__(self, notifier: MarksUpdateNotifier) -> None:
        self._notifier = notifier

    def update_student_marks(self, student_id: int, new_marks: float) -> None:
        # ... business logic / database write to update the student's
        # marks would happen here in a real implementation ...
        print(f"[AdminPanel] Marks for student {student_id} updated to {new_marks} in the database.")
        self._notifier.notify_observers(student_id, new_marks)

# Demonstration
if __name__ == "__main__":
    notifier = MarksUpdateNotifier()

    email_observer = EmailNotifier()
    audit_observer = AuditLogNotifier()

    # Register both observers
    notifier.register_observer(email_observer)
    notifier.register_observer(audit_observer)

    admin_panel = AdminPanel(notifier)

    print("--- Update #1: both observers registered ---")
    admin_panel.update_student_marks(student_id=101, new_marks=78.5)

    # Deregister the email observer and update marks again
    print("\n--- Deregistering EmailNotifier ---")
    notifier.deregister_observer(email_observer)

    print("\n--- Update #2: only AuditLogNotifier should fire ---")
    admin_panel.update_student_marks(student_id=101, new_marks=82.0)

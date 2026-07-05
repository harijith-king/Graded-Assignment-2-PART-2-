"""
lld_classes.py
Assignment 2 - Task 2.3a-b
Student class, Enrollment class hierarchy, and EnrollmentRepository interface.

SOLID principles applied in this file (each is called out again inline
at the exact line/decision that embodies it):

  - SRP (Single Responsibility Principle): Student only manages student
    data. It has no methods for sending notifications - that
    responsibility belongs to EmailNotifier / AuditLogNotifier
    (see observer_demo.py), not to Student.

  - OCP (Open/Closed Principle): Enrollment is open for extension via
    subclassing (e.g. WaitlistedEnrollment below) without modifying the
    base Enrollment class itself.

  - LSP (Liskov Substitution Principle): WaitlistedEnrollment can be used
    anywhere an Enrollment is expected (e.g. passed to
    EnrollmentRepository.save()) without breaking the caller's
    expectations, because it only overrides behaviour, not the contract.

  - ISP (Interface Segregation Principle): EnrollmentRepository exposes
    only the small set of methods an Enrollment actually needs for
    persistence (save/find/delete) - it is not bloated with unrelated
    methods (e.g. student CRUD, notification, reporting).

  - DIP (Dependency Inversion Principle): Enrollment depends on the
    EnrollmentRepository *abstraction*, not on any concrete database
    class. See the class docstring on Enrollment and the explanation
    at the bottom of this file for Task 2.3b.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


# ==========================================
# Student class (Task 2.3a)
# ==========================================

class Student:
    """
    Represents a student's core academic record.

    SRP: This class's single responsibility is holding and managing
    student data (id, name, department, advisor). It intentionally has
    NO method for sending email notifications - that responsibility is
    delegated to a separate observer class (EmailNotifier). If Student
    grew an email-sending method, the class would then have two reasons
    to change: (1) student data rules changing, and (2) notification/
    email formatting changing - which is exactly what SRP says to avoid.
    """

    def __init__(
        self,
        student_id: int,
        student_name: str,
        department: str,
        advisor_name: str,
    ) -> None:
        self.student_id: int = student_id
        self.student_name: str = student_name
        self.department: str = department
        self.advisor_name: str = advisor_name

    def get_student_id(self) -> int:
        return self.student_id

    def get_student_name(self) -> str:
        return self.student_name

    def get_department(self) -> str:
        return self.department

    def update_department(self, new_department: str) -> None:
        self.department = new_department

    def update_advisor(self, new_advisor_name: str) -> None:
        self.advisor_name = new_advisor_name

    def __repr__(self) -> str:
        return (
            f"Student(student_id={self.student_id!r}, "
            f"student_name={self.student_name!r}, "
            f"department={self.department!r}, "
            f"advisor_name={self.advisor_name!r})"
        )


# ==========================================
# EnrollmentRepository interface (Task 2.3b)
# ==========================================

class EnrollmentRepository(ABC):
    """
    Abstraction that any concrete storage mechanism for Enrollment objects
    must implement (e.g. PostgresEnrollmentRepository, InMemoryEnrollmentRepository
    used in unit tests, MySQLEnrollmentRepository, etc.)

    Method signatures only - no implementation, as required by Task 2.3b.

    ISP: this interface only contains the operations an Enrollment needs
    for persistence. It does not also expose unrelated operations like
    "sendEmail" or "createStudent" - callers that only need enrollment
    persistence are never forced to depend on methods they don't use.
    """

    @abstractmethod
    def save(self, enrollment: "Enrollment") -> None:
        """Insert or update the given enrollment in storage."""
        raise NotImplementedError

    @abstractmethod
    def find_by_student(self, student_id: int) -> List["Enrollment"]:
        """Return all enrollments belonging to the given student."""
        raise NotImplementedError

    @abstractmethod
    def find_by_course(self, course_code: str) -> List["Enrollment"]:
        """Return all enrollments for the given course."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, student_id: int, course_code: str) -> None:
        """Remove the enrollment identified by (student_id, course_code)."""
        raise NotImplementedError


# ==========================================
# Enrollment class hierarchy (Task 2.3a)
# ==========================================

class Enrollment:
    """
    Represents a student's enrollment in a course.

    DIP (Dependency Inversion Principle - Task 2.3b):
    Enrollment depends on the EnrollmentRepository ABSTRACTION (the
    interface above), which is injected through the constructor, rather
    than depending on a concrete database class (e.g. PostgresConnection)
    directly. Enrollment (a high-level module containing business rules)
    and any concrete repository implementation (a low-level module doing
    the actual SQL work) both depend on the EnrollmentRepository
    abstraction, instead of Enrollment depending directly on a low-level
    detail. This means the concrete repository can be swapped (real
    Postgres repository in production, an in-memory fake in unit tests)
    without ever changing a single line of the Enrollment class.

    OCP (Open/Closed Principle):
    This class is closed for modification but open for extension.
    get_status() and describe() are written so that a subclass like
    WaitlistedEnrollment (below) can override them to introduce new
    behaviour (a new enrollment status) WITHOUT touching this class at
    all. There is no "if enrollment_type == 'waitlisted'" branch inside
    this class - new enrollment types are added purely through
    inheritance.
    """

    def __init__(
        self,
        student_id: int,
        course_code: str,
        enrollment_year: int,
        repository: EnrollmentRepository,
        marks_obtained: Optional[float] = None,
    ) -> None:
        self.student_id: int = student_id
        self.course_code: str = course_code
        self.enrollment_year: int = enrollment_year
        self.marks_obtained: Optional[float] = marks_obtained
        self._repository: EnrollmentRepository = repository  # injected abstraction (DIP)

    def get_status(self) -> str:
        """Overridable hook - base implementation returns 'ACTIVE'."""
        return "ACTIVE"

    def update_marks(self, marks: float) -> None:
        if not (0 <= marks <= 100):
            raise ValueError("marks must be between 0 and 100")
        self.marks_obtained = marks

    def is_passing(self, pass_mark: float = 35.0) -> bool:
        return self.marks_obtained is not None and self.marks_obtained >= pass_mark

    def save(self) -> None:
        """
        Persists this enrollment via the injected EnrollmentRepository
        abstraction. Enrollment never imports or references a concrete
        database driver directly - that's the DIP payoff.
        """
        self._repository.save(self)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(student_id={self.student_id!r}, "
            f"course_code={self.course_code!r}, "
            f"enrollment_year={self.enrollment_year!r}, "
            f"marks_obtained={self.marks_obtained!r}, "
            f"status={self.get_status()!r})"
        )


class WaitlistedEnrollment(Enrollment):
    """
    A new enrollment subtype added purely through inheritance - the base
    Enrollment class above was NOT modified to support this.

    OCP in action: this is the "extension" half of Open/Closed. A student
    on a waitlist has no marks yet and a different status; that's captured
    entirely by overriding get_status() here.

    LSP in action: anywhere an Enrollment is expected (e.g.
    EnrollmentRepository.save(enrollment: Enrollment)), a
    WaitlistedEnrollment can be substituted without breaking the caller,
    because it honours the same method contracts as its parent.
    """

    def get_status(self) -> str:
        return "WAITLISTED"

    def is_passing(self, pass_mark: float = 35.0) -> bool:
        # A waitlisted student has no marks yet by definition.
        return False


# ==========================================
# Task 2.3b - Dependency Inversion Principle explanation
# ==========================================
#
# Without DIP, Enrollment might look like:
#
#     class Enrollment:
#         def save(self):
#             connection = PostgresDatabaseConnection.get_instance()  # concrete class!
#             connection.execute("INSERT INTO Enrollments ...")
#
# Here, the high-level Enrollment class depends directly on a low-level,
# concrete detail (PostgresDatabaseConnection and raw SQL). If the
# university switched databases, or if a test wanted to avoid hitting a
# real database, Enrollment itself would have to change.
#
# With DIP, as implemented above, Enrollment instead depends on the
# EnrollmentRepository *interface*. The interface is the abstraction that
# both sides depend on:
#
#     Enrollment (high-level)  --->  EnrollmentRepository (abstraction)  <---  PostgresEnrollmentRepository (low-level)
#
# This is Dependency INVERSION: instead of the high-level policy
# (Enrollment's business rules) depending on the low-level detail
# (a specific database), the dependency direction is inverted so that
# both depend on a shared abstraction. Enrollment.save() only ever calls
# self._repository.save(self) - it has no idea whether that repository
# is backed by PostgreSQL, MySQL, or an in-memory dictionary used in a
# unit test, and it does not need to.

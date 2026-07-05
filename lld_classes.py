"""
Task 2.3a-b
"""

from abc import ABC, abstractmethod
from typing import List, Optional


# ==========================================
# Student class (Task 2.3a)
# ==========================================
class Student:
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
        return "ACTIVE"
    def update_marks(self, marks: float) -> None:
        if not (0 <= marks <= 100):
            raise ValueError("marks must be between 0 and 100")
        self.marks_obtained = marks
    def is_passing(self, pass_mark: float = 35.0) -> bool:
        return self.marks_obtained is not None and self.marks_obtained >= pass_mark
    def save(self) -> None:
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
    def get_status(self) -> str:
        return "WAITLISTED"
    def is_passing(self, pass_mark: float = 35.0) -> bool:
        # A waitlisted student has no marks yet by definition.
        return False

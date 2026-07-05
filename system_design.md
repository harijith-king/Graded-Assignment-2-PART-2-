====================================================
## Task 2.1 – Requirements and Architecture Choice
====================================================

### a. Functional and Non-Functional Requirements

#### Functional Requirements

1. The system must allow students to log in and view their published marks for each enrolled course.
2. The system must allow students to enroll in and drop courses, subject to seat availability and prerequisite checks.
3. The system must allow administrators to create, update, and deactivate student, course, and faculty records.

#### Non-Functional Requirements

1. **The system must support at least 50,000 concurrent users without significant performance degradation during examination result publication.**
   - **Design Principle:** Scalability

2. **The system must remain available with minimal downtime during peak usage periods.**
   - **Design Principle:** Availability

3. **The system must protect student records, login credentials, and personal information from unauthorized access.**
   - **Design Principle:** Security

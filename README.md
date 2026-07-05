# Graded-Assignment-2-PART-2-
---

## Task 2.1 - Architecture Decisions

SARS uses a microservices architecture with three independent services: Authentication, Student Portal, and Admin Panel.
Scalability: Enables independent deployment and horizontal scaling of the high-traffic Student Portal to handle 50,000 concurrent users during result publication.
Resilience: Provides fault isolation, ensuring a failure in one service does not take down the others, maximizing system availability.

***SOLID Principles Applied***

Single Responsibility Principle (SRP): The Student class solely manages student data; email notifications are offloaded to dedicated observer classes.

Open/Closed Principle (OCP): The Enrollment class allows extension via subclasses like WaitlistedEnrollment without altering the base code.

Liskov Substitution Principle (LSP): WaitlistedEnrollment can seamlessly replace an Enrollment object without breaking program behavior.

Interface Segregation Principle (ISP): EnrollmentRepository defines only essential enrollment operations, avoiding bloated, unused methods.

Dependency Inversion Principle (DIP): Enrollment depends on the abstract EnrollmentRepository interface rather than a concrete database implementation, simplifying testing and maintenance.

---

===================================
## Task 2.3(d) – Observer Pattern
===================================

The Observer pattern keeps the Admin Panel loosely coupled from the notification services. The Admin Panel only sends a notification to the `MarksUpdateNotifier` without knowing which services receive it. The `EmailNotifier` and `AuditLogNotifier` register themselves as observers and are notified automatically whenever student marks are updated. New notification services can be added or removed without modifying the Admin Panel, making the system easier to maintain and extend.

============================================
## Task 2.4 – Redundancy and Fault Tolerance
============================================

### a. Database Tier Redundancy

To prevent data loss and improve availability, SARS uses a **primary-replica database architecture**. The primary server handles all write operations, while read requests can be served by both the primary and replica servers to reduce load. If the primary server fails, one of the replicas is promoted as the new primary. After failover, all read and write requests are redirected to the new primary, allowing the system to continue with minimal downtime.

---

### b. Fault Isolation in Microservices

The property that makes this possible is **Fault Isolation**. In a microservices architecture, each service runs independently, so if the Email Notification Service fails, the Student Portal continues to function normally. In a monolithic application, all modules run in the same process, so a failure in the email module could affect the entire application.

To prevent failure propagation, the Student Portal should handle email-service failures using **exception handling with fallback** and **request timeouts**. This ensures that students can still view marks and enroll in courses even if the Email Service is unavailable.

---

### c. Synchronous Replication and Failover
With **synchronous replication**, the primary server waits for the replica to acknowledge every write before confirming it to the application. This increases **write latency** compared to asynchronous replication but ensures the replica always has the latest committed data.

If the primary server fails, the promoted replica contains all committed transactions. Students reading from the new primary see the latest consistent data. Before declaring the system fully consistent, the DBA checks the **Write-Ahead Log (WAL)** or binary log for any missing transactions, applies them if possible, and then creates a new replica to restore redundancy.

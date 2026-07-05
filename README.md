# Graded-Assignment-2-PART-2-
---

===================================
## Task 2.3(d) – Observer Pattern
===================================

The Observer pattern keeps the Admin Panel loosely coupled from the notification services. The Admin Panel only sends a notification to the `MarksUpdateNotifier` without knowing which services receive it. The `EmailNotifier` and `AuditLogNotifier` register themselves as observers and are notified automatically whenever student marks are updated. New notification services can be added or removed without modifying the Admin Panel, making the system easier to maintain and extend.

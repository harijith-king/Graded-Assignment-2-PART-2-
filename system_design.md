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

### b. Monolithic vs. Microservices Architecture

| Dimension | Monolithic Architecture | Microservices Architecture |
|------------|-------------------------|----------------------------|
| **Independent Deployment** | The entire application is deployed as a single unit. Updating one module requires redeploying the whole application. | Each service can be developed, tested, and deployed independently without affecting other services. |
| **Fault Isolation** | A failure in one module can affect the entire application because all modules run together. | A failure in one service is isolated, allowing other services to continue operating normally. |
| **Management Complexity** | Easier to develop and manage because there is a single codebase and deployment process. | More complex to manage due to multiple services, inter-service communication, and distributed monitoring. |

**Recommendation: Microservices Architecture**
SARS should use microservices to handle 50,000 concurrent users during result publication. This allows the high-traffic Student Portal to scale independently without wasting resources on the Authentication or Admin services. It also ensures fault isolation—so one service failing won't bring down the whole system. While more complex to manage, the benefits to scalability, availability, and independent deployment outweigh the complexity.

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

===================================================
## Task 2.2 — High-Level Design
===================================================
### a. Main Components

| Component | Single Responsibility | Interface Exposed |
|---|---|---|
| **API Gateway / Load Balancer** | Single entry point for all client traffic; routes incoming requests to the correct backend service and distributes load across instances. | HTTPS/REST endpoint facing the client (browser/mobile app). |
| **Authentication Service** | Verifies user credentials, issues and validates session tokens (e.g. JWTs), enforces login/logout. | REST API (e.g. `POST /login`, `POST /validate-token`, `POST /logout`) consumed by the other services and the gateway. |
| **Student Portal Service** | Handles all student-facing operations: viewing published marks and enrolling in or dropping courses. | REST API (e.g. `GET /marks`, `POST /enroll`) exposed to the frontend; calls the Authentication Service's REST API to validate tokens. |
| **Admin Panel Service** | Handles administrative CRUD operations on students, courses, and faculty records. | REST API (e.g. `POST /students`, `PUT /courses/{id}`) exposed to the admin frontend; also validates tokens via the Authentication Service. |
| **Database / Persistence Layer** | Stores and retrieves all persistent data (Students, Courses, Enrollments, Advisors, Instructors) as designed in Part 1. | Database query interface (SQL over a connection pool), accessed only through each service's own data access layer — never directly by another service. |
| **Shared Session/Cache Store** | Holds authentication session state so that any web server instance can validate a logged-in user (see 2.2e). | Key-value query interface (e.g. Redis `GET`/`SET` over TCP), accessed by the Authentication Service and the API Gateway. |

---

### b. Layered Architecture — Student Portal Module
| Layer | What it does | Receives | Passes on |
|--------|--------------|----------|-----------|
| **Presentation Layer** | Validates HTTP requests and converts responses into JSON format. | Raw HTTP request (headers, body, authentication token). | Validated request object to the Business Layer; JSON response to the client. |
| **Business Layer** | Applies business rules (such as prerequisite and seat availability checks) and coordinates data processing. | Validated request object from the Presentation Layer. | Data access parameters to the Data Access Layer; success or failure result back to the Presentation Layer. |
| **Data Access Layer** | Executes SQL queries, maps database records to domain objects, and manages transactions. | Query parameters from the Business Layer. | SQL queries to the database; retrieved records or domain objects back to the Business Layer. |

---
### c. Scaling Strategy for Web Servers

**Recommendation: Horizontal scaling** (adding more web server instances) rather than vertical scaling (making a single server bigger).

Reasoning:

Vertical Scaling: Limited by a hard ceiling on CPU, memory, and network. It cannot handle the 50,000 concurrent user spike on result day and requires downtime to resize.

Horizontal Scaling: No hard ceiling; capacity expands seamlessly by adding commodity instances behind a load balancer without downtime.

Fault Tolerance: Eliminates a single point of failure. If one instance crashes, the load balancer reroutes traffic to the surviving instances.
Microservices Synergy: Allows individual services (like the high-traffic Student Portal) to scale independently.

***Load-Balancing Algorithm: Least Connections***

Unlike Round Robin—which distributes traffic sequentially regardless of server load—Least Connections routes requests to the server with the fewest active connections. This is critical for SARS because Student Portal requests vary in cost (e.g., viewing marks is a fast read, while course enrollment requires heavy business-logic and DB writes). Least Connections dynamically adapts to this imbalance, preventing already-busy servers from becoming overloaded.

---

### d. Elasticity for Cost Reduction

Elasticity means the number of running web server instances is not fixed — it automatically grows and shrinks in response to real-time demand, instead of being permanently provisioned for the worst-case load.

* **Off-peak (e.g. semester break):** Traffic is low and steady, so an auto-scaling policy keeps only a small baseline number of instances running (just enough to handle routine admin and low-volume student traffic). Since cloud infrastructure is typically billed per instance-hour, running fewer instances directly reduces cost during these long stretches of low demand.
* **Peak (e.g. exam result day):** The auto-scaling policy monitors a metric such as CPU utilization, request queue length, or requests-per-second. When that metric crosses a threshold, new web server instances are launched automatically and registered with the load balancer within minutes, scaling out to meet the surge in demand from 50,000 concurrent users.
* Once the surge subsides (results have been viewed by most students and traffic drops back to normal), the same policy scales the instance count back down, so the university is not paying for peak-day capacity for the remaining months of the semester.

This "pay only for what you use" model is the core cost advantage of elasticity over provisioning a fixed number of servers sized for the worst case year-round.

---

### e. Session Routing Problem

**Problem: Session Affinity (Distributed Session Problem)**

When multiple web servers are used, a user's session is usually stored in the local memory of the server where they logged in. If a load balancer routes the user's next request to a different server, that server cannot find the session and treats the user as unauthenticated, forcing them to log in again.

#### Strategy 1 – Routing-based: Sticky Sessions

The load balancer ensures that all requests from the same user are always routed to the same backend server, usually by using cookies.

**Trade-off:** Sticky sessions can lead to uneven load distribution because many users may be assigned to the same server. If that server fails, all active sessions stored on it are lost, requiring users to log in again.

#### Strategy 2 – Storage-based: Centralized Session Store

Instead of storing sessions in each server's local memory, session data is stored in a shared session store (such as Redis) that every web server can access. This allows any server to validate a user's session.

**Trade-off:** Every authenticated request requires an additional network call to the shared session store, which increases response time slightly. The shared session store must also be highly available because its failure would affect authentication across the entire system, increasing infrastructure cost and complexity.

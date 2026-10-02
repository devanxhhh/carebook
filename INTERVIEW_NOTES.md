# Interview Notes: Engineering Decisions

These notes summarize the rationale behind key technical choices made in the CareBook backend assignment.

### 1. Why FastAPI?
FastAPI is excellent for modern Python backends because it provides automatic validation and serialization via Pydantic, built-in OpenAPI/Swagger documentation, and excellent performance. Its dependency injection system keeps route handlers clean and testable.

### 2. Why PostgreSQL?
PostgreSQL provides strong guarantees around ACID compliance, concurrent transaction handling, and advanced constraints (like `UNIQUE` indexing). It is crucial for financial or booking systems where data integrity and race-condition prevention are more important than sheer write-throughput.

### 3. Why SQLAlchemy?
SQLAlchemy is the industry standard ORM for Python. It abstracts SQL complexities while allowing fine-grained control over transactions and session management. SQLAlchemy 2.0 provides modern declarative models that type-hint well with Pydantic.

### 4. Why CentreTest instead of putting price on Test?
Prices in healthcare often vary by location due to varying operational costs. If `price` was placed on the `DiagnosticTest` model, every centre would be forced to charge the exact same amount for a test. The `CentreTest` association table allows Center A and Center B to offer the exact same "Lipid Profile" at different prices.

### 5. Why store amount on Booking?
The price of a test might change next month. If a booking relies dynamically on the current `CentreTest.price`, historical receipts and booking records would visually change when the admin updates catalogue prices. Copying the value into `Booking.amount` at creation acts as an immutable snapshot of what the user agreed to pay.

### 6. How JWT authentication works
When a user logs in with valid credentials, the server generates a JSON Web Token (JWT) containing their `user_id` and `role`. This token is cryptographically signed using a secret key (`JWT_SECRET`). On subsequent requests, the server verifies the signature to ensure it hasn't been tampered with, extracting the user identity without querying the database for credentials.

### 7. How authorization works
Authorization is handled via FastAPI dependencies. 
- `get_current_user` decodes the JWT to identify the requester.
- `get_current_admin_user` wraps the above but raises a `403 Forbidden` if the `role` is not `ADMIN`.
- In service layers (like `get_booking`), the query explicitly applies `.filter(Booking.user_id == current_user.id)` for normal users, preventing IDOR (Insecure Direct Object Reference) vulnerabilities.

### 8. How webhook idempotency works
Webhook idempotency guarantees that even if a payment gateway sends the same event 10 times, our system only transitions state once. We insert a record into the `WebhookEvent` table for every incoming payload using the gateway's unique `event_id`.

### 9. Why event_id has a UNIQUE constraint
Application-level checks (e.g., `if event_exists: return`) are vulnerable to race conditions if two identical requests arrive at the exact same millisecond. By enforcing a `UNIQUE` index on `event_id` directly in PostgreSQL, the database guarantees that the second request will throw an `IntegrityError`, which we safely catch and ignore.

### 10. How duplicate webhook requests are handled
If an `IntegrityError` is thrown during the webhook event insertion, we immediately roll back the transaction and return an HTTP 200 `already_processed` response to the provider. We do not re-process the booking or payment state.

### 11. How payment and booking state transitions work
State transitions follow a strict logic policy. 
- `PENDING` -> `SUCCESS` updates the booking to `CONFIRMED`.
- `PENDING` -> `FAILED` updates the booking to `FAILED`.
- A failed webhook arriving after a successful payment (stale event) is ignored and does not downgrade the `SUCCESS` state.

### 12. How transactions prevent inconsistent state
When creating a booking, we generate both a `Booking` record and a `Payment` record within the same service call. Both `db.add()` calls add objects to the same SQLAlchemy session. The `db.flush()` after the `Booking` is used only to obtain the auto-generated `booking.id` (required to set `Payment.booking_id`) — it writes to the database but **does not commit**. The single `db.commit()` at the end of the function writes both the `Booking` and `Payment` together in one atomic database transaction. If anything fails before `commit()` — such as a validation error, a database constraint violation, or an application exception — neither record is persisted. This guarantees that a `Booking` without a corresponding `Payment` can never exist.

### 13. How concurrent payment requests are handled
The database unique constraints and transaction isolation levels manage concurrency. Webhooks are serialized by the `event_id` constraint. Explicit locking (`with_for_update()`) could be added if inventory (time slots) were strictly limited.

### 14. Why soft deletion is used for centres/tests
If an admin physically deletes a `DiagnosticCentre`, any historical `Booking` referencing that centre via a Foreign Key would either be deleted (CASCADE) or cause a database error. Using `is_active=False` (soft deletion) hides the centre from new searches while preserving historical data.

### 15. What happens if a webhook arrives twice
The first request inserts the `WebhookEvent` and updates the payment. The second request hits the `UNIQUE` constraint, throws an `IntegrityError`, and the application safely returns a successful 200 response to acknowledge the event without modifying state again.

### 16. What happens if a failed webhook arrives after a successful payment
The service explicitly checks the current state: `if payment.status != PaymentStatus.SUCCESS: payment.status = PaymentStatus.FAILED`. Since the payment is already successful, it bypasses the downgrade and retains the successful state.

### 17. What would be changed for production
For a real production environment, I would add:
- A genuine payment gateway SDK (Stripe/Razorpay).
- Proper database pooling and connection management (e.g., PgBouncer).
- A message queue (Celery + Redis) for background tasks (email receipts, notifications).
- Explicit row-level locking during high-contention slot booking (`SELECT ... FOR UPDATE`).
- Rate limiting to protect authentication and booking endpoints from abuse.

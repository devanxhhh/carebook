# CareBook

## Overview

CareBook is a diagnostic test booking and simulated payment platform designed for reliability and data integrity. It provides users with the ability to discover diagnostic centres, view available tests with location-specific pricing, book appointments, and process simulated payments safely. 

The architecture is built with a focus on edge-case handling, particularly regarding concurrent webhooks and payment state consistency.

## Features

- **Authentication:** JWT-based user and admin roles.
- **Diagnostic Catalogue:** Admin management of active diagnostic centres, diagnostic tests, and specific pricing per centre (`CentreTest`).
- **Booking Engine:** Secure bookings capturing snapshot pricing at the time of creation to insulate against future catalogue price changes.
- **Payment Simulation:** Simulated payment success/failure using a configurable success rate.
- **Webhook Idempotency:** Concurrency-safe webhook processing with strict state transition rules ensuring `SUCCESS` payments are never downgraded by stale events.
- **Pagination & Search:** Clean API responses with proper pagination metadata.

## Architecture

The application uses a standard layered architecture:
`FastAPI (Routing/Validation)` -> `Service Layer (Business Logic)` -> `SQLAlchemy 2.x (ORM)` -> `PostgreSQL (Database)`

- **Routing:** Handles HTTP requests and integrates Pydantic schemas.
- **Service Layer:** Centralizes domain logic (e.g., booking validation, snapshotting prices) and orchestrates database transactions to avoid bloated endpoints.
- **Alembic:** Used for schema migrations.

## Database Design

The data model ensures strict referential integrity and prevents invalid state:

- **User**: Represents platform users and administrators.
- **DiagnosticCentre & DiagnosticTest**: Represents catalogue items.
- **CentreTest**: An association model linking centres and tests. This is necessary because pricing can vary per location. Storing the price here is superior to a single global price on the `DiagnosticTest` model.
- **Booking**: Represents a user's appointment. The `amount` field is intentionally snapshotted here from `CentreTest.price` at the time of booking so historical bookings are unaffected by future price changes.
- **Payment**: Represents the payment state of a booking. Kept separate from booking for clarity in financial auditing.
- **WebhookEvent**: Records incoming provider webhooks. Uses a `UNIQUE` constraint on `event_id` to provide database-level concurrency safety.

## API Documentation

The full OpenAPI documentation is available via Swagger UI at `/docs` when the server is running.

**Authentication**
- `POST /api/v1/auth/signup` - Public. Creates a user.
- `POST /api/v1/auth/login` - Public. Returns JWT.
- `GET /api/v1/auth/me` - Authenticated. Returns current user profile.

**Diagnostic Centres & Tests**
- `GET /api/v1/centres` - Public. Lists active centres.
- `GET /api/v1/tests` - Public. Lists active tests.

**Bookings**
- `POST /api/v1/bookings` - Authenticated. Creates a booking.
- `GET /api/v1/bookings` - Authenticated. Lists user's bookings.
- `POST /api/v1/bookings/{booking_id}/cancel` - Authenticated. Cancels an eligible booking.

**Payments & Webhooks**
- `POST /api/v1/payments/` - Authenticated. Simulates payment processing.
- `POST /api/v1/payments/webhook/` - Provider webhook. Idempotently processes payment state updates.

## Local Setup

### Requirements
- Python 3.11+
- PostgreSQL (if running locally without Docker)

```bash
# Clone the repository
git clone <repository_url>
cd carebook

# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy example environment configuration
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

## Docker Setup

A complete `docker-compose.yml` is provided for immediate execution with PostgreSQL.

```bash
# Start the API and Database
docker compose up --build -d

# Check the API documentation
# Navigate to http://localhost:8000/docs
```

To run database migrations within the docker container (if not automated in the entrypoint):
```bash
docker compose exec api alembic upgrade head
```

## Environment Variables

See `.env.example`. Critical variables include:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `JWT_SECRET`: Secret key for JWT encoding/decoding. Must be secure in production.
- `ADMIN_EMAIL` / `ADMIN_PASSWORD`: Default admin credentials injected into the database if a seeder is used.
- `PAYMENT_SUCCESS_RATE`: Configurable integer (0-100) for payment simulation probability.

## Testing

Integration tests require a dedicated PostgreSQL database, as defined in `docker-compose.yml` under `test_db`. They do not fall back to SQLite.

```bash
pytest -q
```
*Note: Set `TEST_DATABASE_URL` in the environment or `.env` before running tests. The suite fails immediately if it is missing or is not a PostgreSQL URL.*

## Seeding Admin User

To seed the admin user, run:
```bash
python -m app.seed
```
This is an idempotent script that checks the `ADMIN_EMAIL` and `ADMIN_PASSWORD` in your `.env` file and creates the user securely if it does not already exist.

## Payment Simulation

This project does not connect to a real external payment provider. Calling the `POST /api/v1/payments/` endpoint generates a simulated success or failure based on the `PAYMENT_SUCCESS_RATE` environment variable. 

## Webhook Idempotency

Webhooks received at `POST /api/v1/payments/webhook/` are guaranteed to be processed idempotently.
1. The payload includes an `event_id`.
2. The application attempts to insert a `WebhookEvent` row containing this `event_id`.
3. A `UNIQUE` database constraint safely rejects duplicate concurrent requests with an `IntegrityError`.
4. The API gracefully catches this and returns a safe success response (`already_processed`), preventing duplicate database state transitions and maintaining absolute safety.

## Assumptions

1. Prices are captured at booking creation and do not change retroactively.
2. Payment is simulated and does not require actual credit card payloads.
3. Webhook event IDs (`event_id`) are globally unique per provider payload.
4. Users can only access and modify their own bookings.
5. Admin users manage all catalogue data.
6. A single booking translates to a single appointment slot (slot locking and complex availability logic is simplified for this assignment's scope).
7. Soft-deletion is used for `DiagnosticCentre` and `DiagnosticTest` to preserve historical referential integrity.

## Tradeoffs

- **Rate Limiting / Redis:** Deferred to prioritize database integrity, idempotency, and comprehensive integration testing within the time constraint.
- **Background Jobs:** Webhook processing is handled synchronously within the request cycle since it is a lightweight state transition. A queuing system (Celery/Redis) would add architectural overhead unnecessary for this volume.
- **Frontend UI:** No frontend is included. This submission focuses entirely on completing the backend engineering assignment to the highest standard.

## Future Improvements

- Add a background task queue (Celery) for processing complex webhooks or sending email notifications.
- Implement robust rate-limiting (e.g., using Redis) on the login and booking endpoints.
- Integrate a real payment provider SDK (Stripe/Razorpay).
- Implement explicit calendar slot locking for appointments to prevent overbooking a specific time slot at a specific centre.

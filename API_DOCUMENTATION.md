# Real Estate CRM — API Documentation

This document lists all available API endpoints for the Real Estate CRM system, including request methods, paths, descriptions, and required access roles.

## Authentication & Headers

The API supports two authentication methods depending on the type of user:

### 1. For Regular Users (Agents, Managers, Admins)
Regular users authenticate via username/password to get a short-lived JWT token.
*   **Header Name**: `Authorization`
*   **Header Value**: `Bearer <your_jwt_token>`
*   **Example**:
    ```bash
    curl -H "Authorization: Bearer eyJhbGci..." http://localhost:8000/api/v1/leads/
    ```
*   **How to obtain**: Call the `/api/v1/auth/login` endpoint with your email and password.

### 2. For System/External Users (api_user)
External applications, scripts, or AI agents use a persistent API Key.
*   **Header Name**: `X-API-Key`
*   **Header Value**: `sk_<your_api_key>`
*   **Example**:
    ```bash
    curl -H "X-API-Key: sk_abc123..." http://localhost:8000/api/v1/leads/
    ```
*   **How to obtain**: A Super Admin must generate this for you via the `/api/v1/api-keys/` endpoint (the raw key is shown only once upon creation).

*Note: If both headers are provided in a request, the JWT Bearer token takes precedence.*


---

## 1. Authentication

Endpoints for user registration and login.

### Register a User
*   **URL**: `/api/v1/auth/register`
*   **Method**: `POST`
*   **Access**: Public
*   **Description**: Create a new user account.
*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "full_name": "John Doe",
      "password": "yourpassword",
      "role": "agent" 
    }
    ```
    *Note: Role defaults to `agent` if not specified. Available roles: `super_admin`, `sales_manager`, `agent`, `api_user`.*
*   **Response** (201 Created):
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "agent",
      "is_active": true,
      "created_at": "2026-05-01T12:00:00Z"
    }
    ```

### Login
*   **URL**: `/api/v1/auth/login`
*   **Method**: `POST`
*   **Access**: Public
*   **Description**: Authenticate and receive a JWT access token.
*   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "yourpassword"
    }
    ```
*   **Response** (200 OK):
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1...",
      "token_type": "bearer"
    }
    ```

### Get Current User Profile
*   **URL**: `/api/v1/auth/me`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: Returns the profile of the currently authenticated user.

---

## 2. User Management

Endpoints for managing users (Super Admin only).

### List All Users
*   **URL**: `/api/v1/users/`
*   **Method**: `GET`
*   **Access**: `super_admin`
*   **Description**: Returns a list of all users.

### Get Specific User
*   **URL**: `/api/v1/users/{user_id}`
*   **Method**: `GET`
*   **Access**: `super_admin`, `sales_manager`
*   **Description**: Get details of a specific user.

### Update User Role
*   **URL**: `/api/v1/users/{user_id}/role`
*   **Method**: `PATCH`
*   **Access**: `super_admin`
*   **Description**: Update a user's role.
*   **Request Body**:
    ```json
    {
      "role": "sales_manager"
    }
    ```

### Deactivate User
*   **URL**: `/api/v1/users/{user_id}/deactivate`
*   **Method**: `PATCH`
*   **Access**: `super_admin`
*   **Description**: Deactivates (soft-deletes) a user account.

---

## 3. Leads & Contacts

Manage leads and their interaction timeline.

### Create Lead
*   **URL**: `/api/v1/leads/`
*   **Method**: `POST`
*   **Access**: `super_admin`, `sales_manager`, `api_user`
*   **Description**: Create a new lead.
*   **Request Body**:
    ```json
    {
      "first_name": "Sara",
      "last_name": "Ahmed",
      "phone": "01712345678",
      "email": "sara@example.com",
      "source": "website",
      "preferred_channel": "whatsapp",
      "budget_min": 5000000,
      "budget_max": 8000000,
      "desired_location": "Gulshan",
      "property_type_preference": "apartment"
    }
    ```

### List Leads
*   **URL**: `/api/v1/leads/`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: List leads. Agents see only their assigned leads; Managers/Admins see all.
*   **Query Parameters**: `status`, `source`, `location`, `assigned_agent_id`

### Get Lead Details
*   **URL**: `/api/v1/leads/{lead_id}`
*   **Method**: `GET`
*   **Access**: Authenticated (Owner or Manager+)
*   **Description**: Get lead details including the full activity timeline.

### Update Lead
*   **URL**: `/api/v1/leads/{lead_id}`
*   **Method**: `PATCH`
*   **Access**: Authenticated (Owner or Manager+)
*   **Description**: Update lead details or status.

### Log Activity
*   **URL**: `/api/v1/leads/{lead_id}/activities`
*   **Method**: `POST`
*   **Access**: Authenticated (Owner or Manager+)
*   **Description**: Log an interaction (call, message, viewing, etc.) against a lead.
*   **Request Body**:
    ```json
    {
      "activity_type": "call",
      "description": "Discussed property requirements"
    }
    ```

---

## 4. Property Inventory

Manage property listings.

### Create Property
*   **URL**: `/api/v1/properties/`
*   **Method**: `POST`
*   **Access**: `super_admin`, `sales_manager`
*   **Description**: Create a new property listing.
*   **Request Body**:
    ```json
    {
      "title": "Luxury Apartment",
      "location": "Gulshan",
      "property_type": "apartment",
      "asking_price": 7500000,
      "bedrooms": 3,
      "bathrooms": 2
    }
    ```

### List Properties
*   **URL**: `/api/v1/properties/`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: List properties with support for rich filtering.
*   **Query Parameters**: `status`, `property_type`, `location`, `min_price`, `max_price`, `min_bedrooms`

### Get Property Details
*   **URL**: `/api/v1/properties/{property_id}`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: Get details of a specific property.

### Update Property
*   **URL**: `/api/v1/properties/{property_id}`
*   **Method**: `PATCH`
*   **Access**: `super_admin`, `sales_manager`
*   **Description**: Update property details or status.

### Match Properties for Lead
*   **URL**: `/api/v1/properties/match/{lead_id}`
*   **Method**: `GET`
*   **Access**: Authenticated (Owner or Manager+)
*   **Description**: Matches available properties against a lead's preferences (budget, location, type).

---

## 5. Deals & Pipeline

Manage the sales pipeline.

### Create Deal
*   **URL**: `/api/v1/deals/`
*   **Method**: `POST`
*   **Access**: Authenticated (All Roles)
*   **Description**: Create a deal linking a lead to one or more properties.
*   **Request Body**:
    ```json
    {
      "lead_id": 1,
      "property_ids": [1]
    }
    ```

### List Deals
*   **URL**: `/api/v1/deals/`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: List deals. Scoped by role (Agents see own deals).
*   **Query Parameters**: `stage`, `lead_id`

### Advance Deal Stage
*   **URL**: `/api/v1/deals/{deal_id}/stage`
*   **Method**: `PATCH`
*   **Access**: Authenticated (Owner or Manager+)
*   **Description**: Move a deal to a new stage (forward-only progression).
*   **Request Body**:
    ```json
    {
      "stage": "property_tour"
    }
    ```

---

## 6. Tasks

Manage to-dos linked to leads or deals.

### Create Task
*   **URL**: `/api/v1/tasks/`
*   **Method**: `POST`
*   **Access**: Authenticated (All Roles)
*   **Description**: Create a task.
*   **Request Body**:
    ```json
    {
      "title": "Follow up call",
      "assigned_to_id": 1,
      "lead_id": 1,
      "priority": "high"
    }
    ```

### List Tasks
*   **URL**: `/api/v1/tasks/`
*   **Method**: `GET`
*   **Access**: Authenticated (All Roles)
*   **Description**: List tasks. Filters available for `overdue_only`, `completed`, `priority`.

---

## 7. API Keys

Manage API keys for external applications.

### Create API Key
*   **URL**: `/api/v1/api-keys/`
*   **Method**: `POST`
*   **Access**: `super_admin`
*   **Description**: Generate a new API key for an `api_user`. The full key is returned ONLY once.

### List API Keys
*   **URL**: `/api/v1/api-keys/`
*   **Method**: `GET`
*   **Access**: `super_admin`
*   **Description**: List all API keys.

---

## 8. Webhooks

Manage webhook subscriptions for event notifications.

### Register Webhook
*   **URL**: `/api/v1/webhooks/register`
*   **Method**: `POST`
*   **Access**: `super_admin`
*   **Description**: Subscribe a URL to specific events.
*   **Request Body**:
    ```json
    {
      "url": "https://your-server.com/webhook",
      "event": "new_lead_created"
    }
    ```
    *Available events: `new_lead_created`, `new_lead_assigned`, `deal_stage_changed`, `deal_closed`.*

### Test Webhook
*   **URL**: `/api/v1/webhooks/test/{webhook_id}`
*   **Method**: `POST`
*   **Access**: `super_admin`
*   **Description**: Sends a test payload to verify reachability. Rate limited.

---

## Appendix: Allowed Enum Values

To avoid `422 Unprocessable Entity` errors, ensure you use the exact case-sensitive strings listed below for fields that require Enums.

### Lead Source & Preferred Channel
*   `whatsapp`
*   `telegram`
*   `website`
*   `walk_in`
*   `referral`
*   `other`

### Lead Status
*   `new`
*   `contacted`
*   `qualified`
*   `viewing_scheduled`
*   `offer_made`
*   `cold`

### Property Type Preference
*   `apartment`
*   `villa`
*   `land`
*   `commercial`
*   `any`

### Activity Type
Used when logging activities (`POST /api/v1/leads/{lead_id}/activities`).
*   `call`
*   `message`
*   `email`
*   `viewing`
*   `meeting`
*   `note`


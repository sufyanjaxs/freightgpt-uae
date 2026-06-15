# FreightGPT UAE API Documentation

## Base URL
`https://api.freightgpt.ae/api/v1`

## Authentication

All API requests require JWT authentication via Bearer token.

### Get Token
```
POST /auth/login
Body: { "email": "user@company.com", "password": "..." }
Response: { "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

### Refresh Token
```
POST /auth/refresh
Header: Authorization: Bearer <refresh_token>
Response: { "access_token": "...", "token_type": "bearer" }
```

## Agent System

### Run Agent
```
POST /agents/run
Body: {
  "agent_type": "pricing|sales|dispatch|load_acquisition|market_intelligence|shipper_acquisition|driver_copilot|document_ai|finance|ceo",
  "input_data": { ... }
}
```

### Run Workflow
```
POST /agents/workflow/{workflow_name}
Workflows: acquire_load, dispatch_shipment, process_document, generate_report, onboard_shipper
```

## Load Management

```
GET    /loads         - List loads (paginated, filterable by status)
POST   /loads         - Create load
GET    /loads/{id}    - Get load details
PATCH  /loads/{id}/status - Update load status
POST   /loads/{id}/bids   - Place bid on load
```

## Fleet Management

```
GET    /fleet/trucks          - List all trucks
POST   /fleet/trucks          - Register truck
GET    /fleet/trucks/{id}     - Get truck details
PUT    /fleet/trucks/{id}/location - Update GPS location
GET    /fleet/drivers         - List drivers
POST   /fleet/drivers         - Register driver
GET    /fleet/maintenance     - List maintenance records
POST   /fleet/maintenance     - Create maintenance record
```

## Document Processing

```
GET    /documents          - List documents (filterable)
POST   /documents/upload   - Upload document (multipart)
POST   /documents/{id}/process - AI process document
GET    /documents/{id}     - Get document details
```

## Finance

```
GET    /finance/invoices          - List invoices
POST   /finance/invoices          - Create invoice
GET    /finance/invoices/{id}     - Get invoice
POST   /finance/payments          - Record payment
GET    /finance/payouts           - List payouts
POST   /finance/payouts           - Create payout
GET    /finance/transactions      - List transactions
GET    /finance/profit-analysis   - Get profit analysis
```

## Communications

```
POST   /communications/email       - Send email
POST   /communications/whatsapp    - Send WhatsApp message
POST   /communications/voice/call  - Initiate voice call
GET    /communications/history     - Get communication history
```

## Analytics

```
GET    /analytics/dashboard       - Dashboard summary
GET    /analytics/loads/timeline  - Load volume timeline
GET    /analytics/revenue/timeline - Revenue timeline
GET    /analytics/fleet/status    - Fleet status breakdown
```

## Webhooks

```
POST   /webhooks/stripe        - Stripe payment events
POST   /webhooks/twilio/voice  - Twilio voice events
POST   /webhooks/twilio/status - Twilio message status
POST   /webhooks/gps           - GPS device updates
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Rate Limiting

- Authenticated: 100 requests/minute
- Unauthenticated: 20 requests/minute
- Agent endpoints: 10 requests/minute

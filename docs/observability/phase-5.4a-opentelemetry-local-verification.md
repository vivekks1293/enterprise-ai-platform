# Phase 5.4A - OpenTelemetry Local Verification

**Date:** 2026-08-22  
**Scope:** Verify the existing OpenTelemetry foundation locally  
**Code changes:** None

## 1. Current Configuration

OpenTelemetry is configured in:

`apps/backend/app/core/telemetry/opentelemetry.py`

The application creates:

```python
TracerProvider(
    resource=Resource(...),
    sampler=TraceIdRatioBased(settings.otel_sampling_ratio),
)
```

Current defaults:

```text
otel_sampling_ratio = 1.0
otel_console_exporter = false
```

Resource metadata:

```text
service.name = Enterprise AI Platform
service.version = 0.1.0
deployment.environment = development
```

## 2. Exporter Behavior

The configured exporter is:

```python
BatchSpanProcessor(ConsoleSpanExporter())
```

It is attached only when `otel_console_exporter` is enabled.

No OTLP exporter, collector, Jaeger, or Langfuse exporter is configured.

The console exporter is available in the installed OpenTelemetry SDK but disabled by default.

When export is disabled:

- spans are still created in memory
- no external backend is required
- no spans are printed
- no external telemetry request is made
- trace and span IDs remain available inside active spans
- existing application logging continues to work

## 3. Environment Variables

The settings are controlled through these environment variables:

```text
OTEL_SAMPLING_RATIO
OTEL_CONSOLE_EXPORTER
```

PowerShell example:

```powershell
$env:OTEL_SAMPLING_RATIO = "1.0"
$env:OTEL_CONSOLE_EXPORTER = "true"
```

Set these variables before starting Uvicorn. Settings are loaded when the application is imported.

## 4. Instrumentation Locations

FastAPI instrumentation is registered in:

`apps/backend/app/main.py`

```python
app.add_middleware(RequestCorrelationMiddleware)
FastAPIInstrumentor.instrument_app(app)
```

The application span is created in:

`apps/backend/app/application/ai/orchestrator/ai_orchestrator.py`

```python
with tracer.start_as_current_span("rag.orchestrate"):
    async for event in self._respond(...):
        yield event
```

Expected hierarchy:

```text
HTTP server span
`-- rag.orchestrate
    `-- existing RAG operations
```

A request to `/api/v1/health/live` creates an HTTP span only. A conversation message request that reaches `AIOrchestrator` also creates `rag.orchestrate`.

## 5. Request IDs and Trace IDs

These are separate concepts:

| Identifier | Meaning |
|---|---|
| `request_id` | Application correlation ID from `X-Request-ID` |
| `trace_id` | OpenTelemetry distributed trace identifier |
| `span_id` | Current OpenTelemetry operation identifier |

The existing request ID remains available through the request context and is returned in the `X-Request-ID` response header.

When an active span exists, structured application logs can include:

```text
request_id
trace_id
span_id
```

Trace and span IDs are not metric labels.

## 6. Start the Backend With Tracing Disabled

From the backend directory:

```powershell
Set-Location "d:\AI\enterprise-ai-platform\apps\backend"
$env:OTEL_CONSOLE_EXPORTER = "false"
$env:OTEL_SAMPLING_RATIO = "1.0"
uv run uvicorn app.main:app --reload --port 8000
```

The application should start without requiring a collector, Jaeger, or other telemetry backend.

## 7. Enable Development Console Trace Output

Stop the server with `Ctrl+C`, then start it again in the same PowerShell process:

```powershell
Set-Location "d:\AI\enterprise-ai-platform\apps\backend"
$env:OTEL_CONSOLE_EXPORTER = "true"
$env:OTEL_SAMPLING_RATIO = "1.0"
uv run uvicorn app.main:app --reload --port 8000
```

The exporter uses `BatchSpanProcessor`, so spans may appear after a short batching delay or when the process shuts down.

## 8. Send One Real HTTP Request

The liveness endpoint is unauthenticated and does not depend on the database:

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v1/health/live" `
  -Headers @{ "X-Request-ID" = "11111111-1111-1111-1111-111111111111" }
```

Expected response status:

```text
200 OK
```

Expected response body:

```json
{"status":"UP"}
```

Expected response header:

```text
X-Request-ID: 11111111-1111-1111-1111-111111111111
```

## 9. Verify the HTTP Trace

Look in the terminal running Uvicorn and search for:

```text
GET /api/v1/health/live
```

The console exporter should print a completed HTTP server span containing resource metadata similar to:

```text
service.name: Enterprise AI Platform
service.version: 0.1.0
deployment.environment: development
```

The ASGI instrumentation may also emit internal `send` and `receive` spans. The important server span is the one named:

```text
GET /api/v1/health/live
```

## 10. Verify an Actual RAG Span

The health endpoint verifies FastAPI tracing only. To verify `rag.orchestrate`, use the authenticated conversation endpoint.

The flow is:

```text
POST /api/v1/identity/login
POST /api/v1/conversations
POST /api/v1/conversations/{conversation_id}/messages
```

### Login

Use an existing user account:

```powershell
$loginBody = @{
  email = "your-user@example.com"
  password = "your-password"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/identity/login" `
  -Method Post `
  -ContentType "application/json" `
  -Body $loginBody

$token = $loginResponse.access_token
```

### Create a Conversation

```powershell
$conversationBody = @{
  title = "Telemetry verification"
} | ConvertTo-Json

$conversation = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/conversations" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $conversationBody

$conversationId = $conversation.id
```

### Send One SSE Request

```powershell
$messageBody = @{
  prompt = "What information is available in the knowledge base?"
} | ConvertTo-Json

curl.exe -N `
  -X POST `
  "http://127.0.0.1:8000/api/v1/conversations/$conversationId/messages" `
  -H "Authorization: Bearer $token" `
  -H "X-Request-ID: 22222222-2222-2222-2222-222222222222" `
  -H "Content-Type: application/json" `
  -d $messageBody
```

The `-N` option prevents curl from buffering the SSE stream.

Expected event types:

```text
event: token
event: citations
event: complete
```

In the Uvicorn terminal, search for:

```text
rag.orchestrate
```

## 11. SSE Span Lifetime

The HTTP span should cover the complete response lifecycle:

```text
HTTP span starts
    |
SSE stream starts
    |
token events
    |
citations event
    |
complete event
    |
HTTP span ends
```

The `rag.orchestrate` span wraps the async generator, so it also remains active while the stream yields events.

It should not end merely because the `StreamingResponse` object was created.

## 12. Where Trace Information Appears

Trace information can appear in two places.

### Console exporter

When `OTEL_CONSOLE_EXPORTER=true`, completed span data appears in the Uvicorn terminal after batch processing.

### Application logs

Logs generated inside an active span can include:

```text
request_id='...'
trace_id='...'
span_id='...'
```

Startup and shutdown logs occur outside an active span, so they may contain `request_id=None`, `trace_id=None`, and `span_id=None`.

## 13. Why Nothing May Print

The most common reason is the default setting:

```text
OTEL_CONSOLE_EXPORTER=false
```

In that mode, the application creates spans but attaches no exporter.

Other possible causes:

- the environment variable was set after Uvicorn started
- the sampling ratio is `0`
- the span is still waiting in the batch processor
- the request was sent to `/api/v1/health/live` and `rag.orchestrate` was expected
- output is being viewed in a different terminal from the Uvicorn worker
- the application was started before the environment variables were set

Confirm the effective PowerShell value before starting:

```powershell
$env:OTEL_CONSOLE_EXPORTER
$env:OTEL_SAMPLING_RATIO
```

Expected values for console tracing:

```text
true
1.0
```

## 14. Exact Minimal Verification Procedure

```powershell
Set-Location "d:\AI\enterprise-ai-platform\apps\backend"
$env:OTEL_CONSOLE_EXPORTER = "true"
$env:OTEL_SAMPLING_RATIO = "1.0"
uv run uvicorn app.main:app --reload --port 8000
```

In a second PowerShell terminal:

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:8000/api/v1/health/live" `
  -Headers @{ "X-Request-ID" = "11111111-1111-1111-1111-111111111111" }
```

Then inspect the first terminal for:

```text
GET /api/v1/health/live
```

Verify:

- the HTTP span exists
- the service metadata is present
- the span has non-zero trace and span IDs
- the response contains the supplied `X-Request-ID`

For a complete RAG trace, follow the login, conversation creation, and SSE request steps in Section 10 and search the Uvicorn output for `rag.orchestrate`.

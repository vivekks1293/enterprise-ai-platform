# Phase 5.4 - Observability Backend Readiness Report

**Date:** 2026-08-22  
**Scope:** Architecture and dependency inspection only  
**Code changes:** None

## 1. Current Versions

| Component | Version | Source |
|---|---:|---|
| Python runtime | 3.12.13 | Active backend `.venv` |
| Declared Python requirement | `>=3.10` | `apps/backend/pyproject.toml` |
| FastAPI | 0.139.0 | `pyproject.toml`, `uv.lock` |
| Starlette | 1.3.1 | `uv.lock` |
| structlog | 26.1.0 | `pyproject.toml`, `uv.lock` |
| LangChain | 1.3.14 | Active environment |
| langchain-openai | 1.3.5 | Active environment |
| OpenTelemetry API | 1.44.0 | Transitive/current environment |
| OpenTelemetry SDK | 1.44.0 | Transitive/current environment |
| OTLP gRPC exporter | 1.44.0 | Transitive/current environment |
| OTel semantic conventions | 0.65b0 | Transitive/current environment |
| Langfuse | Not installed | Active environment |

The OpenTelemetry packages are not declared directly by the backend. They are present transitively through ChromaDB 1.5.9.

No `opentelemetry-instrumentation-fastapi` package is installed.

## 2. Required Packages

### FastAPI HTTP tracing

```text
opentelemetry-api
opentelemetry-sdk
opentelemetry-instrumentation-fastapi
```

`opentelemetry-instrumentation-asgi` may be required or brought transitively by the FastAPI instrumentation package.

### Manual application spans

```text
opentelemetry-api
opentelemetry-sdk
```

Manual spans can be created around the RAG orchestration, retrieval, context assembly, prompt construction, and provider stream boundaries.

### Metrics

```text
opentelemetry-api
opentelemetry-sdk
```

For OTLP export, prefer:

```text
opentelemetry-exporter-otlp-proto-http
```

The existing OTLP gRPC exporter should not be selected for direct Langfuse export because Langfuse currently supports OTLP over HTTP/JSON and HTTP/protobuf, not gRPC.

The existing application `MetricsRecorder` should remain the application-facing abstraction. An OpenTelemetry adapter can be added later without coupling RAG code to OpenTelemetry.

## 3. Compatibility Concerns

### Python

The project allows Python 3.10 and newer, while the active environment uses Python 3.12.13. Python 3.12 is appropriate for current OpenTelemetry and Langfuse Python SDK versions.

For production, pin the runtime explicitly after deciding the supported version. Avoid allowing untested Python versions through an open-ended `>=3.10` constraint.

### FastAPI and Starlette

Current versions:

```text
FastAPI 0.139.0
Starlette 1.3.1
```

Instrumentation must be tested against these exact versions for:

- startup and shutdown behavior
- streaming responses
- SSE completion timing
- client disconnects
- provider failures
- exception status propagation
- response header handling

The existing request-correlation middleware wraps the full ASGI request and remains active through streaming. OpenTelemetry middleware must be placed so the HTTP span also covers the full SSE lifetime.

### OpenTelemetry

The current packages are aligned:

```text
opentelemetry-api 1.44.0
opentelemetry-sdk 1.44.0
opentelemetry-semantic-conventions 0.65b0
```

Keep OpenTelemetry packages on a compatible release family. Do not independently upgrade only the API or SDK.

GenAI semantic conventions are still evolving. Use stable application attributes together with standard `gen_ai.*` attributes where supported, and validate backend mappings before relying on them operationally.

### Chroma transitive dependency

ChromaDB currently brings OpenTelemetry packages into the lockfile and environment. This is not an intentional application tracing configuration.

Risks include:

- accidental reliance on transitive packages
- future Chroma upgrades changing those versions
- confusion between installed and configured telemetry
- dependency conflicts when direct instrumentation is added

OpenTelemetry should become an explicit direct dependency only during the implementation phase.

### Langfuse

Langfuse is not installed. Current Langfuse documentation identifies Python SDK v4 as the current SDK line. Current documentation states that self-hosted Langfuse v3/v4 SDK features involving newer Observations and Metrics APIs require a Langfuse server version of at least 3.63.0.

Confirm the exact SDK/server compatibility matrix before deployment.

### Langfuse OTLP transport

Langfuse currently supports:

- OTLP over HTTP/JSON
- OTLP over HTTP/protobuf

Langfuse does not currently support gRPC ingestion. Do not plan on:

```text
OTLP gRPC exporter -> Langfuse
```

## 4. Recommended Architecture

Recommended first production architecture:

```text
FastAPI request
    |
OpenTelemetry HTTP instrumentation
    |
Application root span: rag.orchestrate
    |-- retrieval spans
    |-- context assembly span
    |-- prompt construction span
    `-- LLM generation observation
            |
    Langfuse Python SDK v4
            |
    Langfuse exporter/backend
```

Use OpenTelemetry API/SDK for infrastructure and application tracing. Use Langfuse Python SDK v4 for GenAI-specific observations, generations, usage, prompt metadata, scoring, and Langfuse integration.

Keep the existing `MetricsRecorder` abstraction for application metrics until an actual metrics backend is selected.

Do not export the same spans through two independent Langfuse paths. Avoid simultaneously sending identical application spans through the Langfuse SDK exporter and a direct OTLP exporter to Langfuse.

### Collector option

For multiple telemetry destinations, use:

```text
Application -> OpenTelemetry Collector -> infrastructure backends and Langfuse
```

For the first integration, the smaller application plus Langfuse Python SDK path is preferable. Add a collector when centralized filtering, buffering, sampling, or multi-backend routing is needed.

## 5. Expected Trace/Span Structure

```text
HTTP POST /conversations/{id}/messages
`-- rag.orchestrate
    |-- retrieval
    |   |-- retrieval.semantic_search
    |   |-- retrieval.keyword_search
    |   |-- retrieval.hybrid_rrf
    |   `-- retrieval.reranking
    |-- context.assembly
    |-- prompt.construction
    `-- llm.generation
```

### Root request attributes

- service name
- environment
- deployment version
- HTTP method and route template
- status code
- request outcome
- correlation ID as trace/log metadata, not a metric label
- pseudonymous session or user reference only if approved by privacy policy

### Retrieval attributes

- retrieval mode
- configured top-k
- candidate count
- result count
- semantic, keyword, and fused candidate counts
- reranker type
- reranker input/output counts
- duration

### Context assembly attributes

- candidate count
- selected count
- excluded count
- duplicate count
- estimated token count
- configured budget
- duration

### Prompt construction attributes

- message count
- role summary
- context item count
- estimated input size
- duration

### LLM generation attributes

- provider
- model
- time to first token
- total generation duration
- token-event count
- completion status
- actual provider usage, only when supplied by the provider

The provider call should become a Langfuse generation observation or equivalent GenAI span nested beneath `rag.orchestrate`.

## 6. Logging Compatibility

The current logging system is partially compatible with trace/span IDs.

Existing capabilities:

- standard Python logging
- structlog
- contextvars
- request-scoped `request_id`
- structured key-value rendering

Current gap:

- no OpenTelemetry trace context is read
- no `trace_id` or `span_id` is added to log records
- no OpenTelemetry logging handler is configured

The existing logging architecture should be extended rather than replaced. Add trace/span fields to the existing logging context once OpenTelemetry is introduced.

Do not use trace IDs as metric labels.

## 7. Langfuse Capabilities

Current Langfuse Python integration supports:

### Traces

- root traces based on OpenTelemetry context
- nested observations
- trace names
- sessions and user metadata
- tags, versions, releases, environments, and metadata

### Generations

Generation observations support:

- model
- model parameters
- input and output
- usage details
- cost details
- completion timing
- status and errors

### Provider and model metadata

Generation observations can carry provider/system, model name, model parameters, and invocation metadata. The application should pass provider and model explicitly because the current provider abstraction does not expose every provider field uniformly.

### Token usage

Langfuse supports token usage and cost tracking when actual usage is available. The current streaming path exposes token events but not provider token usage. Do not invent prompt or completion token counts.

### Prompt and response capture

Langfuse supports input and output capture, but this application should not send full prompt or response content by default because it handles enterprise knowledge and conversation history. Content capture should be opt-in, redacted, sampled, and governed by retention policy.

### Evaluations

Langfuse supports:

- scores and custom scores
- human annotations
- code evaluators
- LLM-as-a-judge workflows
- datasets and experiments
- evaluation APIs and SDK workflows

These belong to later generation-evaluation phases.

## 8. Data That Should Be Sent

Recommended default data:

- trace name
- environment
- service/version/release
- provider and model
- retrieval mode
- stage durations
- candidate/result/selected counts
- reranker type and counts
- context budget and selected count
- generation status
- fallback status
- TTFT
- total generation duration
- token-event count
- actual provider usage when available
- safe error type and stage
- controlled tags such as environment, release, and retrieval mode

Potentially permitted subject to policy:

- pseudonymous user ID
- conversation/session ID
- request ID as trace metadata, never as a metric dimension

## 9. Data That Should Not Be Sent by Default

Do not send by default:

- API keys
- JWTs
- authorization headers
- request bodies
- full user questions
- full conversation history
- full system prompts
- full retrieved document content
- full model responses
- embedded vectors
- document text
- sensitive filenames or document identifiers
- raw retrieval queries
- secrets contained in prompts or responses

The Phase 5.1 safe logging policy must also apply to Langfuse. Observability must not bypass application privacy controls.

## 10. Proposed Implementation Order

1. Pin the supported production Python version.
2. Add direct, compatible OpenTelemetry API/SDK dependencies.
3. Add FastAPI instrumentation and verify SSE lifecycle behavior.
4. Add trace/span ID injection to the existing logging context.
5. Add a root HTTP/RAG span.
6. Add manual spans around retrieval, RRF, reranking, context assembly, prompt construction, and provider streaming.
7. Preserve the existing `MetricsRecorder` abstraction.
8. Add an OpenTelemetry metrics adapter only after selecting a metrics backend.
9. Add Langfuse Python SDK v4.
10. Create Langfuse generation observations around provider generation.
11. Add provider/model and actual usage metadata.
12. Add privacy filtering and content-capture configuration.
13. Validate nesting, SSE completion, client disconnects, provider failures, and exporter shutdown.
14. Add Langfuse evaluations in the later generation-evaluation phase.

## 11. Final Recommendation

Use OpenTelemetry for HTTP and infrastructure/application tracing, together with the Langfuse Python SDK v4 for GenAI-specific observability. Let both share the same OpenTelemetry context.

Do not install anything or modify dependency files until the supported Python version, Langfuse server target, OTLP transport, export path, and privacy policy are agreed.

## References

- Langfuse Python SDK: https://langfuse.com/docs/sdk/python
- Langfuse SDK overview: https://langfuse.com/docs/observability/sdk/overview
- Langfuse OpenTelemetry integration: https://langfuse.com/integrations/native/opentelemetry
- Langfuse evaluation overview: https://langfuse.com/docs/evaluation/overview
- OpenTelemetry Python instrumentation: https://opentelemetry.io/docs/languages/python/instrumentation/
- OpenTelemetry Python exporters: https://opentelemetry.io/docs/languages/python/exporters/

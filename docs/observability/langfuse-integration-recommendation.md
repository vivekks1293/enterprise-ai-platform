# Langfuse Integration Recommendation

## Recommended Langfuse SDK and Version

Use the **Langfuse Python SDK v4**.

Langfuse is not currently installed. Before production deployment, confirm the exact SDK/server compatibility matrix. Current Langfuse documentation indicates that newer Observations and Metrics APIs require a self-hosted Langfuse server version of `>=3.63.0`.

## OpenTelemetry vs Langfuse SDK

Use both, with separate responsibilities:

- **OpenTelemetry** for HTTP, infrastructure, and application tracing.
- **Langfuse Python SDK v4** for GenAI-specific observations, generations, model metadata, usage, cost, prompt metadata, and evaluations.

Both should share the same OpenTelemetry context so Langfuse generation observations remain nested under the application trace.

Do not export identical spans through both a Langfuse exporter and a direct OTLP-to-Langfuse path, since that can create duplicate observations.

## Dependency Changes

Add:

```text
langfuse
```

Already present in the project:

```text
opentelemetry-api==1.44.0
opentelemetry-sdk==1.44.0
opentelemetry-instrumentation-fastapi>=0.65b0
```

No collector or Prometheus dependency is required initially.

For direct Langfuse OTLP export, use HTTP/JSON or HTTP/protobuf. Do not use the currently available OTLP gRPC exporter for Langfuse ingestion.

## Proposed Trace and Generation Structure

```text
HTTP request
└── rag.orchestrate
    ├── rag.retrieval
    │   ├── rag.retrieval.semantic
    │   ├── rag.retrieval.keyword
    │   ├── rag.retrieval.hybrid_rrf
    │   └── rag.reranking
    ├── rag.context_assembly
    ├── rag.prompt_construction
    └── rag.llm_generation
```

The `rag.llm_generation` span should be represented as a Langfuse generation observation containing, where available:

- provider
- model
- model parameters
- time to first token
- total generation duration
- completion outcome
- actual token usage
- actual cost information

Do not invent token usage when the provider does not expose it.

## Required Environment Variables

Langfuse credentials and endpoint:

```text
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
LANGFUSE_BASE_URL
```

Recommended application controls:

```text
LANGFUSE_ENABLED=false
LANGFUSE_CAPTURE_CONTENT=false
```

For Langfuse Cloud, use the appropriate regional base URL. For self-hosted Langfuse, use the internal deployment URL.

Telemetry should remain disabled or best-effort when Langfuse credentials are absent or invalid.

## Privacy and Content Capture

Keep content capture disabled by default:

```text
LANGFUSE_CAPTURE_CONTENT=false
```

Do not send the following by default:

- full user prompts
- full conversation history
- full system prompts
- full retrieved documents
- full generated responses
- raw retrieval queries
- API keys
- JWTs
- authorization headers
- secrets
- embeddings
- sensitive document identifiers

Safe metadata may include:

- provider
- model
- retrieval mode
- candidate/result/selected counts
- stage durations
- time to first token
- generation outcome
- citation count
- actual provider token usage, when available
- pseudonymous session or user identifiers, if approved by policy

Development content capture may be enabled explicitly, but only with redaction, restricted access, sampling, and retention controls.

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

from app.application.ai.services.prompt_logger import PromptLogger
from app.application.ai.services.retrieval_logger import RetrievalLogger
from app.application.conversation.exceptions import ConversationNotFoundError
from app.application.knowledge.contracts.chunk_metadata import ChunkMetadata
from app.application.knowledge.contracts.retrieved_chunk import RetrievedChunk
from app.application.knowledge.contracts.vector_search_result import (
    VectorSearchResult,
)
from app.core.exceptions.handlers import register_exception_handlers
from app.core.logging.logger import (
    configure_logging,
    log_event,
    request_id_context,
)
from app.core.middleware.request_correlation import RequestCorrelationMiddleware
from app.domain.ai.models.chat_message import ChatMessage
from app.domain.ai.models.chat_request import ChatRequest
from app.domain.conversation.enums.message_role import MessageRole


REQUEST_ID = "11111111-1111-1111-1111-111111111111"
SECOND_REQUEST_ID = "22222222-2222-2222-2222-222222222222"
DOCUMENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
OWNER_ID = UUID("33333333-3333-3333-3333-333333333333")


def setup_function() -> None:
    logging.getLogger().setLevel(logging.INFO)


def create_test_app() -> FastAPI:
    configure_logging()
    app = FastAPI()
    app.add_middleware(RequestCorrelationMiddleware)
    register_exception_handlers(app)

    @app.get("/inspect")
    async def inspect(request: Request):
        log_event(logging.getLogger(__name__), "application.inspected")
        return {
            "state_request_id": request.state.request_id,
            "context_request_id": request_id_context.get(),
        }

    @app.get("/failure")
    async def failure():
        raise ConversationNotFoundError()

    @app.get("/stream")
    async def stream():
        async def events():
            yield "first\n"
            await asyncio.sleep(0)
            log_event(logging.getLogger(__name__), "stream.finished")
            yield "last\n"

        return StreamingResponse(events(), media_type="text/plain")

    return app


def event_records(caplog, event: str):
    return [record for record in caplog.records if record.getMessage() == event]


def test_missing_request_id_generates_and_propagates_an_id(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(create_test_app())

    response = client.get("/inspect")

    request_id = response.headers["X-Request-ID"]
    assert UUID(request_id)
    assert response.json() == {
        "state_request_id": request_id,
        "context_request_id": request_id,
    }
    assert event_records(caplog, "application.inspected")[0].request_id == request_id


def test_valid_request_id_is_reused_in_response_and_logs(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(create_test_app())

    response = client.get("/inspect", headers={"X-Request-ID": REQUEST_ID})

    assert response.headers["X-Request-ID"] == REQUEST_ID
    assert response.json()["state_request_id"] == REQUEST_ID
    assert event_records(caplog, "request.started")[0].request_id == REQUEST_ID
    assert event_records(caplog, "request.completed")[0].request_id == REQUEST_ID


def test_request_ids_do_not_leak_between_concurrent_requests(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(create_test_app())

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda request_id: client.get(
                    "/inspect",
                    headers={"X-Request-ID": request_id},
                ),
                [REQUEST_ID, SECOND_REQUEST_ID],
            )
        )

    assert {response.json()["context_request_id"] for response in responses} == {
        REQUEST_ID,
        SECOND_REQUEST_ID,
    }
    assert {record.request_id for record in event_records(caplog, "application.inspected")} == {
        REQUEST_ID,
        SECOND_REQUEST_ID,
    }


def test_exception_log_is_correlated_and_omits_sensitive_request_content(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(create_test_app())
    sensitive_value = "do-not-log-this-question"

    response = client.get(
        "/failure",
        headers={"X-Request-ID": REQUEST_ID, "X-Sensitive": sensitive_value},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "ConversationNotFound"
    record = event_records(caplog, "request.failed")[0]
    assert record.request_id == REQUEST_ID
    assert record.exception_type == "ConversationNotFoundError"
    assert sensitive_value not in str(record.__dict__)


def test_sse_completion_is_logged_after_stream_finishes_with_same_request_id(caplog):
    caplog.set_level(logging.INFO)
    client = TestClient(create_test_app())

    response = client.get("/stream", headers={"X-Request-ID": REQUEST_ID})

    assert response.text == "first\nlast\n"
    finished_index = next(
        index
        for index, record in enumerate(caplog.records)
        if record.getMessage() == "stream.finished"
    )
    completed_index = next(
        index
        for index, record in enumerate(caplog.records)
        if record.getMessage() == "request.completed"
    )
    assert finished_index < completed_index
    assert caplog.records[completed_index].request_id == REQUEST_ID


def test_safe_prompt_and_retrieval_logs_exclude_content(caplog):
    caplog.set_level(logging.INFO)
    prompt_secret = "prompt-secret-should-not-appear"
    query_secret = "query-secret-should-not-appear"
    chunk_secret = "chunk-secret-should-not-appear"
    request = ChatRequest(
        messages=[
            ChatMessage(role=MessageRole.USER, content=prompt_secret),
        ]
    )
    result = VectorSearchResult(
        chunks=[
            RetrievedChunk(
                content=chunk_secret,
                metadata=ChunkMetadata(
                    document_id=DOCUMENT_ID,
                    filename="private.pdf",
                    chunk_id="private-chunk",
                    chunk_index=0,
                    page_number=1,
                    owner_id=OWNER_ID,
                ),
                score=0.9,
            )
        ]
    )

    PromptLogger.log(request, context_item_count=1, duration_ms=2.5)
    RetrievalLogger.log(
        query=query_secret,
        result=result,
        retrieval_mode="semantic",
        candidate_count=1,
        top_k=5,
        duration_ms=3.5,
    )

    prompt_record = event_records(caplog, "prompt.constructed")[0]
    retrieval_record = event_records(caplog, "retrieval.completed")[0]
    assert prompt_record.message_count == 1
    assert prompt_record.context_item_count == 1
    assert retrieval_record.retrieval_mode == "semantic"
    assert retrieval_record.result_count == 1
    assert retrieval_record.query_length == len(query_secret)
    assert len(retrieval_record.query_hash) == 64
    captured = "\n".join(str(record.__dict__) for record in caplog.records)
    assert prompt_secret not in captured
    assert query_secret not in captured
    assert chunk_secret not in captured
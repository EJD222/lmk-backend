import os
from sqlalchemy.orm import Session as DBSession
from fastapi import BackgroundTasks

from app.db import SessionLocal
from app.models.session import Session
from app.models.participant import Participant
from app.schemas.session import CreateSessionRequest, CreateSessionResponse

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class SessionService:
    @staticmethod
    def create(
        db: DBSession,
        body: CreateSessionRequest,
        background_tasks: BackgroundTasks,
    ) -> CreateSessionResponse:
        # Step 1: insert session with host_id=NULL, flush to get session.id
        session = Session(
            topic=body.topic,
            context=body.context,
            expected_count=body.expected_count,
        )
        db.add(session)
        db.flush()

        # Step 2: insert host participant, flush to get host.id
        host = Participant(
            session_id=session.id,
            display_name=body.host_display_name,
        )
        db.add(host)
        db.flush()

        # Step 3: backfill the circular FK now that both IDs exist
        session.host_id = host.id
        db.commit()

        background_tasks.add_task(
            generate_questions,
            str(session.id),
            body.topic,
            body.context,
            body.host_notes,
        )

        return CreateSessionResponse(
            session_id=str(session.id),
            host_participant_id=str(host.id),
            join_link=f"{FRONTEND_URL}/join/{session.id}",
        )


def generate_questions(
    session_id: str,
    topic: str,
    context: str | None,
    host_notes: str | None,
) -> None:
    # TODO: A4 — OpenAI Call 1, validate mechanic order + Other/Any, save to DB
    pass

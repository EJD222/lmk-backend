import json
import uuid as _uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from app.constants import RESULT_TYPE_ORDER, ResultType
from app.models.participant import Participant
from app.models.result import Result
from app.models.session import Session
from app.schemas.ai import AIResult
from app.schemas.result import ResultOut, ResultsResponse, SessionMeta
from app.utils.http import HTTPErrorMessage, HTTPStatusCode


class ResultService:
    @staticmethod
    def save_results(
        db: DBSession, 
        session_id: str, 
        results: list[AIResult]
    ) -> None:
        """Persist generated results to database."""
        try:
            session_uuid = _uuid.UUID(session_id)
            for result in results:
                db.add(
                    Result(
                        session_id=session_uuid,
                        type=result.type,
                        value=result.value,
                    )
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
    
    @staticmethod
    def get_results(
        db: DBSession,
        session_id: str,
    ) -> ResultsResponse:
        session = db.query(Session).filter(Session.id == _uuid.UUID(session_id)).first()
        if not session:
            raise HTTPException(
                status_code=HTTPStatusCode.NOT_FOUND,
                detail=HTTPErrorMessage.SESSION_NOT_FOUND,
            )
        
        results = db.query(Result).filter(Result.session_id == session.id).all()

        type_rank = {t: i for i, t in enumerate(RESULT_TYPE_ORDER)}
        results.sort(key=lambda r: type_rank.get(r.type, len(RESULT_TYPE_ORDER)))

        _decoder = json.JSONDecoder()

        def _parse(raw: str):
            try:
                obj, _ = _decoder.raw_decode(raw.strip())
                return obj
            except json.JSONDecodeError:
                return raw

        result_outs = [
            ResultOut(
                id=str(r.id),
                type=r.type,
                value=_parse(r.value),
            )
            for r in results
        ]

        top_pick = next(
            (
                r for r in result_outs
                if r.type == ResultType.RECOMMENDATION
                and isinstance(r.value, dict)
                and r.value.get("ranking") == 1
            ),
            None,
        )

        participant_count = (
            db.query(Participant)
            .filter(Participant.session_id == session.id)
            .count()
        )

        return ResultsResponse(
            results=result_outs,
            meta=SessionMeta(
                topic=session.topic,
                participant_count=participant_count,
                created_at=session.created_at,
                top_pick=top_pick,
            ),
        )
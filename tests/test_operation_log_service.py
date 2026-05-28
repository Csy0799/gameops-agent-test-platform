from datetime import datetime, timedelta

from app.db.models import OperationLog
from app.services import operation_log_service


def test_log_operation_writes_operation_log(db_session):
    log = operation_log_service.log_operation(
        db_session,
        operation_type="test.create",
        target_type="test",
        target_id="1",
        status="success",
    )

    assert log is not None
    assert log.operation_type == "test.create"


def test_list_logs_filters_by_operation_type(db_session):
    operation_log_service.log_operation(db_session, "test.a", "test")
    operation_log_service.log_operation(db_session, "test.b", "test")

    logs = operation_log_service.list_logs(db_session, operation_type="test.b")

    assert len(logs) == 1
    assert logs[0].operation_type == "test.b"


def test_cleanup_expired_logs_keeps_recent_logs(db_session):
    old_log = OperationLog(
        operation_type="old.log",
        target_type="test",
        status="success",
        created_at=datetime.utcnow() - timedelta(days=400),
    )
    recent_log = OperationLog(
        operation_type="recent.log",
        target_type="test",
        status="success",
        created_at=datetime.utcnow(),
    )
    db_session.add_all([old_log, recent_log])
    db_session.commit()

    deleted_count = operation_log_service.cleanup_expired_logs(
        db_session,
        retention_days=365,
    )
    logs = operation_log_service.list_logs(db_session, target_type="test")

    assert deleted_count == 1
    assert [log.operation_type for log in logs] == ["recent.log"]

from app.workers.celery_app import celery_app


def test_celery_broker_is_redis():
    assert celery_app.conf.broker_url.startswith("redis://")


def test_celery_result_backend_is_redis():
    assert celery_app.conf.result_backend.startswith("redis://")


def test_celery_queues_defined():
    queue_names = {q.name for q in celery_app.conf.task_queues}
    assert {"critical", "high", "default"} <= queue_names


def test_celery_task_serializer_is_json():
    assert celery_app.conf.task_serializer == "json"

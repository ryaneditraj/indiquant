"""Celery Beat schedule smoke for weekly Trends collect."""

from __future__ import annotations

from celery.schedules import crontab


def test_trends_weekly_beat_schedule() -> None:
    from quant_os_api.workers import celery_app

    schedule = celery_app.conf.beat_schedule or {}
    entry = schedule.get("trends-weekly-collect")
    assert entry is not None, "trends-weekly-collect missing from beat_schedule"
    assert entry["task"] == "quant_os.trends_collect_all"
    cron = entry["schedule"]
    assert isinstance(cron, crontab)
    assert cron.minute == {30}
    assert cron.hour == {2}
    assert cron.day_of_week == {0}  # Sunday
    tz = str(celery_app.conf.timezone or "")
    assert "Kolkata" in tz or "Calcutta" in tz or tz == "Asia/Kolkata"


def test_trends_collect_all_task_registered() -> None:
    from quant_os_api.workers import celery_app

    assert "quant_os.trends_collect_all" in celery_app.tasks
    assert "quant_os.trends_collect" in celery_app.tasks

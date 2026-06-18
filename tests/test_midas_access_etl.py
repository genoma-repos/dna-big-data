from automations.midas_access_etl.automation import MidasAccessETL
from shared.utils.models import ExecutionStatus


def test_midas_access_etl_runs_successfully() -> None:
    result = MidasAccessETL().run()

    assert result.status == ExecutionStatus.SUCCESS
    assert result.rows_loaded == 2

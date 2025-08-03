from enterprise_modules.task_stubs import TASK_STUBS


def test_task_stub_count():
    assert len(TASK_STUBS) == 20


def test_task_stub_fields():
    for stub in TASK_STUBS:
        assert stub.name
        assert stub.design
        assert stub.development
        assert stub.testing
        assert stub.documentation
        assert stub.planning

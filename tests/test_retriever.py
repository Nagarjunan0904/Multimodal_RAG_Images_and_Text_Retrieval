from backend.retriever import retrieve


def test_retrieve_stub() -> None:
    assert retrieve("example query") == []

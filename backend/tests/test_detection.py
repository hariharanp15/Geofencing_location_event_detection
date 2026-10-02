from app.models import EventType, FenceState
from app.services.detection import classify


def test_state_transitions_generate_enter_exit_once():
    assert classify(None, FenceState.outside) == EventType.outside
    assert classify(FenceState.outside, FenceState.inside) == EventType.enter
    assert classify(FenceState.inside, FenceState.inside) == EventType.inside
    assert classify(FenceState.inside, FenceState.outside) == EventType.exit
    assert classify(FenceState.outside, FenceState.outside) == EventType.outside

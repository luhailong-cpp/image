"""User-selected 1200 ms run cycle: sixteen distinct frames, uniform 75 ms."""
RUN_FRAME_MS = 75
RUN_CYCLE_MS = 1200
RUN_NORMAL_DURATIONS = [RUN_FRAME_MS] * 16
assert len(RUN_NORMAL_DURATIONS) == 16 and sum(RUN_NORMAL_DURATIONS) == RUN_CYCLE_MS

from contextlib import contextmanager

from tests.src.log import log


class BDDLogger:
    """BDD (Given-When-Then) logging utility for structured test logging."""

    def __init__(self, test_name: str = None):
        self.test_name = test_name
        self.step_counter = 0

    @contextmanager
    def given(self, description: str):
        """Context manager for GIVEN steps."""
        self.step_counter += 1
        step_num = self.step_counter
        log.info(f"🔵 GIVEN #{step_num}: {description}")
        try:
            yield
            log.info(f"✅ GIVEN #{step_num} completed successfully")
        except Exception as e:
            log.error(f"❌ GIVEN #{step_num} failed: {e}")
            raise

    @contextmanager
    def when(self, description: str):
        """Context manager for WHEN steps."""
        self.step_counter += 1
        step_num = self.step_counter
        log.info(f"🟡 WHEN #{step_num}: {description}")
        try:
            yield
            log.info(f"✅ WHEN #{step_num} completed successfully")
        except Exception as e:
            log.error(f"❌ WHEN #{step_num} failed: {e}")
            raise

    @contextmanager
    def then(self, description: str):
        """Context manager for THEN steps."""
        self.step_counter += 1
        step_num = self.step_counter
        log.info(f"🟢 THEN #{step_num}: {description}")
        try:
            yield
            log.info(f"✅ THEN #{step_num} completed successfully")
        except Exception as e:
            log.error(f"❌ THEN #{step_num} failed: {e}")
            raise

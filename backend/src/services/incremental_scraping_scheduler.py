#!/usr/bin/env python3
"""
Incremental Scraping Scheduler
Automatically checks and triggers continuation scraping at regular intervals
"""
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
import sys

# Dynamic import handling
root_dir = Path(__file__).parent.parent.parent  # backend/
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from src.services.incremental_scraping_manager import IncrementalScrapingManager
except ImportError:
    from src.services.incremental_scraping_manager import IncrementalScrapingManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IncrementalScrapingScheduler:
    def __init__(self, check_interval_minutes: int = 30):
        """
        Initialize the scheduler

        Args:
            check_interval_minutes: How often to check for incomplete projects (default 30 minutes)
        """
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.manager = IncrementalScrapingManager()
        self.running = False
        self.scheduler_thread = None

    def start(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info(
            f"✓ Incremental Scraping Scheduler started (check interval: {self.check_interval//60} minutes)")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Incremental Scraping Scheduler stopped")

    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info(f"Scheduler loop started")

        last_check = 0

        while self.running:
            try:
                current_time = time.time()

                # Check if it's time to run the check
                if current_time - last_check >= self.check_interval:
                    logger.info(f"\n{'='*80}")
                    logger.info(
                        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running incremental scraping check...")
                    logger.info(f"{'='*80}")

                    # Run the check
                    try:
                        continuation_runs = self.manager.check_and_match_pages()

                        if continuation_runs:
                            logger.info(
                                f"[OK] Scheduled {len(continuation_runs)} continuation runs")
                            for run in continuation_runs:
                                logger.info(
                                    f"  - {run['project_name']}: Pages {run['start_page']}-{run['end_page']}")
                        else:
                            logger.info("[OK] No projects need continuation")

                        # Monitor active continuation runs
                        logger.info("\nMonitoring continuation runs...")
                        self.manager.monitor_continuation_runs()

                    except Exception as e:
                        logger.error(f"Error in scheduler check: {e}")
                        import traceback
                        traceback.print_exc()

                    last_check = current_time
                    logger.info(
                        f"Next check: {datetime.fromtimestamp(last_check + self.check_interval).strftime('%Y-%m-%d %H:%M:%S')}\n")

                # Sleep for 1 minute before checking again
                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)


# Global scheduler instance
_scheduler = None


def start_incremental_scraping_scheduler(check_interval_minutes: int = 30):
    """
    Start the incremental scraping scheduler

    Args:
        check_interval_minutes: How often to check for incomplete projects
    """
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        logger.warning("Scheduler is already running")
        return _scheduler

    _scheduler = IncrementalScrapingScheduler(check_interval_minutes)
    _scheduler.start()

    return _scheduler


def stop_incremental_scraping_scheduler():
    """Stop the incremental scraping scheduler"""
    global _scheduler

    if _scheduler:
        _scheduler.stop()
        _scheduler = None


def get_scheduler():
    """Get the current scheduler instance"""
    global _scheduler
    return _scheduler


if __name__ == '__main__':
    """
    Standalone mode - run the scheduler directly
    Usage: python incremental_scraping_scheduler.py [interval_minutes]
    """
    import sys

    interval = 30
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}, using default 30 minutes")

    print("\n" + "="*80)
    print("ParseHub Incremental Scraping Scheduler")
    print("="*80)
    print(f"Check Interval: {interval} minutes")
    print("="*80 + "\n")

    scheduler = start_incremental_scraping_scheduler(interval)

    try:
        # Keep the scheduler running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down scheduler...")
        stop_incremental_scraping_scheduler()
        print("[OK] Scheduler stopped")

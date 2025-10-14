from celery import shared_task
from models import TokenBlocklist
from tasks import logger


@shared_task(ignore_results=False, name="tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    A weekly job to remove expired tokens from the blocklist in the database.
    This keeps the TokenBlocklist table from growing indefinitely.
    """
    logger.info("Starting weekly cleanup of expired tokens...")
    try:
        # We'll remove tokens that are older than 7 days.
        deleted_count = TokenBlocklist.cleanup_blocklist(days=7)
        
        if deleted_count > 0:
            logger.info(f"Successfully removed {deleted_count} expired tokens from the blocklist.")
        else:
            logger.info("No expired tokens to remove this week.")
            
        return f"Token cleanup complete. Removed {deleted_count} tokens."
    except Exception as e:
        logger.error(f"An error occurred during token cleanup: {e}", exc_info=True)
        return "An error occurred during token cleanup."
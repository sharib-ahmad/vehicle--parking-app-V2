from celery import Celery
from app import create_app

# Initialize Celery with Flask app context
def make_celery(app):
    celery = Celery(app.import_name)
    # Update Celery config from Flask config
    celery.config_from_object('celeryconfig')
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    celery.autodiscover_tasks()
    return celery

flask_app = create_app()
celery = make_celery(flask_app)

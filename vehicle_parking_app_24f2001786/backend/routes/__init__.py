from flask_restx import Api
from flask_caching import Cache

# --- Initialize Extensions ---
# By placing the cache object here, it can be easily imported by all route files.
cache = Cache()

authorizations = {
    'Bearer Auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Add a JWT token like this: Bearer <your_token_here>"
    }
}

api = Api(version='1.0',
        title='Vehicle Parking App API',
        description='API for vehicle parking app',
        authorizations=authorizations,
        security='Bearer Auth',
        doc='/docs')  

def register_blueprints(app):
        cache.init_app(app)

        from routes.auth import auth_ns    
        from routes.user import user_ns
        from routes.admin import admin_ns
        from routes.public import public_ns
        
        api.add_namespace(user_ns, path='/users')
        api.add_namespace(auth_ns, path='/auth')
        api.add_namespace(admin_ns, path='/admin')
        api.add_namespace(public_ns, path='/public')

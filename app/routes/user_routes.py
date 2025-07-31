from flask_restx import Namespace, Resource, fields
from app.services.user_service import get_all_users, create_user,update_user,get_user_by_id,login_user,logout_user

user_blueprint = Namespace('users', description='User operations')

user_model = user_blueprint.model('UserModel', {
    'username': fields.String(required=True, description='The user name'),
    'email': fields.String(required=True, description='The user email'),
    'password_hash': fields.String(required=True, description='The user password'),
    'document_number': fields.String(required=True, description='The user document number'),
    "is_admin": fields.Boolean(required=False, description='Is the user an admin?')
})

@user_blueprint.route('/')
class UserList(Resource):
    def get(self):
        users,status = get_all_users()
        return users, status

    @user_blueprint.expect(user_model)
    def post(self):
        users,status = create_user()
        return users, status

@user_blueprint.route('/<int:user_id>')
class User(Resource):
    def get(self, user_id):
        users,status = get_user_by_id(user_id)
        return users, status

    @user_blueprint.expect(user_model)
    def put(self, user_id):
        users,status = update_user(user_id)
        return users, status

@user_blueprint.route('/login')
class UserLogin(Resource):
    @user_blueprint.expect(user_blueprint.model('LoginModel', {
    'email': fields.String(required=True, description='The user email'),
    'password': fields.String(required=True, description='The user password')
    }))
    def post(self):
        users,status = login_user()
        return users, status

@user_blueprint.route('/logout')
class UserLogout(Resource):
    def post(self):
        users,status = logout_user()
        return users, status
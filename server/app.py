#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

# NEW: Login Resource
class Login(Resource):
    def post(self):
        # Get username from request JSON
        username = request.get_json().get('username')
        
        # Retrieve user by username
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Set session's user_id to the user's id
            session['user_id'] = user.id
            
            # Return user as JSON with 200 status code
            return user.to_dict(), 200
        
        return {'error': 'User not found'}, 404

# NEW: Logout Resource
class Logout(Resource):
    def delete(self):
        # Remove user_id from session
        session.pop('user_id', None)
        
        # Return no data with 204 status code
        return '', 204

# NEW: CheckSession Resource
class CheckSession(Resource):
    def get(self):
        # Retrieve user_id from session
        user_id = session.get('user_id')
        
        if user_id:
            # If session has user_id, return the user as JSON with 200
            user = User.query.filter_by(id=user_id).first()
            if user:
                return user.to_dict(), 200
        
        # If no user_id in session, return empty dict with 401 Unauthorized
        return {}, 401

# Register existing resources
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

# Register new login/logout/session resources
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
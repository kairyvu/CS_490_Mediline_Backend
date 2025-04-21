from flaskr.services import get_comments_of_post, get_all_posts
from flask import Blueprint, jsonify, request
from flasgger import swag_from

social_media_bp = Blueprint('social_media', __name__)

@social_media_bp.route('/', methods=['GET'])
@swag_from('../docs/social_media_routes/get_posts.yml')
def get_posts():
    try:
        posts = get_all_posts()
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@social_media_bp.route('/<int:post_id>/comments', methods=['GET'])
@swag_from('../docs/social_media_routes/get_post_comments.yml')
def get_post_comments(post_id):
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'asc')
    try:
        comments = get_comments_of_post(post_id, sort_by, order)
        return jsonify(comments), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
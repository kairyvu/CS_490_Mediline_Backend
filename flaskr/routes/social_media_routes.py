from flaskr.services import get_comments_of_post, get_all_posts, delete_post, delete_comment, update_comment, update_post, create_comment, create_post
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
    
@social_media_bp.route('/<int:user_id>/post/<int:post_id>', methods=['DELETE'])
@swag_from('../docs/social_media_routes/delete_post.yml')
def delete_posts(user_id, post_id):
    result = delete_post(user_id, post_id)
    if not result:
        return jsonify({"error": "Post not found or unauthorized"}), 404
    return jsonify(result), 200

@social_media_bp.route('/<int:user_id>/comment/<int:comment_id>', methods=['DELETE'])
@swag_from('../docs/social_media_routes/delete_comment.yml')
def delete_comments(user_id, comment_id):
    result = delete_comment(user_id, comment_id)
    if not result:
        return jsonify({"error": "Comment not found or unauthorized"}), 404
    return jsonify(result), 200

@social_media_bp.route('/<int:user_id>/post/<int:post_id>', methods=['PUT'])
@swag_from('../docs/social_media_routes/update_post.yml')
def update_posts(user_id, post_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    result = update_post(user_id, post_id, data)
    if not result:
        return jsonify({"error": "Post not found or unauthorized"}), 404

    return jsonify(result), 200

@social_media_bp.route('/<int:user_id>/comment/<int:comment_id>', methods=['PUT'])
@swag_from('../docs/social_media_routes/update_comment.yml')
def update_comments(user_id, comment_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    result = update_comment(user_id, comment_id, data)
    if not result:
        return jsonify({"error": "Comment not found or unauthorized"}), 404

    return jsonify(result), 200

@social_media_bp.route('/<int:user_id>/post', methods=['POST'])
@swag_from('../docs/social_media_routes/create_posts.yml')
def create_posts(user_id):
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not content:
        return jsonify({"error": "content is required"}), 400
    result = create_post(user_id, title, content)
    return jsonify({
                    "message": "Post Created Successfully",
                    "comment" : result
        }), 201

@social_media_bp.route('/<int:user_id>/post/<int:post_id>/comment', methods=['POST'])
@swag_from('../docs/social_media_routes/create_comments.yml')
def create_comments(user_id, post_id):
    data = request.get_json()
    content = data.get("content")
    if not content:
        return jsonify({"error": "Content is required"}), 400
    result = create_comment(user_id, post_id, content)
    return jsonify({
                    "message": "Comment Created Successfully",
                    "comment" : result
        }), 201

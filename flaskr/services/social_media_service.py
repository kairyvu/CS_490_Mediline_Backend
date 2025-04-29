from flaskr.models import Post, Comment
from flaskr.extensions import db
from datetime import datetime

def get_all_posts(sort_by='created_at', order='asc'):
    posts = Post.query.all()
    if hasattr(Post, sort_by):
        if order == 'desc':
            posts = sorted(posts, key=lambda p: getattr(p, sort_by), reverse=True)
        else:
            posts = sorted(posts, key=lambda p: getattr(p, sort_by))
    else:
        raise ValueError(f"Invalid sort field: {sort_by}")
    return [post.to_dict() for post in posts]

def get_comments_of_post(post_id, sort_by='created_at', order='asc'):
    post = Post.query.get(post_id)
    if not post:
        raise ValueError("Post not found")
    comments = post.comments
    if hasattr(Comment, sort_by):
        if order.lower() == 'desc':
            comments = sorted(comments, key=lambda c: getattr(c, sort_by), reverse=True)
        else:
            comments = sorted(comments, key=lambda c: getattr(c, sort_by))
    
    return [comment.to_dict() for comment in comments]

def delete_post(user_id, post_id):
    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()
    if not post:
        return None
    db.session.delete(post)
    db.session.commit()
    return {"message": "Post and it comments deleted successfully", "post_id": post_id}

def delete_comment(user_id, comment_id):
    comment = Comment.query.filter_by(comment_id=comment_id, user_id=user_id).first()
    if not comment:
        return None
    db.session.delete(comment)
    db.session.commit()
    return {"message": "Comment deleted successfully", "comment_id": comment_id}

def update_post(user_id, post_id, new_data):
    post = Post.query.filter_by(post_id=post_id, user_id=user_id).first()
    if not post:
        return None
    if "title" in new_data:
        post.title = new_data["title"]
    if "content" in new_data:
        post.content = new_data["content"]
    db.session.commit()
    return post.to_dict()

def update_comment(user_id, comment_id, new_data):
    comment = Comment.query.filter_by(comment_id=comment_id, user_id=user_id).first()
    if not comment:
        return
    if "content" in new_data:
        comment.content = new_data["content"]
    db.session.commit()
    return comment.to_dict()

def create_post(user_id, title, content):
    now = datetime.now()
    new_post = Post(
        user_id=user_id,
        title=title,
        content=content,
        created_at=now,
        updated_at=now
    )
    db.session.add(new_post)
    db.session.commit()
    return new_post.to_dict()

def create_comment(user_id, post_id, content):
    now = datetime.now()
    new_comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=content,
        created_at=now,
        updated_at=now
    )
    db.session.add(new_comment)
    db.session.commit()
    return new_comment.to_dict()
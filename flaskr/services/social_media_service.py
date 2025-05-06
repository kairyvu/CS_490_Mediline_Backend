from flaskr.models import Post, Comment

def get_all_posts(sort_by='created_at', order='asc'):
    if not hasattr(Post, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by!r}")
    column = getattr(Post, sort_by)

    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    posts = Post.query.order_by(column).all()
    
    return [post.to_dict() for post in posts]

def get_comments_of_post(post_id, sort_by='created_at', order='asc'):
    post = Post.query.get(post_id)
    if not post:
        raise ValueError("Post not found")
    if not hasattr(Comment, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by!r}")
    column = getattr(Comment, sort_by)
    if order.lower() == 'desc':
        column = column.desc()
    elif order.lower() == 'asc':
        column = column.asc()
    else:
        raise ValueError(f"Invalid order: {order}")
    comments = Comment.query.filter_by(post_id=post_id).order_by(column).all()

    return [comment.to_dict() for comment in comments]
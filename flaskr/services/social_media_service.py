from flaskr.models import Post, Comment

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
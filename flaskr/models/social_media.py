from flaskr.extensions import db

class Post(db.Model):
    __tablename__ = 'post'

    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', back_populates='post', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, comments=False):
        result = {
            'post_id': self.post_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            }
        if comments:
            result['comments'] = [comment.to_dict() for comment in self.comments]
        return result


class Comment(db.Model):
    __tablename__ = 'comment'

    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    post = db.relationship('Post', back_populates='comments')
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
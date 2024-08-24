from extensions import db
from func import hex_id


class Catgories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    blogs = db.relationship("Blogs", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<Category {self.name}>"


class Blogs(db.Model):
    __tablename__ = "blogs"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    display = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    category_id = db.Column(
        db.String(50), db.ForeignKey("categories.id"), nullable=False
    )

    def __init__(self, title, content, category_id):
        self.title = title
        self.content = content
        self.category_id = category_id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title.title(),
            "content": self.content,
            "deleted": self.deleted,
            "display": self.display,
            "created": self.created.strftime("%a, %d %b %Y %H:%M:%S"),
            "updated": self.updated.strftime("%a, %d %b %Y %H:%M:%S"),
            "category": self.category.name.title(),
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<Blog {self.title}>"


def save_blog(title, content, category_id):
    blog = Blogs(title, content, category_id)
    blog.save()
    return blog


def get_blogs_per_category(category_id, page, per_page):
    blogs = Blogs.query.filter_by(
        category_id=category_id, deleted=False, display=True
    ).paginate(page=page, per_page=per_page, error_out=False)

    return blogs


def get_categories():
    cats = Catgories.query.all()
    return [cat.to_dict() for cat in cats]


def get_blog(blog_id):
    blog = Blogs.query.filter_by(id=blog_id, deleted=False, display=True).first()
    return blog.to_dict()


def get_all_blogs(page, per_page, blog_id, cat_id):
    query = Blogs.query.filter_by(deleted=False, display=True)

    if blog_id:
        query = query.filter_by(id=blog_id)

    if cat_id:
        query = query.filter_by(category_id=cat_id)

    blogs = query.paginate(page=page, per_page=per_page, error_out=False)
    return blogs


def category_exists(name):
    return Catgories.query.filter_by(name=name.lower()).first()


def save_category(name):
    category = Catgories(name.lower())
    category.save()
    return category

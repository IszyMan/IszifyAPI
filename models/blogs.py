from extensions import db
from func import hex_id


class Catgories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    blogs = db.relationship("Blogs", backref="category", lazy=True)

    def to_dict(self, with_blogs=False):
        cats = {"id": self.id, "name": self.name}
        if with_blogs:
            cats["blogs"] = [b.to_dict() for b in self.blogs]
        return cats

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
    featured_image = db.Column(db.Text)
    image_1 = db.Column(db.Text)
    image_2 = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    display = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    category_id = db.Column(
        db.String(50), db.ForeignKey("categories.id"), nullable=False
    )

    def __init__(
        self, title, content, category_id, featured_image, image_1=None, image_2=None
    ):
        self.title = title
        self.content = content
        self.category_id = category_id
        self.featured_image = featured_image
        self.image_1 = image_1
        self.image_2 = image_2

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title.title(),
            "content": self.content,
            # "deleted": self.deleted,
            # "display": self.display,
            "featured_image": self.featured_image,
            "image_1": self.image_1,
            "image_2": self.image_2,
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

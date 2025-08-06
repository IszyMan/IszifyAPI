from models.blogs import Blogs, Catgories


def save_blog(title, content, category_id, featured_image, image_1, image_2):
    blog = Blogs(title, content, category_id, featured_image, image_1, image_2)
    blog.save()
    return blog


def get_blogs_per_category(category_id, page, per_page):
    blogs = Blogs.query.filter_by(
        category_id=category_id, deleted=False, display=True
    ).paginate(page=page, per_page=per_page, error_out=False)

    return blogs


def get_categories():
    cats = Catgories.query.order_by(Catgories.name).all()
    return [cat.to_dict() for cat in cats]


def get_blog(blog_id):
    blog = Blogs.query.filter_by(id=blog_id, deleted=False, display=True).first()
    return blog.to_dict()


def get_blog_inst(blog_id):
    return Blogs.query.filter_by(id=blog_id, deleted=False, display=True).first()


def get_all_blogs(page, per_page, blog_id, cat_id):
    query = Blogs.query.filter_by(deleted=False, display=True)

    if blog_id:
        query = query.filter_by(id=blog_id)

    if cat_id:
        query = query.filter_by(category_id=cat_id)

    # order by
    query = query.order_by(Blogs.created.desc())

    blogs = query.paginate(page=page, per_page=per_page, error_out=False)
    return blogs


def category_exists(name):
    return Catgories.query.filter_by(name=name.lower()).first()


def save_category(name):
    category = Catgories(name.lower())
    category.save()
    return category


# get cat by id
def get_category(cat_id):
    return Catgories.query.filter_by(id=cat_id).first()

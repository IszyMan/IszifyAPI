from flask import Blueprint, request
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    get_all_blogs,
    get_blogs_per_category,
    get_blog,
    get_categories,
    save_blog,
    save_category,
    category_exists,
)
from utils import return_response
from extensions import db
from logger import logger

BLOG_PREFIX = "blog"

blog_blp = Blueprint("blog_blp", __name__)


# create blog
@blog_blp.route(f"/{BLOG_PREFIX}/create-blog", methods=["POST"])
def create_blog():
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        category_id = data.get("category_id")

        if not title or not content or not category_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Title, content and category are required",
            )

        blog = save_blog(title, content, category_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Blog created successfully",
            data=blog.to_dict(),
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/create_blog")
        logger.error(f"{e}: error@blog_blp/create_blog")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@blog_blp.route(f"/{BLOG_PREFIX}/get-blogs", methods=["GET"])
def get_blog():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        blog_id = request.args.get("blog_id")
        cat_id = request.args.get("cat_id")

        all_blogs = get_all_blogs(page, per_page, blog_id, cat_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="All blogs",
            data=[blog.to_dict() for blog in all_blogs.items],
            pages=all_blogs.pages,
            per_page=all_blogs.per_page,
            total_items=all_blogs.total,
            total_pages=all_blogs.pages,
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/get_blog")
        logger.error(f"{e}: error@blog_blp/get_blog")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get blogs per cat id
@blog_blp.route(f"/{BLOG_PREFIX}/get-blogs/<cat_id>", methods=["GET"])
def get_blogs_per_cat_id(cat_id):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        blog = get_blogs_per_category(cat_id, page, per_page)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="All blogs",
            data=[blog.to_dict() for blog in blog.items],
            pages=blog.page,
            per_page=blog.per_page,
            total_items=blog.total,
            total_pages=blog.pages,
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/get_blog")
        logger.error(f"{e}: error@blog_blp/get_blog")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get one blog
@blog_blp.route(f"/{BLOG_PREFIX}/get-blog/<blog_id>", methods=["GET"])
def get_one_blog(blog_id):
    try:
        blog = get_blog(blog_id)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="Blog", data=blog
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/get_blog")
        logger.error(f"{e}: error@blog_blp/get_blog")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get categories
@blog_blp.route(f"/{BLOG_PREFIX}/get-categories", methods=["GET"])
def get_all_categories():
    try:
        categories = get_categories()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Categories",
            data=categories,
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/get_blog")
        logger.error(f"{e}: error@blog_blp/get_blog")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create category
@blog_blp.route(f"/{BLOG_PREFIX}/create-category", methods=["POST"])
def create_category():
    try:
        data = request.get_json()
        name = data.get("name")
        if not name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Name is required",
            )

        name = name.lower()
        if category_exists(name):
            return return_response(
                HttpStatus.CONFLICT,
                status=StatusRes.FAILED,
                message="Category already exists",
            )

        category = save_category(name)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Category created successfully",
            data=category.to_dict(),
        )

    except Exception as e:
        logger.exception("traceback@blog_blp/create_category")
        logger.error(f"{e}: error@blog_blp/create_category")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )

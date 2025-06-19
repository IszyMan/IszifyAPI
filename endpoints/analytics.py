from flask import Blueprint
from models.qrcode import QrcodeRecord, QRCodeData
from models.shorten_url import Urlshort, UrlShortenerClicks
from status_res import StatusRes
from extensions import db, limiter
from utils import return_response, user_id_limiter
from flask_jwt_extended import jwt_required, current_user
from datetime import datetime
from decorators import email_verified
from logger import logger
from sqlalchemy import extract
from http_status import HttpStatus
from crud import (
    get_top_7_qrcodes,
    get_most_clicked_url_short,
    get_top_location_qrcodes,
    get_top_location_short_url,
)

ANALYTICS_PREFIX = "analytics"

analytics_blp = Blueprint("analytics_blp", __name__)


@analytics_blp.route(f"/{ANALYTICS_PREFIX}/all", methods=["GET"])
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def get_all_analytics():
    try:
        user_id = current_user.id

        # Prepare data for the charts
        qr_codes = QRCodeData.query.filter_by(user_id=user_id).all()
        # bio_pages = CreateBioPage.query.filter_by(user_id=user_id).all()
        url_shorts = Urlshort.query.filter_by(user_id=user_id).all()

        current_month = datetime.now().month
        current_year = datetime.now().year

        # Query to get clicks for each day of the current month and year
        clicks_per_month_s = (
            UrlShortenerClicks.query.join(
                Urlshort, Urlshort.id == UrlShortenerClicks.url_id
            )
            .filter(
                Urlshort.user_id == current_user.id,
                extract("month", UrlShortenerClicks.created) == current_month,
                extract("year", UrlShortenerClicks.created) == current_year,
            )
            .all()
        )

        click_per_month_qrcode_s = (
            QrcodeRecord.query.join(
                QRCodeData, QRCodeData.id == QrcodeRecord.qr_code_id
            )
            .filter(
                QRCodeData.user_id == current_user.id,
                extract("month", QrcodeRecord.date) == current_month,
                extract("year", QrcodeRecord.date) == current_year,
            )
            .all()
        )

        # click_per_month_bio_s = (
        #     BioPageClicks.query.join(
        #         CreateBioPage, CreateBioPage.id == BioPageClicks.bio_page_id
        #     )
        #     .filter(
        #         CreateBioPage.user_id == current_user.id,
        #         extract("month", BioPageClicks.created) == current_month,
        #         extract("year", BioPageClicks.created) == current_year,
        #         )
        #     .all()
        # )

        res_dict = {}
        res2_dict = {}
        res3_dict = {}
        for clicks_per_month in clicks_per_month_s:
            res_dict[clicks_per_month.created.strftime("%d-%b-%Y")] = (
                clicks_per_month.count
                if not res_dict.get(clicks_per_month.created.strftime("%d-%b-%Y"))
                else res_dict[clicks_per_month.created.strftime("%d-%b-%Y")]
                + clicks_per_month.count
            )

        for clicks_per_month in click_per_month_qrcode_s:
            res2_dict[clicks_per_month.date.strftime("%d-%b-%Y")] = (
                clicks_per_month.clicks
                if not res2_dict.get(clicks_per_month.date.strftime("%d-%b-%Y"))
                else res2_dict[clicks_per_month.date.strftime("%d-%b-%Y")]
                + clicks_per_month.clicks
            )

        # for clicks_per_month in click_per_month_bio_s:
        #     res3_dict[clicks_per_month.created.strftime("%d-%b-%Y")] = (
        #         clicks_per_month.count
        #         if not res3_dict.get(clicks_per_month.created.strftime("%d-%b-%Y"))
        #         else res3_dict[clicks_per_month.created.strftime("%d-%b-%Y")]
        #              + clicks_per_month.count
        #     )
        res = [
            {
                "date": key,
                "clicks": val,
            }
            for key, val in res_dict.items()
        ]
        res2 = [
            {
                "date": key,
                "clicks": val,
            }
            for key, val in res2_dict.items()
        ]
        # res3 = [
        #     {
        #         "date": key,
        #         "clicks": val,
        #     }
        #     for key, val in res3_dict.items()
        # ]

        # Prepare data for the charts
        qr_code_clicks = sum(qr_code.clicks for qr_code in qr_codes)
        # bio_page_clicks = sum(bio_page.clicks for bio_page in bio_pages)
        url_short_clicks = sum(url_short.clicks for url_short in url_shorts)

        qr_code_generated = len(qr_codes)
        # bio_pages_generated = len(bio_pages)
        url_shorts_generated = len(url_shorts)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Success",
            **{
                "analytics": {
                    "qr_code_clicks": qr_code_clicks,
                    # "bio_page_clicks": bio_page_clicks,
                    "url_short_clicks": url_short_clicks,
                    "qr_code_generated": qr_code_generated,
                    # "bio_pages_generated": bio_pages_generated,
                    "url_shorts_generated": url_shorts_generated,
                    "shortener_analytics": res,
                    "qr_code_analytics": res2,
                    "qr_code_location_history": get_top_location_qrcodes(
                        current_user.id
                    ),
                    "short_url_location_history": get_top_location_short_url(
                        current_user.id
                    ),
                    "top_7_qrcodes": get_top_7_qrcodes(current_user.id),
                    "top_7_shorts": get_most_clicked_url_short(current_user.id),
                    # "res3": res3,
                }
            },
        )
    except Exception as e:
        logger.exception("error@analytics_blp/get_all_analytics")
        logger.error(f"{e}: error@analytics_blp/get_all_analytics")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# qrcode analytics
@analytics_blp.route(
    f"/{ANALYTICS_PREFIX}/qrcode-analytics/<string:qr_code_id>", methods=["GET"]
)
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def qrcode_analytics(qr_code_id):
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year

        res2_dict = {}
        click_per_month_qrcode_s = (
            QrcodeRecord.query.join(
                QRCodeData, QRCodeData.id == QrcodeRecord.qr_code_id
            )
            .filter(
                QRCodeData.user_id == current_user.id,
                QRCodeData.id == qr_code_id,
                extract("month", QrcodeRecord.date) == current_month,
                extract("year", QrcodeRecord.date) == current_year,
            )
            .all()
        )
        for clicks_per_month in click_per_month_qrcode_s:
            res2_dict[clicks_per_month.date.strftime("%d-%b-%Y")] = (
                clicks_per_month.clicks
                if not res2_dict.get(clicks_per_month.date.strftime("%d-%b-%Y"))
                else res2_dict[clicks_per_month.date.strftime("%d-%b-%Y")]
                + clicks_per_month.clicks
            )
        res2 = [
            {
                "date": key,
                "clicks": val,
            }
            for key, val in res2_dict.items()
        ]
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Success",
            **{
                "analytics": {
                    "qr_code_location_history": get_top_location_qrcodes(
                        current_user.id, qr_code_id
                    ),
                    "qr_code_analytics": res2,
                    # "top_7_qrcodes": get_top_7_qrcodes(current_user.id, qr_code_id),
                }
            },
        )
    except Exception as e:
        logger.exception("traceback@analytics_blp/qrcode_analytics")
        logger.error(f"{e}: error@analytics_blp/qrcode_analytics")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# short url analytics
@analytics_blp.route(
    f"/{ANALYTICS_PREFIX}/shorturl-analytics/<short_id>", methods=["GET"]
)
@jwt_required()
@email_verified
@limiter.limit("5 per minute", key_func=user_id_limiter)
def short_url_analytics(short_id):
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year

        clicks_per_month_s = (
            UrlShortenerClicks.query.join(
                Urlshort, Urlshort.id == UrlShortenerClicks.url_id
            )
            .filter(
                Urlshort.user_id == current_user.id,
                Urlshort.id == short_id,
                extract("month", UrlShortenerClicks.created) == current_month,
                extract("year", UrlShortenerClicks.created) == current_year,
            )
            .all()
        )
        res_dict = {}
        for clicks_per_month in clicks_per_month_s:
            res_dict[clicks_per_month.created.strftime("%d-%b-%Y")] = (
                clicks_per_month.count
                if not res_dict.get(clicks_per_month.created.strftime("%d-%b-%Y"))
                else res_dict[clicks_per_month.created.strftime("%d-%b-%Y")]
                + clicks_per_month.count
            )
        res = [
            {
                "date": key,
                "clicks": val,
            }
            for key, val in res_dict.items()
        ]
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Success",
            **{
                "analytics": {
                    "short_url_location_history": get_top_location_short_url(
                        current_user.id, short_id
                    ),
                    "short_url_analytics": res,
                    # "top_7_shorts": get_most_clicked_url_short(
                    #     current_user.id, short_id
                    # ),
                }
            },
        )
    except Exception as e:
        logger.exception("error@analytics_blp/get_short_url_analytics")
        logger.error(f"{e}: error@analytics_blp/get_short_url_analytics")
        db.session.rollback()
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )

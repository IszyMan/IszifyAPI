from models.qrcode import (
    QRCodeCategories,
    QRCodeData,
    QrcodeRecord,
    SocialMedia,
    QrCodeStyling,
    QrFrame,
    QrCodeClickLocation,
)
from extensions import db
from utils import gen_short_code
from sqlalchemy import func, extract
from datetime import datetime
from logger import logger


def save_qrcode_category(name):
    qrcode_cat = QRCodeCategories(name=name.lower())
    qrcode_cat.save()
    return qrcode_cat


def get_qrcode_categories():
    cats = QRCodeCategories.query.order_by(QRCodeCategories.name).all()
    return [cat.to_dict() for cat in cats]


def save_qrcode_data(qrcode_data_payload, user_id):
    qrcode_data = QRCodeData(
        url=qrcode_data_payload["url"],
        phone_number=qrcode_data_payload["phone_number"],
        message=qrcode_data_payload["message"],
        email=qrcode_data_payload["email"],
        subject=qrcode_data_payload["subject"],
        ssid=qrcode_data_payload["ssid"],
        password=qrcode_data_payload["password"],
        encryption=qrcode_data_payload["encryption"],
        ios_url=qrcode_data_payload["ios_url"],
        android_url=qrcode_data_payload["android_url"],
        other_device_url=qrcode_data_payload["other_device_url"],
        longitude=qrcode_data_payload["longitude"],
        latitude=qrcode_data_payload["latitude"],
        trade_number=qrcode_data_payload["trade_number"],
        prefix=qrcode_data_payload["prefix"],
        first_name=qrcode_data_payload["first_name"],
        last_name=qrcode_data_payload["last_name"],
        company_name=qrcode_data_payload["company_name"],
        mobile_phone=qrcode_data_payload["mobile_phone"],
        fax=qrcode_data_payload["fax"],
        bitcoin_address=qrcode_data_payload["bitcoin_address"],
        bitcoin_amount=qrcode_data_payload["bitcoin_amount"],
        bitcoin_label=qrcode_data_payload["bitcoin_label"],
        bitcoin_message=qrcode_data_payload["bitcoin_message"],
        postal_code=qrcode_data_payload["postal_code"],
        religion=qrcode_data_payload["religion"],
        street=qrcode_data_payload["street"],
        city=qrcode_data_payload["city"],
        state=qrcode_data_payload["state"],
        country=qrcode_data_payload["country"],
        category=qrcode_data_payload["category"],
        short_url=gen_short_code() if qrcode_data_payload["url"] else None,
        title=qrcode_data_payload.get("title"),
        user_id=user_id,
    )

    if qrcode_data_payload["social_media"]:
        logger.info("social media")
        for sm in qrcode_data_payload["social_media"]:
            social_media = SocialMedia(
                name=sm["name"], url=sm["url"], qrcode=qrcode_data
            )
            db.session.add(social_media)

    if qrcode_data_payload["qr_style"]:
        logger.info("qr style")
        qr_styling = QrCodeStyling(
            width=qrcode_data_payload["qr_style"].get("width"),
            height=qrcode_data_payload["qr_style"].get("height"),
            image=qrcode_data_payload["qr_style"].get("image"),
            margin=qrcode_data_payload["qr_style"].get("margin"),
            qr_options=qrcode_data_payload["qr_style"].get("qrOptions", {}),
            image_options=qrcode_data_payload["qr_style"].get("imageOptions", {}),
            dots_options=qrcode_data_payload["qr_style"].get("dotsOptions", {}),
            background_options=qrcode_data_payload["qr_style"].get(
                "backgroundOptions", {}
            ),
            corners_square_options=qrcode_data_payload["qr_style"].get(
                "cornersSquareOptions", {}
            ),
            corners_dot_options=qrcode_data_payload["qr_style"].get(
                "cornersDotOptions", {}
            ),
            frame_text=qrcode_data_payload["qr_style"].get("frame_text"),
            frame_color=qrcode_data_payload["qr_style"].get("frame_color"),
            qrcode=qrcode_data,
        )

        db.session.add(qr_styling)

    if qrcode_data_payload["qr_frame"]:
        logger.info("qr frame")
        qr_frame = QrFrame(
            frame=qrcode_data_payload["frame"],
            scan_name=qrcode_data_payload["scan_name"],
            qrcode=qrcode_data,
        )
        db.session.add(qr_frame)

    db.session.add(qrcode_data)
    db.session.commit()
    return qrcode_data


def get_qrcode_data(
    page, per_page, user_id, category=None, start_date=None, end_date=None, hidden=False
):
    query = QRCodeData.query.filter(
        QRCodeData.user_id == user_id, QRCodeData.hidden == hidden
    )

    # Filter by category if provided
    if category:
        query = query.filter(func.lower(QRCodeData.category) == category.lower())

    # Filter by start_date and end_date if provided
    if start_date:
        query = query.filter(QRCodeData.created >= start_date)
    if end_date:
        query = query.filter(QRCodeData.created <= end_date)

    # Order by creation date descending and paginate
    qrcode_data = query.order_by(QRCodeData.created.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return {
        "data": [qrcode.to_dict() for qrcode in qrcode_data.items],
        "total_items": qrcode_data.total,
        "page": qrcode_data.page,
        "total_pages": qrcode_data.pages,
        "per_page": qrcode_data.per_page,
    }


def update_qrcode_data(qrcode_data_payload, user_id, qr_id):
    qrcode_data = QRCodeData.query.filter(
        QRCodeData.user_id == user_id, QRCodeData.id == qr_id
    ).first()

    if not qrcode_data:
        return False

    qrcode_data.url = qrcode_data_payload.get("url") or qrcode_data.url
    qrcode_data.phone_number = (
        qrcode_data_payload.get("phone_number") or qrcode_data.phone_number
    )
    qrcode_data.message = qrcode_data_payload.get("message") or qrcode_data.message
    qrcode_data.email = qrcode_data_payload.get("email") or qrcode_data.email
    qrcode_data.subject = qrcode_data_payload.get("subject") or qrcode_data.subject
    qrcode_data.ssid = qrcode_data_payload.get("ssid") or qrcode_data.ssid
    qrcode_data.password = qrcode_data_payload.get("password") or qrcode_data.password
    qrcode_data.encryption = (
        qrcode_data_payload.get("encryption") or qrcode_data.encryption
    )
    qrcode_data.ios_url = qrcode_data_payload.get("ios_url") or qrcode_data.ios_url
    qrcode_data.android_url = (
        qrcode_data_payload.get("android_url") or qrcode_data.android_url
    )
    qrcode_data.other_device_url = (
        qrcode_data_payload.get("other_device_url") or qrcode_data.other_device_url
    )
    qrcode_data.longitude = (
        qrcode_data_payload.get("longitude") or qrcode_data.longitude
    )
    qrcode_data.latitude = qrcode_data_payload.get("latitude") or qrcode_data.latitude
    qrcode_data.trade_number = (
        qrcode_data_payload.get("trade_number") or qrcode_data.trade_number
    )
    qrcode_data.prefix = qrcode_data_payload.get("prefix") or qrcode_data.prefix
    qrcode_data.first_name = (
        qrcode_data_payload.get("first_name") or qrcode_data.first_name
    )
    qrcode_data.last_name = (
        qrcode_data_payload.get("last_name") or qrcode_data.last_name
    )
    qrcode_data.company_name = (
        qrcode_data_payload.get("company_name") or qrcode_data.company_name
    )
    qrcode_data.mobile_phone = (
        qrcode_data_payload.get("mobile_phone") or qrcode_data.mobile_phone
    )
    qrcode_data.fax = qrcode_data_payload.get("fax") or qrcode_data.fax
    qrcode_data.postal_code = (
        qrcode_data_payload.get("postal_code") or qrcode_data.postal_code
    )
    qrcode_data.religion = qrcode_data_payload.get("religion") or qrcode_data.religion
    qrcode_data.street = qrcode_data_payload.get("street") or qrcode_data.street
    qrcode_data.city = qrcode_data_payload.get("city") or qrcode_data.city
    qrcode_data.state = qrcode_data_payload.get("state") or qrcode_data.state
    qrcode_data.country = qrcode_data_payload.get("country") or qrcode_data.country
    # qrcode_data.category = qrcode_data_payload.get("category") or qrcode_data.category
    qrcode_data.title = qrcode_data_payload.get("title") or qrcode_data.title
    qrcode_data.bitcoin_address = (
        qrcode_data_payload.get("bitcoin_address") or qrcode_data.bitcoin_address
    )
    qrcode_data.bitcoin_amount = (
        qrcode_data_payload.get("bitcoin_amount") or qrcode_data.bitcoin_amount
    )
    qrcode_data.bitcoin_label = (
        qrcode_data_payload.get("bitcoin_label") or qrcode_data.bitcoin_label
    )
    qrcode_data.bitcoin_message = (
        qrcode_data_payload.get("bitcoin_message") or qrcode_data.bitcoin_message
    )

    if isinstance(qrcode_data_payload.get("hidden"), bool):
        qrcode_data.hidden = qrcode_data_payload.get("hidden")
        if qrcode_data.short_url_id:
            qrcode_data.url_shortener.hidden = qrcode_data_payload.get("hidden")

    if qrcode_data_payload.get("social_media"):
        for social_media in qrcode_data_payload.get("social_media"):
            each_social = SocialMedia.query.filter_by(id=social_media["id"]).first()
            if each_social:
                each_social.url = social_media.get("url") or each_social.url
                each_social.name = social_media.get("name") or each_social.name
                each_social.update()
            else:
                social = SocialMedia(
                    url=social_media.get("url"), name=social_media.get("name")
                )
                social.save()

    # TODO: Edit QR Code Styling
    if qrcode_data_payload.get("qr_style"):
        for qr_style in qrcode_data_payload.get("qr_style"):
            each_qr = QrCodeStyling.query.filter_by(id=qr_style["id"]).first()
            if each_qr:
                each_qr.update()
            else:
                qr = QrCodeStyling()
                qr.save()
    if qrcode_data_payload.get("qr_frame"):
        qr_code_frame = QrFrame.query.filter_by(qrcode_id=qr_id).first()
        if qr_code_frame:
            qr_code_frame.frame = (
                qrcode_data_payload.get("qr_frame").get("frame") or qr_code_frame.frame
            )
            qr_code_frame.scan_name = (
                qrcode_data_payload.get("qr_frame").get("scan_name")
                or qr_code_frame.scan_name
            )
            qr_code_frame.update()
        else:
            qr_frame = QrFrame(
                frame=qrcode_data_payload.get("qr_frame").get("frame"),
                scan_name=qrcode_data_payload.get("qr_frame").get("scan_name"),
                qrcode_id=qr_id,
            )
            qr_frame.save()

    qrcode_data.update()

    return True


def get_qrcode_data_by_id(user_id, qr_id, fetch_type=None):
    qrcode_data = QRCodeData.query.filter_by(user_id=user_id, id=qr_id).first()
    if not qrcode_data:
        return None
    return qrcode_data if fetch_type else qrcode_data.to_dict()


def qrcode_styling(payload, qrcode_id, user_id):
    existing_style = (
        QrCodeStyling.query.join(QRCodeData)
        .filter(QrCodeStyling.qrcode_id == qrcode_id, QRCodeData.user_id == user_id)
        .first()
    )
    if existing_style:
        logger.info("update existing style")
        existing_style.width = payload.get("width") or existing_style.width
        existing_style.height = payload.get("height") or existing_style.height
        existing_style.image = payload.get("image") or existing_style.image
        existing_style.margin = payload.get("margin") or existing_style.margin
        existing_style.qr_options = (
            payload.get("qrOptions") or existing_style.qr_options
        )
        existing_style.image_options = (
            payload.get("imageOptions") or existing_style.image_options
        )
        existing_style.dots_options = (
            payload.get("dotsOptions") or existing_style.dots_options
        )
        existing_style.background_options = (
            payload.get("backgroundOptions") or existing_style.background_options
        )
        existing_style.corners_square_options = (
            payload.get("cornersSquareOptions") or existing_style.corners_square_options
        )
        existing_style.corners_dot_options = (
            payload.get("cornersDotOptions") or existing_style.corners_dot_options
        )
        existing_style.frame_text = (
            payload.get("frame_text") or existing_style.frame_text
        )
        existing_style.frame_color = (
            payload.get("frame_color") or existing_style.frame_color
        )

        existing_style.update()
        return existing_style, True
    logger.info("create new style")
    qr_styling = QrCodeStyling(
        width=payload.get("width"),
        height=payload.get("height"),
        image=payload.get("image"),
        margin=payload.get("margin"),
        qr_options=payload.get("qrOptions"),
        image_options=payload.get("imageOptions"),
        dots_options=payload.get("dotsOptions"),
        background_options=payload.get("backgroundOptions"),
        corners_square_options=payload.get("cornersSquareOptions"),
        corners_dot_options=payload.get("cornersDotOptions"),
        frame_text=payload.get("frame_text"),
        frame_color=payload.get("frame_color"),
        qrcode_id=qrcode_id,
    )

    qr_styling.save()
    return qr_styling, False


def get_url_by_short_url(short_url):
    original_url = QRCodeData.query.filter(
        func.lower(QRCodeData.short_url) == short_url.lower()
    ).first()
    return original_url.url if original_url else None


# check if url and category already exists
def check_url_category_exists(url, category, user_id):
    return QRCodeData.query.filter(
        func.lower(QRCodeData.url) == url.lower(),
        func.lower(QRCodeData.category) == category.lower(),
        QRCodeData.user_id == user_id,
    ).first()


def save_want_qr_code(
    category, short_url, short_id, url, user_id, title, qr_style=None, qr_frame=None
):
    if qr_frame is None:
        qr_frame = {}
    if qr_style is None:
        qr_style = {}
    qr_code_data = QRCodeData(
        url=url,
        short_url=short_url,
        short_url_id=short_id,
        category=category,
        user_id=user_id,
        title=title,
    )

    db.session.add(qr_code_data)

    if qr_style and isinstance(qr_style, dict):
        logger.info(f"qr style {qr_style}")
        qr_styling = QrCodeStyling(
            width=qr_style.get("width"),
            height=qr_style.get("height"),
            image=qr_style.get("image"),
            margin=qr_style.get("margin"),
            qr_options=qr_style.get("qrOptions", {}),
            image_options=qr_style.get("imageOptions", {}),
            dots_options=qr_style.get("dotsOptions", {}),
            background_options=qr_style.get("backgroundOptions", {}),
            corners_square_options=qr_style.get("cornersSquareOptions", {}),
            corners_dot_options=qr_style.get("cornersDotOptions", {}),
            frame_text=qr_style.get("frame_text"),
            frame_color=qr_style.get("frame_color"),
            qrcode=qr_code_data,
        )

        db.session.add(qr_styling)

    if qr_frame and isinstance(qr_frame, dict):
        logger.info("qr frame")
        # Implement this later
        pass

    db.session.commit()

    return qr_code_data


# CHECK SHORT URL EXIST
def check_short_url_exist(short_url):
    return QRCodeData.query.filter(QRCodeData.short_url == short_url).first()


# duplicate qr code
def duplicate_qr_code(qr_code_id, user_id, short_url):
    try:
        qr_code = QRCodeData.query.filter_by(id=qr_code_id, user_id=user_id).first()
        if not qr_code:
            return None

        sh_url = (gen_short_code() if qr_code.url else None,)

        new_qr_code = QRCodeData(
            url=qr_code.url,
            phone_number=qr_code.phone_number,
            message=qr_code.message,
            email=qr_code.email,
            subject=qr_code.subject,
            ssid=qr_code.ssid,
            password=qr_code.password,
            encryption=qr_code.encryption,
            ios_url=qr_code.ios_url,
            android_url=qr_code.android_url,
            other_device_url=qr_code.other_device_url,
            longitude=qr_code.longitude,
            latitude=qr_code.latitude,
            trade_number=qr_code.trade_number,
            prefix=qr_code.prefix,
            first_name=qr_code.first_name,
            last_name=qr_code.last_name,
            company_name=qr_code.company_name,
            mobile_phone=qr_code.mobile_phone,
            fax=qr_code.fax,
            bitcoin_address=qr_code.bitcoin_address,
            bitcoin_amount=qr_code.bitcoin_amount,
            bitcoin_label=qr_code.bitcoin_label,
            bitcoin_message=qr_code.bitcoin_message,
            postal_code=qr_code.postal_code,
            religion=qr_code.religion,
            street=qr_code.street,
            city=qr_code.city,
            state=qr_code.state,
            country=qr_code.country,
            category=qr_code.category,
            short_url=short_url or sh_url,
            title=qr_code.title,
            duplicate=True,
            user_id=qr_code.user_id,
        )

        db.session.add(new_qr_code)

        if qr_code.qr_style:
            qr_code_styling = qr_code.qr_style
            new_qr_styling = QrCodeStyling(
                width=qr_code_styling.width,
                height=qr_code_styling.height,
                image=qr_code_styling.image,
                margin=qr_code_styling.margin,
                qr_options=qr_code_styling.qr_options,
                image_options=qr_code_styling.image_options,
                dots_options=qr_code_styling.dots_options,
                background_options=qr_code_styling.background_options,
                corners_square_options=qr_code_styling.corners_square_options,
                corners_dot_options=qr_code_styling.corners_dot_options,
                qrcode_id=new_qr_code.id,
            )

            db.session.add(new_qr_styling)

        db.session.commit()
        return qr_code
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return None


def get_current_qr_code_count(current_user):
    """Return the count of QRCodeData records created in the current month."""
    now = datetime.utcnow()  # Use datetime.now() if your app isn't in UTC
    return (
        QRCodeData.query.filter_by(user=current_user)
        .filter(extract("year", QRCodeData.created) == now.year)
        .filter(extract("month", QRCodeData.created) == now.month)
        .count()
    )


def save_qrcode_clicks(url_id, payload):
    import datetime

    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = QrcodeRecord.query.filter(
        QrcodeRecord.qr_code_id == url_id,
        extract("year", QrcodeRecord.date) == current_year,
        extract("month", QrcodeRecord.date) == current_month,
        extract("day", QrcodeRecord.date) == current_day,
    ).first()

    if not clicks:
        print("save new click record")
        new_record = QrcodeRecord(clicks=1, qr_code_id=url_id)
        db.session.add(new_record)
    else:
        print("update click record")
        clicks.clicks += 1

    db.session.commit()
    save_qrcode_click_location(
        payload["ip_address"],
        payload["country"],
        payload["city"],
        payload["device"],
        payload["browser_name"],
        url_id,
    )
    return True


def save_qrcode_click_location(ip_address, country, city, device, browser, url_id):
    new_record = QrCodeClickLocation(
        ip_address=ip_address,
        country=country,
        city=city,
        device=device,
        browser=browser,
        qr_code_id=url_id,
    )
    db.session.add(new_record)
    db.session.commit()
    return True


# most 7 clicked qrcodes for a user
def get_top_7_qrcodes(user_id, qr_id=None):
    top_qrs = (
        QrcodeRecord.query.join(QRCodeData, QRCodeData.id == QrcodeRecord.qr_code_id)
        .filter(
            QRCodeData.user_id == user_id, QRCodeData.id == qr_id if qr_id else True
        )
        .order_by(QrcodeRecord.clicks.desc())
        .limit(7)
        .all()
    )
    return [top_qr.to_dict_qrcode_data() for top_qr in top_qrs]


def get_top_location_qrcodes(user_id, qr_id=None):
    # Total clicks for the user
    total_clicks = (
        QrCodeClickLocation.query.join(QRCodeData)
        .filter(QRCodeData.user_id == user_id)
        .count()
    )

    # Top countries
    top_countries = (
        db.session.query(
            QrCodeClickLocation.country,
            func.count(QrCodeClickLocation.id).label("count"),
        )
        .join(QRCodeData, QRCodeData.id == QrCodeClickLocation.qr_code_id)
        .filter(
            QRCodeData.user_id == user_id, QRCodeData.id == qr_id if qr_id else True
        )
        .group_by(QrCodeClickLocation.country)
        .order_by(func.count(QrCodeClickLocation.id).desc())
        .limit(7)
        .all()
    )

    # Top cities
    top_cities = (
        db.session.query(
            QrCodeClickLocation.city, func.count(QrCodeClickLocation.id).label("count")
        )
        .join(QRCodeData, QRCodeData.id == QrCodeClickLocation.qr_code_id)
        .filter(
            QRCodeData.user_id == user_id, QRCodeData.id == qr_id if qr_id else True
        )
        .group_by(QrCodeClickLocation.city)
        .order_by(func.count(QrCodeClickLocation.id).desc())
        .limit(7)
        .all()
    )

    # Top devices
    top_devices = (
        db.session.query(
            QrCodeClickLocation.device,
            func.count(QrCodeClickLocation.id).label("count"),
        )
        .join(QRCodeData, QRCodeData.id == QrCodeClickLocation.qr_code_id)
        .filter(
            QRCodeData.user_id == user_id, QRCodeData.id == qr_id if qr_id else True
        )
        .group_by(QrCodeClickLocation.device)
        .order_by(func.count(QrCodeClickLocation.id).desc())
        .limit(7)
        .all()
    )

    # Top browsers
    top_browsers = (
        db.session.query(
            QrCodeClickLocation.browser,
            func.count(QrCodeClickLocation.id).label("count"),
        )
        .join(QRCodeData, QRCodeData.id == QrCodeClickLocation.qr_code_id)
        .filter(
            QRCodeData.user_id == user_id, QRCodeData.id == qr_id if qr_id else True
        )
        .group_by(QrCodeClickLocation.browser)
        .order_by(func.count(QrCodeClickLocation.id).desc())
        .limit(7)
        .all()
    )

    # Helper function to calculate percentages
    def calculate_percentage(data):
        return [
            {
                "name": item[0],  # The grouped value (country, city, device, browser)
                "count": item[1],  # The count value
                "percentage": round((item[1] / total_clicks * 100), 2) if total_clicks > 0 else 0,
            }
            for item in data
        ]

    # Creating the final output
    return {
        "top_countries": calculate_percentage(top_countries),
        "top_cities": calculate_percentage(top_cities),
        "top_devices": calculate_percentage(top_devices),
        "top_browsers": calculate_percentage(top_browsers),
    }

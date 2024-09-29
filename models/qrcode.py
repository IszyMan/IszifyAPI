from extensions import db
from func import hex_id
from sqlalchemy import func
from flask import request
from utils import gen_short_code
from decorators import retry_on_exception


class QRCodeCategories(db.Model):
    __tablename__ = "qrcode_categories"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    display = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name.title()}

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<QRCodeCategory {self.name}>"


class QRCodeData(db.Model):
    __tablename__ = "qrcode_data"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    url = db.Column(db.Text)
    phone_number = db.Column(db.String(50))
    message = db.Column(db.Text)
    email = db.Column(db.String(100))
    subject = db.Column(db.String(150))
    ssid = db.Column(db.String(100))
    password = db.Column(db.String(150))
    encryption = db.Column(db.String(150))
    ios_url = db.Column(db.Text)
    android_url = db.Column(db.Text)
    other_device_url = db.Column(db.Text)
    longitude = db.Column(db.String(100))
    latitude = db.Column(db.String(100))
    trade_number = db.Column(db.String(100))
    prefix = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company_name = db.Column(db.String(150))
    mobile_phone = db.Column(db.String(50))
    fax = db.Column(db.String(50))
    postal_code = db.Column(db.String(50))
    religion = db.Column(db.String(50))
    street = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(150))
    country = db.Column(db.String(150))
    short_url = db.Column(db.String(50))
    category = db.Column(db.String(50), nullable=False)
    short_url_id = db.Column(db.String(50), db.ForeignKey("url_shortener.id"), nullable=True)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    social_media = db.relationship("SocialMedia", backref="qrcode", lazy=True)
    qr_style = db.relationship("QrCodeStyling", backref="qrcode", lazy=True, uselist=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return f"<QRCodeData {self.category}>"

    def to_dict(self):
        result = {
            "id": self.id,
            "url": self.url,
            "phone_number": self.phone_number,
            "message": self.message,
            "email": self.email,
            "subject": self.subject,
            "ssid": self.ssid,
            "password": self.password,
            "encryption": self.encryption,
            "ios_url": self.ios_url,
            "android_url": self.android_url,
            "other_device_url": self.other_device_url,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "trade_number": self.trade_number,
            "prefix": self.prefix,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company_name": self.company_name,
            "mobile_phone": self.mobile_phone,
            "fax": self.fax,
            "postal_code": self.postal_code,
            "religion": self.religion,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "short_url": f"{request.host_url}{self.short_url}",
            "country": self.country,
            "category": self.category,
            "created": self.created.strftime("%d-%b-%Y %H:%M:%S"),
            "social_media": (
                [sm.to_dict() for sm in self.social_media] if self.social_media else []
            ),
            "qr_style": self.qr_style.to_dict() if self.qr_style else {},
        }
        return {key: value for key, value in result.items() if value}


class QrCodeStyling(db.Model):
    __tablename__ = "qr_code_styling"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    width = db.Column(db.Integer, default=200)
    height = db.Column(db.Integer, default=200)
    image = db.Column(db.Text, nullable=True)
    margin = db.Column(db.Integer, default=0)

    qr_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for QR options
    image_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for image options
    dots_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for dots options
    background_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for background options
    corners_square_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for square corners options
    corners_dot_options = db.Column(db.JSON, nullable=False)  # Dynamic JSON for dot corners options

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        data_to_return = {
            "id": self.id,
            "width": self.width,
            "height": self.height,
            "image": self.image,
            "margin": self.margin,
            "qr_options": self.qr_options,
            "image_options": self.image_options,
            "dots_options": self.dots_options,
            "background_options": self.background_options,
            "corners_square_options": self.corners_square_options,
            "corners_dot_options": self.corners_dot_options,
        }
        return {key: value for key, value in data_to_return.items() if value}


class SocialMedia(db.Model):
    __tablename__ = "social_media"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {"id": self.id, "name": self.name, "url": self.url}


def save_qrcode_category(name):
    qrcode_cat = QRCodeCategories(name=name.lower())
    qrcode_cat.save()
    return qrcode_cat


def get_qrcode_categories():
    cats = QRCodeCategories.query.order_by(QRCodeCategories.name).all()
    return [cat.to_dict() for cat in cats]


@retry_on_exception(retries=3, delay=1)
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
        postal_code=qrcode_data_payload["postal_code"],
        religion=qrcode_data_payload["religion"],
        street=qrcode_data_payload["street"],
        city=qrcode_data_payload["city"],
        state=qrcode_data_payload["state"],
        country=qrcode_data_payload["country"],
        category=qrcode_data_payload["category"],
        short_url=gen_short_code() if qrcode_data_payload["url"] else None,
        user_id=user_id,
    )

    if qrcode_data_payload["social_media"]:
        print("social media")
        for sm in qrcode_data_payload["social_media"]:
            social_media = SocialMedia(
                name=sm["name"], url=sm["url"], qrcode=qrcode_data
            )
            db.session.add(social_media)

    if qrcode_data_payload["qr_style"]:
        print("qr style")
        qr_styling = QrCodeStyling(
            width=qrcode_data_payload["qr_style"].get("width"),
            height=qrcode_data_payload["qr_style"].get("height"),
            image=qrcode_data_payload["qr_style"].get("image"),
            margin=qrcode_data_payload["qr_style"].get("margin"),
            qr_options=qrcode_data_payload["qr_style"].get("qr_options", {}),
            image_options=qrcode_data_payload["qr_style"].get("image_options", {}),
            dots_options=qrcode_data_payload["qr_style"].get("dots_options", {}),
            background_options=qrcode_data_payload["qr_style"].get("background_options", {}),
            corners_square_options=qrcode_data_payload["qr_style"].get("corners_square_options", {}),
            corners_dot_options=qrcode_data_payload["qr_style"].get("corners_dot_options", {}),
            qrcode=qrcode_data,
        )

        db.session.add(qr_styling)

    db.session.add(qrcode_data)
    db.session.commit()
    return qrcode_data


@retry_on_exception(retries=3, delay=1)
def get_qrcode_data(
    page, per_page, user_id, category=None, start_date=None, end_date=None
):
    query = QRCodeData.query.filter(QRCodeData.user_id == user_id)

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


@retry_on_exception(retries=3, delay=1)
def update_qrcode_data(qrcode_data_payload, user_id, qr_id):
    qrcode_data = QRCodeData.query.filter(
        QRCodeData.user_id == user_id, QRCodeData.id == qr_id
    ).first()

    if not qrcode_data:
        return False

    qrcode_data.url = qrcode_data_payload.get("url", qrcode_data.url)
    qrcode_data.phone_number = qrcode_data_payload.get(
        "phone_number", qrcode_data.phone_number
    )
    qrcode_data.message = qrcode_data_payload.get("message", qrcode_data.message)
    qrcode_data.email = qrcode_data_payload.get("email", qrcode_data.email)
    qrcode_data.subject = qrcode_data_payload.get("subject", qrcode_data.subject)
    qrcode_data.ssid = qrcode_data_payload.get("ssid", qrcode_data.ssid)
    qrcode_data.password = qrcode_data_payload.get("password", qrcode_data.password)
    qrcode_data.encryption = qrcode_data_payload.get(
        "encryption", qrcode_data.encryption
    )
    qrcode_data.ios_url = qrcode_data_payload.get("ios_url", qrcode_data.ios_url)
    qrcode_data.android_url = qrcode_data_payload.get(
        "android_url", qrcode_data.android_url
    )
    qrcode_data.other_device_url = qrcode_data_payload.get(
        "other_device_url", qrcode_data.other_device_url
    )
    qrcode_data.longitude = qrcode_data_payload.get("longitude", qrcode_data.longitude)
    qrcode_data.latitude = qrcode_data_payload.get("latitude", qrcode_data.latitude)
    qrcode_data.trade_number = qrcode_data_payload.get(
        "trade_number", qrcode_data.trade_number
    )
    qrcode_data.prefix = qrcode_data_payload.get("prefix", qrcode_data.prefix)
    qrcode_data.first_name = qrcode_data_payload.get(
        "first_name", qrcode_data.first_name
    )
    qrcode_data.last_name = qrcode_data_payload.get("last_name", qrcode_data.last_name)
    qrcode_data.company_name = qrcode_data_payload.get(
        "company_name", qrcode_data.company_name
    )
    qrcode_data.mobile_phone = qrcode_data_payload.get(
        "mobile_phone", qrcode_data.mobile_phone
    )
    qrcode_data.fax = qrcode_data_payload.get("fax", qrcode_data.fax)
    qrcode_data.postal_code = qrcode_data_payload.get(
        "postal_code", qrcode_data.postal_code
    )
    qrcode_data.religion = qrcode_data_payload.get("religion", qrcode_data.religion)
    qrcode_data.street = qrcode_data_payload.get("street", qrcode_data.street)
    qrcode_data.city = qrcode_data_payload.get("city", qrcode_data.city)
    qrcode_data.state = qrcode_data_payload.get("state", qrcode_data.state)
    qrcode_data.country = qrcode_data_payload.get("country", qrcode_data.country)
    qrcode_data.category = qrcode_data_payload.get("category", qrcode_data.category)

    if qrcode_data_payload.get("social_media"):
        for social_media in qrcode_data_payload.get("social_media"):
            each_social = SocialMedia.query.filter_by(id=social_media["id"]).first()
            if each_social:
                each_social.url = social_media.get("url", each_social.url)
                each_social.name = social_media.get("name", each_social.name)
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

    qrcode_data.update()

    return True


@retry_on_exception(retries=3, delay=1)
def get_qrcode_data_by_id(user_id, qr_id, fetch_type=None):
    qrcode_data = QRCodeData.query.filter_by(user_id=user_id, id=qr_id).first()
    if not qrcode_data:
        return None
    return qrcode_data if fetch_type else qrcode_data.to_dict()


@retry_on_exception(retries=3, delay=1)
def qrcode_styling(payload, qrcode_id):
    existing_style = QrCodeStyling.query.filter_by(qrcode_id=qrcode_id).first()
    if existing_style:
        print("update existing style")
        existing_style.width = payload.get("width", existing_style.width)
        existing_style.height = payload.get("height", existing_style.height)
        existing_style.image = payload.get("image", existing_style.image)
        existing_style.margin = payload.get("margin", existing_style.margin)
        existing_style.qr_options = payload.get("qr_options", existing_style.qr_options)
        existing_style.image_options = payload.get(
            "image_options", existing_style.image_options
        )
        existing_style.dots_options = payload.get(
            "dots_options", existing_style.dots_options
        )
        existing_style.background_options = payload.get(
            "background_options", existing_style.background_options
        )
        existing_style.corners_square_options = payload.get(
            "corners_square_options", existing_style.corners_square_options
        )
        existing_style.corners_dot_options = payload.get(
            "corners_dot_options", existing_style.corners_dot_options
        )

        existing_style.update()
        return existing_style
    print("create new style")
    qr_styling = QrCodeStyling(
        width=payload.get("width"),
        height=payload.get("height"),
        image=payload.get("image"),
        margin=payload.get("margin"),
        qr_options=payload.get("qr_options"),
        image_options=payload.get("image_options"),
        dots_options=payload.get("dots_options"),
        background_options=payload.get("background_options"),
        corners_square_options=payload.get("corners_square_options"),
        corners_dot_options=payload.get("corners_dot_options"),
        qrcode_id=qrcode_id,
    )

    qr_styling.save()
    return qr_styling


@retry_on_exception(retries=3, delay=1)
def get_url_by_short_url(short_url):
    original_url = QRCodeData.query.filter(
        func.lower(QRCodeData.short_url) == short_url.lower()).first()
    return original_url.url if original_url else None

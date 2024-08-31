from extensions import db
from func import hex_id
from sqlalchemy import func


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
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    social_media = db.relationship("SocialMedia", backref="qrcode", lazy=True)
    qr_style = db.relationship("QrCodeStyling", backref="qrcode", lazy=True)

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
            "country": self.country,
            "category": self.category,
            "created": self.created.strftime("%d-%b-%Y %H:%M:%S"),
            "social_media": (
                [sm.to_dict() for sm in self.social_media] if self.social_media else []
            ),
            "qr_style": [qs.to_dict() for qs in self.qr_style] if self.qr_style else [],
        }
        return {key: value for key, value in result.items() if value}


class QrCodeStyling(db.Model):
    __tablename__ = "qr_code_styling"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    def to_dict(self):
        return {"id": self.id}


class SocialMedia(db.Model):
    __tablename__ = "social_media"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    qrcode_id = db.Column(db.String(50), db.ForeignKey("qrcode_data.id"))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "url": self.url}


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
        postal_code=qrcode_data_payload["postal_code"],
        religion=qrcode_data_payload["religion"],
        street=qrcode_data_payload["street"],
        city=qrcode_data_payload["city"],
        state=qrcode_data_payload["state"],
        country=qrcode_data_payload["country"],
        category=qrcode_data_payload["category"],
        user_id=user_id,
    )

    if "social_media" in qrcode_data_payload:
        for sm in qrcode_data_payload["social_media"]:
            social_media = SocialMedia(
                name=sm["name"], url=sm["url"], qrcode=qrcode_data
            )
            db.session.add(social_media)

    if "qr_style" in qrcode_data_payload:
        for qs in qrcode_data_payload["qr_style"]:
            qr_style = QrCodeStyling(qrcode=qrcode_data)  # TODO: add styling options
            db.session.add(qr_style)

    db.session.add(qrcode_data)
    db.session.commit()
    return qrcode_data


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

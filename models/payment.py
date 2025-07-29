from extensions import db
from func import hex_id
from datetime import datetime, timedelta
from logger import logger


class PaymentPlans(db.Model):
    __tablename__ = "payment_plans"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(50), nullable=False)
    halve_backs = db.Column(db.Integer, default=0)
    customer_support = db.Column(db.Boolean, default=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in months or other unit
    unlimited_link_clicks = db.Column(db.Boolean, default=False)
    unlimited_qr_scans = db.Column(db.Boolean, default=False)
    shortlinks_per_month = db.Column(db.Integer, default=0)
    qr_codes_per_month = db.Column(db.Integer, default=0)
    link_in_bio = db.Column(db.Integer, default=0)
    analytics_access = db.Column(db.Boolean, default=False)
    qr_code_customization = db.Column(db.Boolean, default=False)
    qr_code_watermark = db.Column(db.Boolean, default=True)

    user_sub = db.relationship("Subscriptions", backref="plan", lazy=True)

    def __init__(
        self,
        name,
        amount,
        currency,
        duration,
        unlimited_link_clicks=False,
        unlimited_qr_scans=False,
        shortlinks_per_month=0,
        qr_codes_per_month=0,
        link_in_bio=0,
        analytics_access=False,
        qr_code_customization=False,
        qr_code_watermark=True,
        customer_support=False,
        halve_backs=0,
    ):
        self.name = name.title()
        self.amount = amount
        self.currency = currency
        self.duration = duration
        self.unlimited_link_clicks = unlimited_link_clicks
        self.unlimited_qr_scans = unlimited_qr_scans
        self.shortlinks_per_month = shortlinks_per_month
        self.qr_codes_per_month = qr_codes_per_month
        self.link_in_bio = link_in_bio
        self.analytics_access = analytics_access
        self.qr_code_customization = qr_code_customization
        self.qr_code_watermark = qr_code_watermark
        self.customer_support = customer_support
        self.halve_backs = halve_backs

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "currency": self.currency,
            "duration": self.duration,
            "unlimited_link_clicks": self.unlimited_link_clicks,
            "unlimited_qr_scans": self.unlimited_qr_scans,
            "shortlinks_per_month": self.shortlinks_per_month,
            "qr_codes_per_month": self.qr_codes_per_month,
            "link_in_bio": self.link_in_bio,
            "analytics_access": self.analytics_access,
            "qr_code_customization": self.qr_code_customization,
            "qr_code_watermark": self.qr_code_watermark,
            "customer_support": self.customer_support or False,
            "halve_backs": self.halve_backs or 0,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    plan_id = db.Column(db.String(50), db.ForeignKey("payment_plans.id"))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(50))

    def __init__(self, user_id, plan_id, start_date, end_date, status):
        self.user_id = user_id
        self.plan_id = plan_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
        }

    def user_to_dict(self):
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "start_date": self.start_date,
            "end_date": (
                self.end_date
                if "beginner" not in self.plan.name.lower()
                else "No Expiration"
            ),
            "plan": self.plan.to_dict(),
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Transactions(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    description = db.Column(db.Text)
    amount = db.Column(db.Float)
    method = db.Column(db.String(50))
    transaction_reference = db.Column(db.String(150))
    currency = db.Column(db.String(50))
    status = db.Column(db.String(50))
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())

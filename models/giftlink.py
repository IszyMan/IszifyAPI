from extensions import db
from func import hex_id, format_datetime
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta
import enum
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import JSON


class CaseInsensitiveEnum(enum.Enum):
    @classmethod
    def from_str(cls, value):
        """Convert a string to enum member (case-insensitive)."""
        if not isinstance(value, str):
            raise ValueError(f"{value} is not a string")
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class NicheEnum(CaseInsensitiveEnum):
    blogger = "blogger"
    artiste = "artiste"
    musician = "musician"
    actor = "actor"
    skit_maker = "skit maker"
    comedian = "comedian"
    writer = "writer"
    influencer = "influencer"
    entrepreneur = "entrepreneur"
    fashion_designer = "fashion designer"
    podcaster = "podcaster"
    vlogger = "vlogger"
    social = "social"
    art = "art"
    music = "music"
    comedy = "comedy"
    education = "education"
    fitness = "fitness"
    health = "health"
    lifestyle = "lifestyle"
    travel = "travel"
    tech = "tech"
    business = "business"
    finance = "finance"
    gaming = "gaming"
    sports = "sports"


class GiftType(CaseInsensitiveEnum):
    fundraising = "Fundraising"
    gift = "Gift"


# gift account
class GiftAccount(db.Model):
    __tablename__ = "gift_account"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(150))
    username = db.Column(db.String(50))
    niche = db.Column(MutableList.as_mutable(JSON), default=list, nullable=True)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.Text)
    cover_image = db.Column(db.Text)
    website = db.Column(db.Text)
    buy_me = db.Column(db.String(50))
    tip_unit_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    button_option = db.Column(db.String(50))
    thanks_msg = db.Column(db.Text, nullable=True)
    layout = db.Column(db.String(150), nullable=True)
    sugg_amounts = db.Column(MutableList.as_mutable(JSON), default=list, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    social_links = db.relationship("SocialLinks", backref="gift_account", lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "username": self.username,
            "bio": self.bio,
            "profile_image": self.profile_image,
            "cover_image": self.cover_image,
            "website": self.website,
            "niche": self.niche or [],
            "buy_me": self.buy_me or "",
            "tip_unit_price": self.tip_unit_price,
            "min_price": self.min_price or 0,
            "button_option": self.button_option or "",
            "sugg_amounts": self.sugg_amounts or [],
            "layout": self.layout or "",
            "thanks_msg": self.thanks_msg or "",
            "created": format_datetime(self.created),
            "updated": format_datetime(self.updated),
            "social_links": [social_link.link for social_link in self.social_links],
        }


# social links
class SocialLinks(db.Model):
    __tablename__ = "social_links"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    gift_account_id = db.Column(
        db.String(50), db.ForeignKey("gift_account.id"), nullable=False
    )
    link = db.Column(db.Text)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )


class GiftLinks(db.Model):
    __tablename__ = "gift_links"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    gift_type = db.Column(db.Enum(GiftType), nullable=False, default=GiftType.gift)
    gift_account_id = db.Column(db.String(50), db.ForeignKey("gift_account.id"))
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    layout = db.Column(db.String(50))
    buy_me = db.Column(db.String(50))
    tip_unit_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    button_option = db.Column(db.String(50))
    sugg_amounts = db.Column(MutableList.as_mutable(JSON), default=list)
    image = db.Column(db.Text, nullable=True)
    link = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    goal_amount = db.Column(db.Float, default=0)
    start_amount = db.Column(db.Float, default=0)
    current_amount = db.Column(db.Float, default=0)
    profile_image = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.Text, nullable=True)
    font_style = db.Column(db.String(50), nullable=True)
    color_theme = db.Column(db.String(50), nullable=True)
    thanks_msg = db.Column(db.Text, nullable=True)
    slug = db.Column(db.String(50), nullable=True, unique=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # indexes
    __table_args__ = (
        db.Index("ix_gift_links_slug", "slug", unique=True),
        db.Index("ix_gift_links_user_id", "user_id"),
        db.Index("ix_gift_links_active", "active"),
        db.Index("ix_gift_links_created", "created"),
        db.Index("ix_gift_links_updated", "updated"),
        db.Index("ix_gift_links_gift_type", "gift_type"),
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "layout": self.layout,
            "buy_me": self.buy_me,
            "tip_unit_price": self.tip_unit_price,
            "min_price": self.min_price,
            "button_option": self.button_option,
            "sugg_amounts": self.sugg_amounts,
            "image": self.image,
            "link": self.link,
            "active": self.active,
            "goal_amount": self.goal_amount,
            "start_amount": self.start_amount,
            "current_amount": self.current_amount,
            "profile_image": self.profile_image,
            "cover_image": self.cover_image,
            "font_style": self.font_style,
            "color_theme": self.color_theme,
            "created": format_datetime(self.created),
            "updated": format_datetime(self.updated),
            # "social_links": [social_link.link for social_link in self.social_links],
        }

    def user_to_dict(self):
        model_dict = self.to_dict()
        model_dict["user"] = f"{self.user.last_name} {self.user.first_name}".title()

        # only return key with value
        model_dict = {k: v for k, v in model_dict.items() if v}
        return model_dict


# user wallet
class UserWallet(db.Model):
    __tablename__ = "user_wallet"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "balance": self.balance}


class SavedBank(db.Model):
    __tablename__ = "saved_bank"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    bank_code = db.Column(db.String(50))
    bank_name = db.Column(db.String(150))
    account_name = db.Column(db.String(150))
    account_number = db.Column(db.String(50))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    # indexes
    __table_args__ = (
        db.Index("ix_saved_bank_user_id", "user_id"),
        db.Index("ix_saved_bank_created", "created"),
        db.Index("ix_saved_bank_updated", "updated"),
        db.Index("ix_saved_bank_bank_code", "bank_code"),
        db.Index("ix_saved_bank_bank_name", "bank_name"),
        db.Index("ix_saved_bank_account_name", "account_name"),
        db.Index("ix_saved_bank_account_number", "account_number"),
    )

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "bank_code": self.bank_code,
            "bank_name": self.bank_name,
            "account_name": self.account_name,
            "account_number": self.account_number,
        }


class Donation(db.Model):
    __tablename__ = "donations"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    gift_link_id = db.Column(
        db.String(36), db.ForeignKey("gift_links.id"), nullable=False
    )
    fan_name = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False, default=0)
    message = db.Column(db.Text)
    donated = db.Column(db.Boolean, default=False)
    payment_reference = db.Column(
        db.String(100), unique=True
    )  # from Paystack/Flutterwave
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

from extensions import db
from func import hex_id, format_datetime
from passlib.hash import pbkdf2_sha256 as hasher
from datetime import datetime, timedelta
import enum


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
    blogger = "Blogger"
    artiste = "Artiste"
    musician = "Musician"
    actor = "Actor"
    skit_maker = "Skit Maker"
    comedian = "Comedian"
    writer = "Writer"
    influencer = "Influencer"
    entrepreneur = "Entrepreneur"
    fashion_designer = "Fashion Designer"
    podcaster = "Podcaster"
    vlogger = "Vlogger"


class GiftType(CaseInsensitiveEnum):
    fundraising = "Fundraising"
    gift = "Gift"


class GiftLinks(db.Model):
    __tablename__ = "gift_links"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    user_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=False)
    gift_type = db.Column(db.Enum(GiftType), nullable=False, default=GiftType.gift)
    niche = db.Column(db.Enum(NicheEnum), nullable=False, default=NicheEnum.blogger)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)
    link = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)
    goal_amount = db.Column(db.Float, default=0)
    current_amount = db.Column(db.Float, default=0)
    profile_image = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.Text, nullable=True)
    font_style = db.Column(db.String(50), nullable=True)
    color_theme = db.Column(db.String(50), nullable=True)
    slug = db.Column(db.String(250), nullable=False, unique=True)
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
        db.Index("ix_gift_links_niche", "niche"),
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
            "niche": self.niche.value,
            "gift_type": self.gift_type.value,
            "image": self.image,
            "slug": self.slug,
            "link": self.link,
            "active": self.active,
            "goal_amount": self.goal_amount,
            "current_amount": self.current_amount,
            "profile_image": self.profile_image,
            "cover_image": self.cover_image,
            "font_style": self.font_style,
            "color_theme": self.color_theme,
            "created": format_datetime(self.created),
            "updated": format_datetime(self.updated),
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

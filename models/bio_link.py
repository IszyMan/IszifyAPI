from extensions import db
from func import hex_id
from sqlalchemy import func
from datetime import datetime, timedelta


class BioLink(db.Model):
    __tablename__ = "bio_link"

    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )

    def __repr__(self):
        return f"<BioLink {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()


# save bio link
# def save_bio_link(bio_link):
#     db.session.add(bio_link)
#     db.session.commit()
#     return True

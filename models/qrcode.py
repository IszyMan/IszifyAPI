from extensions import db
from func import hex_id


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


def save_qrcode_category(name):
    qrcode_cat = QRCodeCategories(name=name.lower())
    qrcode_cat.save()
    return qrcode_cat


def get_qrcode_categories():
    cats = QRCodeCategories.query.order_by(QRCodeCategories.name).all()
    return [cat.to_dict() for cat in cats]

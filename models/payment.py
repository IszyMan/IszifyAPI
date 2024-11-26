from extensions import db
from func import hex_id


class PaymentPlans(db.Model):
    __tablename__ = "payment_plans"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(50))
    duration = db.Column(db.Integer)

    def __init__(self, name, amount, currency, duration):
        self.name = name
        self.amount = amount
        self.currency = currency
        self.duration = duration

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount,
            "currency": self.currency,
            "duration": self.duration,
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

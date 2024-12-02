from extensions import db
from func import hex_id


class PaymentPlans(db.Model):
    __tablename__ = "payment_plans"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(100))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(50))
    duration = db.Column(db.Integer)

    user_sub = db.relationship("Subscriptions", backref="plan", lazy=True)

    def __init__(self, name, amount, currency, duration):
        self.name = name.title()
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


# create payment plan
def create_payment_plan(name, amount, currency, duration):
    if PaymentPlans.query.filter_by(name=name.title()).first():
        return False
    plan = PaymentPlans(name, amount, currency, duration)
    plan.save()
    return plan

def get_payment_plans():
    plans = PaymentPlans.query.all()
    return [plan.to_dict() for plan in plans]


# edit payment plan
def edit_payment_plan(plan_id, name, amount, currency, duration):
    plan = PaymentPlans.query.filter_by(id=plan_id).first()
    if not plan:
        return False
    if name:
        if PaymentPlans.query.filter_by(name=name.title()).first() and name.title() != plan.name:
            return "Name already exists"
        plan.name = name
    if amount:
        plan.amount = float(amount)
    if currency:
      plan.currency = currency
    if duration:
        plan.duration = int(duration)
    plan.update()
    return plan


# delete payment plan
def delete_payment_plan(plan_id):
    plan = PaymentPlans.query.filter_by(id=plan_id).first()
    if not plan:
        return False, None
    plan_name = plan.name
    db.session.delete(plan)
    db.session.commit()
    return True, plan_name

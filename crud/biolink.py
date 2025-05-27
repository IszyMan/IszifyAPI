
from models.bio_link import BioLink
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import extract

# save bio link
# def save_bio_link(bio_link):
#     db.session.add(bio_link)
#     db.session.commit()
#     return True


def get_current_bio_link_count(current_user):
    """Return the current count of BioLink records."""
    now = datetime.utcnow()
    return (
        BioLink.query.filter_by(user=current_user)
        .filter(extract("year", BioLink.created) == now.year)
        .filter(extract("month", BioLink.created) == now.month)
        .count()
    )

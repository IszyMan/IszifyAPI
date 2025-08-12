from extensions import db
from models.giftlink import SavedBank, GiftLinks, GiftType, NicheEnum, UserWallet


def save_or_update_bank_details(
    bank_code, bank_name, account_name, account_number, user_id
):
    saved_bank = SavedBank.query.filter_by(user_id=user_id).first()
    if saved_bank:
        saved_bank.bank_code = bank_code
        saved_bank.bank_name = bank_name
        saved_bank.account_name = account_name
        saved_bank.account_number = account_number
        saved_bank.update()
    else:
        saved_bank = SavedBank(
            user_id=user_id,
            bank_code=bank_code,
            bank_name=bank_name,
            account_name=account_name,
            account_number=account_number,
        )
        saved_bank.save()
    return saved_bank


def get_bank_details(user_id):
    saved_bank = SavedBank.query.filter_by(user_id=user_id).first()
    return saved_bank


def is_valid_enum_value(value, enum_class):
    return value in [e.value for e in enum_class]


# slug exist
def is_slug_exist(slug):
    gift_link = GiftLinks.query.filter_by(slug=slug).first()
    return gift_link


# create gift link
def create_gift_link(
    user_id,
    gift_type,
    niche,
    title,
    description,
    image,
    link,
    goal_amount,
    profile_image,
    cover_image,
    font_style,
    color_theme,
    slug,
):
    gift_link = GiftLinks(
        user_id=user_id,
        gift_type=GiftType(gift_type),
        niche=NicheEnum(niche),
        title=title,
        description=description,
        image=image,
        link=link,
        goal_amount=goal_amount,
        profile_image=profile_image,
        cover_image=cover_image,
        font_style=font_style,
        color_theme=color_theme,
        slug=slug,
    )
    gift_link.save()
    return gift_link


# create user wallet
def create_user_wallet(user_id):
    if UserWallet.query.filter_by(user_id=user_id).first():
        return
    user_wallet = UserWallet(
        user_id=user_id,
    )
    user_wallet.save()
    return user_wallet


def get_user_wallet(user_id):
    user_wallet = UserWallet.query.filter_by(user_id=user_id).first()
    if not user_wallet:
        user_wallet = create_user_wallet(user_id)
    return user_wallet


def get_gift_links_with_pagination(user_id, page, per_page, niche, gift_type, slug):
    gift_links = GiftLinks.query.filter_by(user_id=user_id)
    if niche:
        gift_links = gift_links.filter_by(niche=niche)
    if gift_type:
        gift_links = gift_links.filter_by(gift_type=gift_type)
    if slug:
        gift_links = gift_links.filter(GiftLinks.slug.ilike(f"%{slug}%"))
    gift_links = gift_links.paginate(page=page, per_page=per_page, error_out=False)
    return gift_links


def load_gift_link_by_slug(slug):
    gift_link = GiftLinks.query.filter_by(slug=slug, active=True).first()
    return gift_link

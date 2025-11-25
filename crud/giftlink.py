from extensions import db
from models.giftlink import (
    SavedBank,
    GiftLinks,
    GiftType,
    NicheEnum,
    UserWallet,
    GiftAccount,
    SocialLinks,
)


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


# username exist
def is_username_exist(username):
    gift_account = GiftAccount.query.filter(
        GiftAccount.username.ilike(f"%{username}%")
    ).first()
    return gift_account


def get_one_gift_account(user_id, gift_account_id):
    gift_account = GiftAccount.query.filter_by(
        user_id=user_id, id=gift_account_id
    ).first()
    return gift_account


def get_all_gift_account(user_id, page, per_page):
    gift_accounts = GiftAccount.query.filter_by(user_id=user_id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return gift_accounts


def get_current_user_gift_account(user_id):
    # get only one, the recent one using the created
    gift_accounts = (
        GiftAccount.query.filter_by(user_id=user_id)
        .order_by(GiftAccount.created.desc())
        .first()
    )
    return gift_accounts


def create_gift_account(
    user_id, full_name, username, bio, profile_image, cover_image, website, niche
):
    gift_account = GiftAccount(
        user_id=user_id,
        full_name=full_name,
        username=username,
        bio=bio,
        profile_image=profile_image,
        cover_image=cover_image,
        website=website,
        niche=niche,
    )
    gift_account.save()
    return gift_account


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
        niche=niche,
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


def create_fresh_giftlink(
    user_id,
    gift_account_id,
    title,
    description,
    layout,
    buy_me,
    tip_unit_price,
    min_price,
    button_option,
    sugg_amounts,
    image,
    link,
    active,
    goal_amount,
    start_amount,
    profile_image,
    cover_image,
    font_style,
    color_theme,
    thanks_msg,
    social_links,
):
    gift_link = GiftLinks(
        user_id=user_id,
        title=title,
        layout=layout,
        buy_me=buy_me,
        tip_unit_price=tip_unit_price,
        min_price=min_price,
        button_option=button_option,
        gift_account_id=gift_account_id,
        description=description,
        image=image,
        link=link,
        sugg_amounts=sugg_amounts,
        active=active,
        start_amount=start_amount,
        goal_amount=goal_amount,
        profile_image=profile_image,
        cover_image=cover_image,
        font_style=font_style,
        color_theme=color_theme,
        thanks_msg=thanks_msg,
    )
    db.session.add(gift_link)
    db.session.flush()

    social_link_objects = [
        SocialLinks(
            user_id=user_id,
            gift_account_id=gift_account_id,
            gift_link_id=gift_link.id,
            link=social_lnk,
        )
        for social_lnk in social_links
    ]

    db.session.add_all(social_link_objects)
    db.session.commit()
    return gift_link


def get_one_gift_link(user_id, gift_link_id):
    gift_link = GiftLinks.query.filter_by(id=gift_link_id, user_id=user_id).first()
    return gift_link


# update gift links
def update_gift_link(
    user_id,
    gift_link_id,
    title,
    description,
    layout,
    buy_me,
    tip_unit_price,
    min_price,
    button_option,
    sugg_amounts,
    image,
    link,
    active,
    goal_amount,
    start_amount,
    profile_image,
    cover_image,
    font_style,
    color_theme,
    social_links,
    thanks_msg,
):
    gift_link = GiftLinks.query.filter_by(id=gift_link_id, user_id=user_id).first()
    if not gift_link:
        return False
    gift_link.title = title or new_gift_link.title
    gift_link.description = description or new_gift_link.description
    gift_link.layout = layout or new_gift_link.layout
    gift_link.buy_me = buy_me or new_gift_link.buy_me
    gift_link.tip_unit_price = tip_unit_price or new_gift_link.tip_unit_price
    gift_link.min_price = min_price or new_gift_link.min_price
    gift_link.button_option = button_option or new_gift_link.button_option
    gift_link.sugg_amounts = sugg_amounts or new_gift_link.sugg_amounts
    gift_link.image = image or new_gift_link.image
    gift_link.link = link or new_gift_link.link
    gift_link.active = active or new_gift_link.active
    gift_link.goal_amount = goal_amount or new_gift_link.goal_amount
    gift_link.start_amount = start_amount or new_gift_link.start_amount
    gift_link.profile_image = profile_image or new_gift_link.profile_image
    gift_link.cover_image = cover_image or new_gift_link.cover_image
    gift_link.font_style = font_style or new_gift_link.font_style
    gift_link.color_theme = color_theme or new_gift_link.color_theme
    gift_link.thanks_msg = thanks_msg or new_gift_link.thanks_msg
    gift_link.update()

    # if social_links:
    #     update_social_links(
    #         gift_link_id, user_id, gift_link.gift_account_id, social_links
    #     )
    return True


# update, add or remove social links
def update_social_links(user_id, gift_account_id, new_social_links: list[str]):
    # Get existing social links
    existing_social_links = SocialLinks.query.filter_by(
        gift_account_id=gift_account_id
    ).all()

    existing_links_set = {social_link.link for social_link in existing_social_links}
    new_links_set = set(new_social_links)

    # Links to delete (exist in DB but not in new list)
    links_to_delete = existing_links_set - new_links_set

    # Links to add (exist in new list but not in DB)
    links_to_add = new_links_set - existing_links_set

    # Delete old links only if there are any to delete
    if links_to_delete:
        SocialLinks.query.filter(
            SocialLinks.gift_account_id == gift_account_id,
            SocialLinks.link.in_(links_to_delete),
        ).delete(synchronize_session=False)

    # Add new links only if there are any to add
    if links_to_add:
        new_social_link_objects = [
            SocialLinks(
                user_id=user_id,
                gift_account_id=gift_account_id,
                link=link,
            )
            for link in links_to_add
        ]
        db.session.add_all(new_social_link_objects)

    db.session.commit()
    return True


def get_all_gift_links(user_id, gift_account_id, page, per_page):
    gift_links = GiftLinks.query.filter_by(
        user_id=user_id, gift_account_id=gift_account_id
    ).paginate(page=page, per_page=per_page, error_out=False)
    return gift_links


def update_gift_account(
    user_id,
    gift_account_id,
    full_name,
    username,
    bio,
    profile_image,
    cover_image,
    website,
    niche,
    buy_me,
    tip_unit_price,
    min_price,
    button_option,
    sugg_amounts,
    social_links,
    layout,
    thanks_msg
):
    gift_account = GiftAccount.query.filter_by(
        id=gift_account_id, user_id=user_id
    ).first()
    if not gift_account:
        return False
    gift_account.full_name = full_name or gift_account.full_name
    gift_account.username = username or gift_account.username
    gift_account.bio = bio or gift_account.bio
    gift_account.profile_image = profile_image or gift_account.profile_image
    gift_account.cover_image = cover_image or gift_account.cover_image
    gift_account.website = website or gift_account.website
    gift_account.niche = niche or gift_account.niche
    gift_account.buy_me = buy_me or gift_account.buy_me
    gift_account.tip_unit_price = tip_unit_price or gift_account.tip_unit_price
    gift_account.min_price = min_price or gift_account.min_price
    gift_account.button_option = button_option or gift_account.button_option
    gift_account.sugg_amounts = sugg_amounts or gift_account.sugg_amounts
    gift_account.layout = layout or gift_account.layout
    gift_account.thanks_msg = thanks_msg or gift_account.thanks_msg
    if social_links:
        update_social_links(user_id, gift_account_id, social_links)
    gift_account.update()
    return True

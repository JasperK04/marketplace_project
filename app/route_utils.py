import os
import uuid

import sqlalchemy as sa
from PIL import Image as IM

from app.config import config
from app.extensions import db
from app.models.Image import Image
from app.models.Listing import Listing

app_config = config[os.getenv("FLASK_ENV", "development")]

from app.config import config

app_config = config[os.getenv("FLASK_ENV", "development")]


def get_open_listings_with_images(
    by_user=None,
    by_category=None,
    search=None,
    min_price=None,
    max_price=None,
    condition=None,
    page=1,
    per_page=36,
):
    # basic normalization
    if per_page >= 600:
        per_page = 600
    elif isinstance(per_page, int):
        per_page = per_page if per_page % 12 == 0 else (per_page // 12 + 1) * 12
        per_page = min(max(per_page, 12), 60)
    else:
        per_page = 12

    listings = []
    listings_with_images = (
        db.session.query(Listing, Image.filename)
        .join(
            Image,
            (Image.listingID == Listing.id),
            isouter=True,
        )
        .filter((Listing.sold == False) & (Listing.is_deactivated == False))
    )
    if by_user:
        listings_with_images = listings_with_images.filter(Listing.userID == by_user)
    if by_category:
        listings_with_images = listings_with_images.filter(
            Listing.categoryID == by_category
        )
    if condition:
        condition_value = Listing.normalize_condition(condition)
        listings_with_images = listings_with_images.filter(
            Listing.condition >= condition_value
        )
    if search:
        term = f"%{search}%"
        listings_with_images = listings_with_images.filter(
            sa.or_(Listing.title.ilike(term), Listing.description.ilike(term))
        )
    if min_price is not None:
        listings_with_images = listings_with_images.filter(Listing.price >= min_price)
    if max_price is not None:
        listings_with_images = listings_with_images.filter(Listing.price <= max_price)

    total_items = listings_with_images.count()
    total_pages = -(-total_items // per_page)

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    # Apply pagination
    start = (page - 1) * per_page
    listings_with_images = listings_with_images.offset(start).limit(per_page).all()

    for listing, filename in listings_with_images:
        if filename:
            listing = listing.to_dict()
            listing["filename"] = filename
            listings.append(listing)
        else:
            listings.append(listing.to_dict())

    return listings, per_page, total_pages


def resize_upload_image(file, ratio, size, user_id=None, listing_id=None):
    img = IM.open(file)
    format = img.format

    # find the biggest centered box within the uploaded picture
    x, y = ratio
    width, height = img.size
    max_x = width // x
    max_y = height // y
    max_size = min(max_x, max_y)
    new_width = max_size * x
    new_height = max_size * y
    start_x = (width - new_width) // 2
    start_y = (height - new_height) // 2

    # resize the box within to the requested size
    img = img.resize(
        size,
        resample=1,
        box=(start_x, start_y, start_x + new_width, start_y + new_height),
    )

    filename = (
        f"{uuid.uuid4()}_{f'profile' if user_id else listing_id}.{format.lower()}"  # type: ignore
    )
    folder = app_config.PICTURE_FOLDER
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    img.save(filepath, format)

    assert listing_id or user_id, "requires a listing_id or user_id"

    new_image = Image(
        filepath=filepath, filename=filename, listingID=listing_id, userID=user_id
    )

    return new_image


def delete_images(listing_id=None, user_id=None):
    # first query the filepaths so the files on disk can be deleted
    assert listing_id or user_id, "one or the other is required"
    if listing_id:
        images = db.session.execute(
            sa.select(Image).where(Image.listingID == listing_id)
        ).scalars()
        for image in images:
            if image and os.path.exists(image.filepath):
                os.remove(image.filepath)
                # then delete images in database
                db.session.delete(image)
                db.session.commit()
    else:
        image = db.session.execute(
            sa.select(Image).where(Image.userID == user_id)
        ).scalar()
        if image and os.path.exists(image.filepath):
            os.remove(image.filepath)
            # then delete image in database
            db.session.delete(image)
            db.session.commit()

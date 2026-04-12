import os
import uuid
from typing import cast

import sqlalchemy as sa
from PIL import Image as IM

from app.config import config
from app.extensions import db
from app.models.Image import Image
from app.models.Listing import Listing

app_config = config[os.getenv("FLASK_ENV", "development")]


def get_open_listings_with_images(
    by_user=None,
    by_category=None,
    search=None,
    min_price=None,
    max_price=None,
    condition=None,
    include_deactivated=False,
    include_only_deactivated=False,
    include_sold=False,
    include_only_sold=False,
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
    # include Image.id and filename so templates can request the binary route
    listings_with_images = db.session.query(Listing, Image.id, Image.filename).join(
        Image,
        (Image.listingID == Listing.id),
        isouter=True,
    )
    if include_only_sold:
        listings_with_images = listings_with_images.filter(Listing.sold.is_(True))
    elif not include_sold:
        listings_with_images = listings_with_images.filter(Listing.sold.is_(False))
    if include_only_deactivated:
        listings_with_images = listings_with_images.filter(
            Listing.is_deactivated.is_(True)
        )
    elif not include_deactivated:
        listings_with_images = listings_with_images.filter(
            Listing.is_deactivated.is_(False)
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
            Listing.condition == condition_value
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

    for row in listings_with_images:
        # row is (Listing, image_id, filename) when Image exists, otherwise (Listing, None, None)
        listing_obj = row[0]
        image_id = row[1]
        filename = row[2]
        listing = listing_obj.to_dict()
        if image_id:
            listing["image_id"] = image_id
            listing["filename"] = filename
        listings.append(listing)

    return listings, per_page, total_pages


def resize_upload_image(
    file, ratio, size, user_id: int | None = None, listing_id: int | None = None
):
    img = IM.open(file)
    format = "webp"

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

    filename = f"{uuid.uuid4()}_{'profile' if user_id else listing_id}.{format}"  # type: ignore

    # save to bytes in webp format
    from io import BytesIO

    buf = BytesIO()
    img.save(buf, format=format)
    img_bytes = buf.getvalue()

    assert listing_id or user_id, "requires a listing_id or user_id"

    image_data = cast(
        dict[str, str | int | None],
        {
            "data": img_bytes,
            "filename": filename,
            "listingID": listing_id,
            "userID": user_id,
        },
    )
    new_image = Image().from_dict(image_data)

    return new_image


def delete_images(listing_id=None, user_id=None):
    # first query the filepaths so the files on disk can be deleted
    assert listing_id or user_id, "one or the other is required"
    if listing_id:
        images = db.session.execute(
            sa.select(Image).where(Image.listingID == listing_id)
        ).scalars()
        for image in images:
            # delete image record from DB (legacy on-disk files were handled during migration)
            db.session.delete(image)
            db.session.commit()
    else:
        image = db.session.execute(
            sa.select(Image).where(Image.userID == user_id)
        ).scalar()
        if image:
            db.session.delete(image)
            db.session.commit()

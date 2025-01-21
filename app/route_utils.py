import uuid
import os
import sqlalchemy as sa

import os
import sqlalchemy as sa
from PIL import Image as IM
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.Listing import Listing
from app.models.Image import Image
from app.config import config

app_config = config[os.getenv("FLASK_ENV", "development")]

from app.config import config

app_config = config[os.getenv("FLASK_ENV", "development")]


def get_open_listings_with_images(limit:int|None=None, by_user:int|None=None, by_category:int|None=None):
    listings = []
    listings_with_images = (
        db.session.query(Listing, Image.filename)
        .join(
            Image,
            (Image.listingID == Listing.id) & (Image.variant == "original"),
            isouter=True,
        )
        .filter((Listing.sold == False) & (Listing.is_deactivated == False))
    )
    if by_user:
        listings_with_images = listings_with_images.filter(Listing.userID == by_user)
    if by_category:
        listings_with_images = listings_with_images.filter(Listing.categoryID == by_category)
    if limit:
        listings_with_images = listings_with_images.limit(limit)
    listings_with_images = listings_with_images.all()
    for listing, filename in listings_with_images:
        if filename:
            listing = listing.to_dict()
            listing["filename"] = filename
            listings.append(listing)
        else:
            listings.append(listing.to_dict())

    return listings


def resize_upload_image(file, size, user_id, listing_id, folder, type, variant):
    image = IM.open(file)
    img = image.copy()

    # if image is smaller than preferred size, thumbnail (resize with same aspect ratio) cannot be used
    if img.width < size[0] or img.height < size[1]:
        img = img.resize(
            size, resample=1
        )  # 1=LANCZOS resampling leads to higher quality pictures
    else:
        img.thumbnail(size, resample=1)
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    folder = app_config.UPLOAD_FOLDER if folder == "UPLOAD_FOLDER" else app_config.RESIZED_FOLDER
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    img.save(filepath)
    if type == "listing":
        new_image = Image(
            filename=filename,
            filepath=filepath,
            type=type,
            listingID=listing_id,
            variant=variant,
        )
    else:
        new_image = Image(
            filename=filename,
            filepath=filepath,
            type=type,
            userID=user_id,
            variant=variant,
        )   
    return new_image


def delete_images(id:int,variant:str):
    # first query the filepaths so the files on disk can be deleted
    if variant == "listing":
        images = db.session.execute(
            sa.select(Image).where(Image.listingID == id)
        ).scalars()
        for image in images:
            if image and os.path.exists(image.filepath):
                os.remove(image.filepath)
                # then delete images in database
                db.session.delete(image)
                db.session.commit()
    else:
        image = db.session.execute(
            sa.select(Image).where(Image.userID == id)
        ).scalar()
        if image and os.path.exists(image.filepath):
            os.remove(image.filepath)
            # then delete image in database
            db.session.delete(image)
            db.session.commit()

import json
from base64 import b64encode
from io import BytesIO

import qrcode
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField

from backend.database_schema import db

player_page = Blueprint("player", __name__)


class PlayerNameForm(FlaskForm):
    player_name = StringField("Spielername")


def convert_pil_image_to_bytes(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io


@player_page.route("/player", methods=["GET", "POST"])
@login_required
def player_site():
    player_name = current_user.player_name

    if player_name is None:
        form = PlayerNameForm()

        if form.validate_on_submit():
            player_name = form.player_name.data

            current_user.player_name = player_name
            db.session.commit()

            return redirect(url_for("player.player_site"))

        return render_template("player_site.html", form=form)

    qr = qrcode.QRCode(
        version=None,  # fit=True below sets this automatically
        box_size=8,  # How many pixels each box of the QR code is
        border=4  # Per QR specification
    )

    to_encode = {
        "player_id": current_user.player_id,
        "email": current_user.email
    }

    qr.add_data(b64encode(json.dumps(to_encode).encode("ascii")))

    image_io = convert_pil_image_to_bytes(qr.make_image(fit=True, fill_color="black", back_color="white"))
    player_qr_code_b64 = b64encode(image_io.getvalue()).decode("ascii")

    return render_template("player_site.html", player_name=player_name, player_qr_code_b64=player_qr_code_b64)

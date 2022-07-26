from flask import Blueprint, abort, render_template
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import EmailField, validators

from backend.database_schema import EmailWhitelist, db

admin_page = Blueprint("admin", __name__)


class WhiteListForm(FlaskForm):
    email = EmailField("E-Mail", validators=[validators.InputRequired()])


@admin_page.route("/admin", methods=["GET", "POST"])
@login_required
def admin_site():
    if not current_user.is_admin:
        return abort(403)

    form = WhiteListForm()

    if form.validate_on_submit():
        email = form.email.data

        new_whitelist_entry = EmailWhitelist(email=email)

        db.session.add(new_whitelist_entry)
        db.session.commit()

    return render_template("admin_site.html", form=form)

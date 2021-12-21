from flask_login import current_user, login_required
from flask import flash, request, redirect, url_for, current_app, render_template

from app import db
from app.main import bp
from app.main.forms import TripForm, EditProfileForm
from app.models import Trip, User


@bp.route("/", methods=["GET", "POST"])
@bp.route("/index", methods=["GET", "POST"])
@login_required
def index():
    remaining_days = str(current_user.get_remaining_days())
    form = TripForm()
    if form.validate_on_submit():
        trip = Trip(start=form.start.data, end=form.end.data, traveller=current_user)
        db.session.add(trip)
        db.session.commit()
        flash("Trip added!")
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type=int)
    trips = current_user.trips.order_by(Trip.start.desc()).paginate(
        page, current_app.config["TRIPS_PER_PAGE"], False
    )
    next_url = url_for("main.index", page=trips.next_num) if trips.has_next else None
    prev_url = url_for("main.index", page=trips.prev_num) if trips.has_prev else None
    return render_template(
        "index.html",
        title="Home",
        remaining_days=remaining_days,
        form=form,
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/user/<id>")
@login_required
def user(id):
    user = User.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    trips = user.trips.order_by(Trip.start.desc()).paginate(
        page, current_app.config["TRIPS_PER_PAGE"], False
    )
    next_url = (
        url_for("main.user", id=user.id, page=trips.next_num)
        if trips.has_next
        else None
    )
    prev_url = (
        url_for("main.user", id=user.id, page=trips.prev_num)
        if trips.has_prev
        else None
    )
    return render_template(
        "user.html",
        user=user,
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.surname = form.surname.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        form.first_name.data = current_user.first_name
        form.surname.data = current_user.surname
    return render_template("edit_profile.html", title="Edit Profile", form=form)

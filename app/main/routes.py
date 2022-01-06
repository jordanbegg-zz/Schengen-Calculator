from flask_login import current_user, login_required
from flask import flash, request, redirect, url_for, current_app, render_template
import datetime

from app import db
from app.main import bp
from app.main.forms import TripForm, EditProfileForm, EndDateForm, DeleteTripForm
from app.main.panels import EditProfilePanel
from app.models import Trip, User


@bp.route(
    "/", methods=["GET", "POST"], defaults={"date": datetime.date.today().isoformat()}
)
@bp.route(
    "/index",
    methods=["GET", "POST"],
    defaults={"date": datetime.date.today().isoformat()},
)
@bp.route(
    "/index/<date>",
    methods=["GET", "POST"],
)
@login_required
def index(date):
    date = datetime.date.fromisoformat(date)
    remaining_days = str(current_user.get_remaining_days(date))
    form = TripForm()
    end_date_form = EndDateForm()
    if request.method == "POST":
        if request.form.get("submit_delete_trip"):
            trip = Trip.query.get(request.form.get("trip_id"))
            db.session.delete(trip)
            db.session.commit()
            flash("Trip deleted!")
        elif request.form.get("submit_add_trip"):
            trip = Trip(
                start=form.start.data, end=form.end.data, traveller=current_user
            )
            db.session.add(trip)
            db.session.commit()
            flash("Trip added!")
        return redirect(url_for("main.index"))
    if end_date_form.validate_on_submit():
        return redirect(url_for("main.index", date=end_date_form.end.data))
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
        end_date_form=end_date_form,
        form=form,
        delete_trip_form=DeleteTripForm,
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
        date=date,
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
    panel = EditProfilePanel(current_user)
    # form = EditProfileForm()
    if request.method == "POST":
        if (
            request.form.get("submit_edit_profile")
            and panel.edit_profile_form.validate()
        ):
            current_user.first_name = panel.edit_profile_form.first_name.data
            current_user.surname = panel.edit_profile_form.surname.data
            db.session.commit()
            flash("Your changes have been saved.")
            return redirect(url_for("main.edit_profile"))
    # if form.validate_on_submit():
    #     current_user.first_name = form.first_name.data
    #     current_user.surname = form.surname.data
    #     db.session.commit()
    #     flash("Your changes have been saved.")
    #     return redirect(url_for("main.edit_profile"))
    elif request.method == "GET":
        panel.edit_profile_form.first_name.data = current_user.first_name
        panel.edit_profile_form.surname.data = current_user.surname
    return render_template("edit_profile.html", title="Edit Profile", panel=panel)

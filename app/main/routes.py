import json
import datetime

from flask_login import current_user, login_required
from flask import flash, request, redirect, url_for, current_app, render_template
import plotly
import plotly.graph_objects as go

from app import db
from app.main import bp
from app.main.forms import TripForm, EditProfileForm, EndDateForm, DeleteTripForm
from app.models import Trip


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
    remaining_days = current_user.get_remaining_days(date)
    current_remaining_days = str(remaining_days[-1])
    end_date_form = EndDateForm()
    if end_date_form.validate_on_submit():
        return redirect(url_for("main.index", date=end_date_form.end.data))
    page = request.args.get("page", 1, type=int)
    trips = current_user.trips.order_by(Trip.start.desc()).paginate(
        page, current_app.config["TRIPS_PER_PAGE"], False
    )
    next_url = url_for("main.index", page=trips.next_num) if trips.has_next else None
    prev_url = url_for("main.index", page=trips.prev_num) if trips.has_prev else None

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=remaining_days.index,
            y=remaining_days,
            fill="tozeroy",
            line_color="rgb(85,51,255)",
        )
    )
    fig.update_xaxes(title_text="Date"),
    fig.update_yaxes(title_text="Days Remaining")
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "index.html",
        title="Home",
        current_remaining_days=current_remaining_days,
        end_date_form=end_date_form,
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
        date=date,
        fig_json=fig_json,
    )


@bp.route("/user", methods=["GET", "POST"])
@login_required
def user():
    page = request.args.get("page", 1, type=int)
    trips = current_user.trips.order_by(Trip.start.desc()).paginate(
        page, current_app.config["TRIPS_PER_PAGE"], False
    )
    next_url = url_for("main.user", page=trips.next_num) if trips.has_next else None
    prev_url = url_for("main.user", page=trips.prev_num) if trips.has_prev else None
    if request.method == "POST" and request.form.get("submit_delete_trip"):
        trip = Trip.query.get(request.form.get("trip_id"))
        db.session.delete(trip)
        db.session.commit()
        flash("Trip deleted!")
        return redirect(url_for("main.user"))

    return render_template(
        "user.html",
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
        delete_trip_form=DeleteTripForm,
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


@bp.route("/trips", methods=["GET", "POST"])
@login_required
def trips():
    form = TripForm()
    page = request.args.get("page", 1, type=int)
    trips = current_user.trips.order_by(Trip.start.desc()).paginate(
        page, current_app.config["TRIPS_PER_PAGE"], False
    )
    next_url = url_for("main.trips", page=trips.next_num) if trips.has_next else None
    prev_url = url_for("main.trips", page=trips.prev_num) if trips.has_prev else None

    if request.method == "POST" and request.form.get("submit_delete_trip"):
        trip = Trip.query.get(request.form.get("trip_id"))
        db.session.delete(trip)
        db.session.commit()
        flash("Trip deleted!")
        return redirect(url_for("main.trips"))
    if form.validate_on_submit():
        trip = Trip(start=form.start.data, end=form.end.data, traveller=current_user)
        db.session.add(trip)
        db.session.commit()
        flash("Trip added!")
        return redirect(url_for("main.trips"))
    return render_template(
        "trips.html",
        form=form,
        trips=trips.items,
        next_url=next_url,
        prev_url=prev_url,
        delete_trip_form=DeleteTripForm,
    )

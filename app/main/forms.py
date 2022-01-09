from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from app.models import Trip
from flask_login import current_user


class TripForm(FlaskForm):
    start = DateField("Start Date", validators=[DataRequired()])
    end = DateField("End Date", validators=[DataRequired()])
    submit_add_trip = SubmitField("Submit")

    def validate_end(self, end):
        if end.data < self.start.data:
            raise ValidationError("End date cannot be before start date.")
        trip = Trip.query.filter_by(
            start=self.start.data, end=end.data, traveller=current_user
        ).first()
        if trip:
            raise ValidationError("Trip already exists!")


class EditProfileForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    submit_edit_profile = SubmitField("Submit")


class EndDateForm(FlaskForm):
    end = DateField("Calculation End Date", validators=[DataRequired()])
    submit_update_end_date = SubmitField("Submit")


class DeleteTripForm(FlaskForm):
    trip_id = HiddenField()
    submit_delete_trip = SubmitField("Delete")

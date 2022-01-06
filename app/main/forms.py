from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, HiddenField
from wtforms.validators import DataRequired


class TripForm(FlaskForm):
    start = DateField("Start Date", validators=[DataRequired()])
    end = DateField("End Date", validators=[DataRequired()])
    submit_add_trip = SubmitField("Submit")


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

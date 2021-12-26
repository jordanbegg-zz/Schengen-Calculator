import bootlets.templates as bl
from flask import request

from app.main.forms import EditProfileForm


class EditProfilePanel:
    def __init__(self, user):
        self.user = user
        self.edit_profile_form = EditProfileForm(request.form)

    def build(self):
        return bl.Container(bl.H("Edit Profile"), bl.Form(self.edit_profile_form))

    def draw(self):
        return self.build().draw()

from wtforms import Form, StringField, DecimalField, IntegerField, TextAreaField, PasswordField, validators


class RegisterForm(Form):
    name = StringField("Full Name", [validators.Length(min=1, max=64)])
    username = StringField("Username", [validators.Length(min=4, max=32)])
    email = StringField("Email", [validators.Length(min=6, max=64)])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.Length(min=8),
            validators.EqualTo("confirm_password", message="Passwords do not match")
        ]
    )
    confirm_password = PasswordField("Confirm Password")


class SendLinkTForm(Form):
    send_to_address = StringField('Wallet Address', [validators.Length(min=32, max=32)])
    amount = StringField("Amount", [validators.Length(min=1, max=64)])

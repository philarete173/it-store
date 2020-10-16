from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, BooleanField, SubmitField, FieldList, PasswordField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Required, Email, EqualTo, Optional, NumberRange, InputRequired, ValidationError
from app.models import User, Cartridge, Printer, Office, CartridgeStock, PrinterStock


def cartridgeChoice():
    return Cartridge.query.all()


def printerChoice():
    return Printer.query.all()


def officeChoice():
    return Office.query.all()
"""
def printerInOffice(office):
    printers = []
    for printer in office.printers:
        printers.append(Printer.query.filter_by(id=printer.id).first())
    return printers

def cartridgeInPrinter(printer):
    cartridges= []
    for cartridge in printer.cartridges:
        cartridges.append(Cartridge.query.filter_by(id=cartridge.id).first())
    return cartridges
"""


class AddTypeForm(FlaskForm):
    type = SelectField('Add info about', choices=[('cartridge', 'Cartridge'), ('printer', 'Printer'), ('office', 'Office')])
    submit = SubmitField('Add Data')


class AddCartridgeForm(FlaskForm):
    cartridge_model = StringField('Model', validators=[DataRequired()])
    color = SelectField('Cartridge Color', validators=[InputRequired()], choices=[('Cyan', 'Cyan'), ('Magenta', 'Magenta'), ('Yellow', 'Yellow'), ('Black', 'Black')])
    submit = SubmitField('Add Data')


class AddPrinterForm(FlaskForm):
    brand = StringField('Brand', validators=[DataRequired()])
    printer_model = StringField('Model', validators=[DataRequired()])
    cartridges = FieldList(QuerySelectField('Compatible cartridge', validators=[Required()], query_factory=cartridgeChoice), min_entries=1, max_entries=4)
    submit = SubmitField('Add Data')


class AddOfficeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    place = StringField('Place', validators=[DataRequired()])
    printers = FieldList(QuerySelectField('Printer', validators=[InputRequired()], query_factory=printerChoice), min_entries=1)
    submit = SubmitField('Add Data')


class CartridgeStockForm(FlaskForm):
    office = QuerySelectField('Office', validators=[InputRequired()], query_factory=officeChoice)
    cartridge = QuerySelectField('Cartridge', validators=[InputRequired()], query_factory=cartridgeChoice)
    in_out = SelectField('In/Out', choices=[(True, 'In'), (False, 'Out')], validators=[InputRequired()], coerce=lambda x: x == 'True')
    amount = IntegerField('Amount', validators=[NumberRange(min=1), DataRequired()])
    submit = SubmitField('Add Data')


class PrinterStockForm(FlaskForm):
    office = QuerySelectField('Office', validators=[InputRequired()], query_factory=officeChoice)
    printer = QuerySelectField('Printer', validators=[InputRequired()], query_factory=printerChoice)
    in_out = SelectField('In/Out', choices=[(True, 'In'), (False, 'Out')], validators=[InputRequired()], coerce=lambda x: x == 'True')
    amount = IntegerField('Amount', validators=[NumberRange(min=1), DataRequired()])
    submit = SubmitField('Add Data')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

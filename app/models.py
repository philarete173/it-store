from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

cartridges = db.Table('cartridges',
                    db.Column('cartridge_id', db.Integer, db.ForeignKey('cartridge.id')),
                    db.Column('printer_id', db.Integer, db.ForeignKey('printer.id'))
                    )

printers = db.Table('printers',
                    db.Column('printer_id', db.Integer, db.ForeignKey('printer.id')),
                    db.Column('office_id', db.Integer, db.ForeignKey('office.id'))
                    )


def date_formatter(view, context, model, name):
    return model.date.strftime('%d.%m.%Y %H:%M:%S')


def cartridge_formatter(view, context, model, name):
    return Cartridge.query.filter_by(id=model.cartridge).first().cartridge_model


def printer_formatter(view, context, model, name):
    return Printer.query.filter_by(id=model.printer).first().printer_model


def office_formatter(view, context, model, name):
    return Office.query.filter_by(id=model.office).first().name


def role_formatter(view, context, model, name):
    return Role.query.filter_by(id=model.id).first().name


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return self.name


class RoleView(ModelView):
    column_formatters = {'name': role_formatter}


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary='user_roles')
    cartridge_stock_records = db.relationship('CartridgeStock', backref='user', lazy='dynamic')
    printer_stock_records = db.relationship('PrinterStock', backref='user', lazy='dynamic')

    def __repr__(self):
        return 'User {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        search_role = Role.query.filter_by(name=role).first()
        if search_role in self.roles:
            return True
        else:
            return False

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))


class UserView(ModelView):
    can_create=False
    column_list = ['username', 'email', 'roles']


class Cartridge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cartridge_model = db.Column(db.String(64), index=True, unique=True)
    color = db.Column(db.String(10), index=True)

    def __repr__(self):
        return '{}'.format(self.cartridge_model)


class CartridgeView(ModelView):
    can_create = False


class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(64), index=True)
    printer_model = db.Column(db.String(64), index=True, unique=True)
    cartridges = db.relationship('Cartridge', secondary=cartridges, backref=db.backref('printers', lazy='dynamic'))

    def __repr__(self):
        return '{} {}'.format(self.brand, self.printer_model)


class PrinterView(ModelView):
    can_create = False


class Office(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True)
    place = db.Column(db.String(250), index=True)
    printers = db.relationship('Printer', secondary=printers, backref=db.backref('offices', lazy='dynamic'))

    def __repr__(self):
        return '{} at {}'.format(self.name, self.place)


class OfficeView(ModelView):
    can_create = False


class CartridgeStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.now)
    in_out = db.Column(db.Boolean)
    office = db.Column(db.Integer, db.ForeignKey('office.id'))
    cartridge = db.Column(db.Integer, db.ForeignKey('cartridge.id'))
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        self.office = Office.query.filter_by(id=self.office).first().name
        self.cartridge = Cartridge.query.filter_by(id=self.cartridge).first().cartridge_model
        return '{} to {} , amount {}, {}'.format(self.cartridge, self.office, self.amount, self.in_out)


class CartridgeStockView(ModelView):
    can_create = False
    column_hide_backrefs = False
    column_list = [CartridgeStock.date, CartridgeStock.in_out, CartridgeStock.office, CartridgeStock.cartridge, CartridgeStock.amount]
    column_formatters = {'date': date_formatter, 'office': office_formatter, 'cartridge': cartridge_formatter}


class PrinterStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.now)
    in_out = db.Column(db.Boolean)
    office = db.Column(db.Integer, db.ForeignKey('office.id'))
    printer = db.Column(db.Integer, db.ForeignKey('printer.id'))
    amount = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        self.office = Office.query.filter_by(id=self.office).first().name
        self.printer = Printer.query.filter_by(id=self.printer).first().printer_model
        return '{} to {} , amount {}'.format(self.printer, self.office, self.amount)


class PrinterStockView(ModelView):
    can_create = False
    column_list = [PrinterStock.date, PrinterStock.in_out, PrinterStock.office, PrinterStock.printer, PrinterStock.amount]
    column_formatters = {'date': date_formatter, 'office': office_formatter, 'printer': printer_formatter}

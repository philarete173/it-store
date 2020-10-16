from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_admin import expose, AdminIndexView, Admin
from app import app, db
from app.forms import AddTypeForm, AddCartridgeForm, AddPrinterForm, AddOfficeForm, CartridgeStockForm, \
    PrinterStockForm, LoginForm, RegistrationForm
from app.models import User, Role, RoleView, UserRoles, UserView, Cartridge, CartridgeView, Printer, PrinterView, \
    Office, OfficeView, CartridgeStock, CartridgeStockView, PrinterStock, PrinterStockView
from datetime import datetime


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            if not current_user.has_role('Admin'):
                flash('You do not have enough permissons for opening this page.')
                return redirect(url_for('index'))
            return super(MyAdminIndexView, self).index()
        else:
            return redirect(url_for('index'))


admin = Admin(app, name='IT Store', index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(UserView(User, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(CartridgeView(Cartridge, db.session))
admin.add_view(PrinterView(Printer, db.session))
admin.add_view(OfficeView(Office, db.session))
admin.add_view(CartridgeStockView(CartridgeStock, db.session))
admin.add_view(PrinterStockView(PrinterStock, db.session))


def cartridgeAmount(cartridge):
    cart_amount = 0
    for i in CartridgeStock.query.filter_by(cartridge=cartridge.id, in_out=True):
        cart_amount += i.amount
    for j in CartridgeStock.query.filter_by(cartridge=cartridge.id, in_out=False):
        cart_amount -= j.amount
    return cart_amount


def printerAmount(printer):
    printer_amount = 0
    for i in PrinterStock.query.filter_by(printer=printer.id, in_out=True):
        printer_amount += i.amount
    for j in PrinterStock.query.filter_by(printer=printer.id, in_out=False):
        printer_amount -= j.amount
    return printer_amount


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    cartridge_stock = CartridgeStock.query.order_by(CartridgeStock.date.desc()).all()
    cartridge_stock_edit = [{'date': record.date,
                             'place': Office.query.filter_by(id=record.office).first().place,
                             'office': Office.query.filter_by(id=record.office).first().name,
                             'cartridge': Cartridge.query.filter_by(id=record.cartridge).first().cartridge_model,
                             'in_out': record.in_out,
                             'amount': record.amount} for record in cartridge_stock]
    cartridges_amount = [{'model': cartridge.cartridge_model,
                          'amount': cartridgeAmount(cartridge)} for cartridge in Cartridge.query.all()]
    printer_stock = PrinterStock.query.order_by(PrinterStock.date.desc()).all()
    printer_stock_edit = [{'date': record.date,
                           'place': Office.query.filter_by(id=record.office).first().place,
                           'office': Office.query.filter_by(id=record.office).first().name,
                           'printer': Printer.query.filter_by(id=record.printer).first().printer_model,
                           'in_out': record.in_out,
                           'amount': record.amount} for record in printer_stock]
    printers_amount = [{'model': printer.printer_model,
                        'amount': printerAmount(printer)} for printer in Printer.query.all()]
    return render_template('index.html', cartridge_stock=cartridge_stock_edit, cartridges_amount=cartridges_amount,
                           printer_stock=printer_stock_edit, printers_amount=printers_amount)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Successfully logged in as {}'.format(user.username))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        default_role = Role.query.filter_by(name='User').first()
        user.roles.append(default_role)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddTypeForm()
    if form.validate_on_submit():
        type = form.type.data
        return redirect(url_for('add_data', type=type))
    return render_template('add.html', title='Add Data', form=form)


@app.route('/add_<type>', methods=['GET', 'POST'])
@login_required
def add_data(type):
    if type == 'cartridge':
        form = AddCartridgeForm()
        if form.validate_on_submit():
            cartridge = Cartridge(cartridge_model=form.cartridge_model.data, color=form.color.data)
            db.session.add(cartridge)
            db.session.commit()
            flash('Info about {} {} successfully added.'.format(type, cartridge))
            return redirect(url_for('index'))
    elif type == 'printer':
        form = AddPrinterForm()
        if form.validate_on_submit():
            printer = Printer(brand=form.brand.data, printer_model=form.printer_model.data)
            for entry in form.cartridges.entries:
                printer.cartridges.append(entry.data)
            db.session.add(printer)
            db.session.commit()
            flash('Info about {} {} successfully added.'.format(type, printer))
            return redirect(url_for('index'))
    elif type == 'office':
        form = AddOfficeForm()
        if form.validate_on_submit():
            office = Office(name=form.name.data, place=form.place.data)
            for entry in form.printers.entries:
                office.printers.append(entry.data)
            db.session.add(office)
            db.session.commit()
            flash('Info about {} {} successfully added.'.format(type, office))
            return redirect(url_for('index'))
    return render_template('add_data.html', title='Add Data', type=type, form=form)


@app.route('/cartridgestock', methods=['GET', 'POST'])
@login_required
def cartridgestock():
    form = CartridgeStockForm()
    if form.validate_on_submit():
        stockitem = CartridgeStock(in_out=form.in_out.data, office=form.office.data.id,
                                   cartridge=form.cartridge.data.id, amount=form.amount.data, user=current_user)
        match = False
        if form.in_out.data is False:
            for printer in Office.query.filter_by(id=form.office.data.id).first().printers:
                if form.cartridge.data.id in printer.cartridges and form.amount.data < cartridgeAmount(
                        form.cartridge.data):
                    match = True
        if form.in_out.data is True and form.office.data.id == 1:
            match = True
        if match:
            db.session.add(stockitem)
            db.session.commit()
            flash('Record added')
            return redirect(url_for('index'))
        else:
            flash('Something went wrong. Check the entered data.')
            return redirect(url_for('index'))
    return render_template('cartridgestock.html', form=form)


@app.route('/printerstock', methods=['GET', 'POST'])
@login_required
def printerstock():
    form = PrinterStockForm()
    if form.validate_on_submit():
        stockitem = PrinterStock(in_out=form.in_out.data, office=form.office.data.id, printer=form.printer.data.id,
                                 amount=form.amount.data, user=current_user)
        match = False
        if form.in_out.data is False and form.amount.data < printerAmount(form.printer.data):
            match = True
        if form.in_out.data is True and form.office.data.id == 1:
            match = True
        if match:
            db.session.add(stockitem)
            db.session.commit()
            flash('Record added')
            return redirect(url_for('index'))
        else:
            flash('Something went wrong. Check the entered data.')
            return redirect(url_for('index'))
    return render_template('printerstock.html', form=form)

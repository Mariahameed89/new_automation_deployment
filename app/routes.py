from pickle import FALSE
import requests
from selenium.webdriver.support import expected_conditions as EC
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import atexit

from .models import Order
from .email_utils import send_admin_email, send_pin_email, send_order_email
from .automation import bot_automation
from . import db
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random
import time
from concurrent.futures import ThreadPoolExecutor

main_bp = Blueprint('main', __name__)
g_driver = None


def browser_init():
    global g_driver
    if g_driver is None:
        try:
            proxy_username = "9fa3c330655cbd7ee012"
            proxy_password = "3607b7d7a975d149"
            proxy_address = "gw.dataimpulse.com"
            proxy_port = "16000"

            # formulate the proxy URL with authentication for dataimpulse
            proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"

            # Set Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            

            # Set up the WebDriver
           # g_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

            # Heroku environment
            chromedriver_path = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
            g_driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options, seleniumwire_options=proxy_options)
            

            # Open a new browser window
            g_driver.execute_script("window.open('');")
            g_driver.switch_to.window(g_driver.window_handles[0])
            g_driver.get('https://accounts.nintendo.com')

            # Clean up the WebDriver when the application exits
            atexit.register(cleanup_driver)

            print('Chrome started successfully!')
        except Exception as error:
            print(f"Error during WebDriver or automation process - {error}")
            g_driver = None
    return g_driver


def cleanup_driver():
    global g_driver
    if g_driver is not None:
        g_driver.get("https://accounts.nintendo.com")
        g_driver.delete_all_cookies()


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/save', methods=['POST'])
def save():
    order_id = request.form['order_id']
    password = request.form['password']
    big_link = request.form['big_link']
    email = request.form.get('email', '')

    updated_rows = Order.query.filter_by(order_id=order_id).update({
        'password': password,
        'big_link': big_link,
        'email': email,
        'role': 'admin'
    })

    if updated_rows:
        # Commit the update to the database
        db.session.commit()
        flash(f"Order ID {order_id} exists. Data has been updated.", 'info')
    else:
        # Create a new order if no existing order was found
        new_order = Order(order_id=order_id, password=password, big_link=big_link, email=email, role='admin',
                          pin_code='')
        db.session.add(new_order)
        db.session.commit()
        flash('Order saved successfully!', 'success')

    return render_template('index.html', order_id=order_id, password=password, big_link=big_link, email=email,
                           show_email_popup=FALSE)


@main_bp.route('/view_db')
def view_db():
    orders = Order.query.all()
    return render_template('view_db.html', orders=orders)


@main_bp.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'POST':
        order_id = request.form['order_id']
        access_code = request.form.get('access_code')
        email = request.form['email']

        if not access_code:
            flash("Access code is required!", "error")
            return redirect(url_for('main.customer'))

        is_order_id = Order.query.filter_by(order_id=order_id).first()
        if is_order_id:
            is_pin_code = is_order_id.pin_code
            existing_password = is_order_id.password
            if is_pin_code:
                flash(f"{existing_password}", "info")
                return redirect(url_for('main.customer'))

        existing_order = Order.query.filter_by(order_id=order_id).first()
        if existing_order:
            existing_order.access_code = access_code
            existing_order.email = email
            db.session.commit()
            print("access code", access_code)

            if existing_order.pin_code:
                print("pin_code", existing_order.pin_code)
                flash(
                    f"Already Login! Your 5-digit pin code is: {existing_order.pin_code} and password is: {existing_order.password}",
                    "success")
            else:
                g_driver = browser_init()
                if g_driver:
                    pin_code, password = bot_automation(order_id, g_driver)
                    if pin_code:
                        existing_order.pin_code = pin_code
                        existing_order.password = password
                        db.session.commit()

                        flash(f"Your 5-digit pin code is: {pin_code}  {password}", "success")
                        print("saved password and access code in database", password, access_code)
                    else:
                        flash("Access code expired.....", "error")
        else:
            flash("Order ID not found. Please check your details and try again.", "error")

        return redirect(url_for('main.customer'))

    return render_template('customer.html')


@main_bp.route('/print_orders')
def print_orders():
    all_orders = Order.query.all()
    orders_data = ""
    for order in all_orders:
        orders_data += f"ID: {order.id}, Order ID: {order.order_id}, Password: {order.password}, "
        orders_data += f"Big Link: {order.big_link}, Email: {order.email},  Access Code: {order.access_code}\n"

    return f"<pre>{orders_data}</pre>"

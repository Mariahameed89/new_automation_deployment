from flask import Blueprint, render_template, request, flash
from .models import Order
from .automation import bot_automation
from . import db
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import atexit

logging.basicConfig(level=logging.INFO)

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

            # formulate the proxy url with authentication for dataimpulse
            proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"

            # Set proxy options for SeleniumWire
            proxy_options = {
                "proxy": {
                    "http": proxy_url,
                    "https": proxy_url
                }
            }
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            # g_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            chromedriver_path = "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"  # Use correct path
            g_driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options, seleniumwire_options=proxy_options)
            g_driver.get('https://accounts.nintendo.com')
            atexit.register(cleanup_driver)
        except Exception as error:
            logging.error(f"Error initializing browser: {error}")
            g_driver = None
    return g_driver

def cleanup_driver():
    global g_driver
    if g_driver:
        g_driver.quit()
        g_driver = None

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/save', methods=['POST'])
def save():
    try:
        order_id = request.form['order_id']
        password = request.form['password']
        big_link = request.form['big_link']
        email = request.form.get('email', '')

        order = Order.query.filter_by(order_id=order_id).first()
        if order:
            order.password = password
            order.big_link = big_link
            order.email = email
            db.session.commit()
            flash("Order updated successfully!", 'info')
        else:
            new_order = Order(order_id=order_id, password=password, big_link=big_link, email=email, role='admin')
            db.session.add(new_order)
            db.session.commit()
            flash("Order saved successfully!", 'success')
    except Exception as e:
        logging.error(f"Error saving order: {e}")
        flash("Failed to save the order.", 'danger')
    return render_template('index.html')

@main_bp.route('/run_automation/<int:order_id>', methods=['GET'])
def run_automation(order_id):
    driver = browser_init()
    if not driver:
        flash("Failed to initialize the browser.", 'danger')
        return redirect('/')

    code, password = bot_automation(order_id, driver)
    if code:
        flash(f"5-digit code retrieved: {code}", 'success')
    else:
        flash("Automation failed.", 'danger')
    return redirect('/')

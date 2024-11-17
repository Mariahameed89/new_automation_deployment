import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_admin_email(order_id, access_code, email):
    sender_email = 'deliveryacc89@gmail.com'
    sender_password = 'wvhu wfqo xnol zsmv' 

    recipient_email = 'rajzadasamiii@gmail.com'  # Admin email
    subject = 'New Customer Request'
    message = f"""
    New customer request received:
    Order ID: {order_id}
    Access Code: {access_code}
    Customer Email: {email}
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_pin_email(customer_email, pin_code, password):
    sender_email = 'deliveryacc89@gmail.com'
    sender_password = 'wvhu wfqo xnol zsmv'
    
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Your 5-Digit PIN Code"
    body = f"""Hi Customer
    \n\nHere is your code: {pin_code}\n\n
    New eShop password: {password}
    
    How to download the game? 
    Go to the eShop
    Go to Avatar
    Go to Redownload, 
    Still not found it? Go to the email delivery mail, and select the FAQ List,
    Any further questions? Come to psnaccounts and click on (chat now). Dear customer, thank you!"""

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, customer_email, msg.as_string())
        print(f"Email sent to {customer_email} with PIN code: {pin_code}")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
    finally:
        server.quit()


def send_order_email(recipient_email, order_id):
    sender_email = 'deliveryacc89@gmail.com'
    sender_password = 'wvhu wfqo xnol zsmv'  # Use the app password here

    subject = 'Your Order Information'

    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Attach the text message
    message = f"""
Hi,

Your account is ready to use
your Oder_ ID: {order_id}

Activate your account as soon as possible!

LOOK IN THE ACTIVATION GUIDE, THERE IS A WEBSITE LINK AT THE BOTTOM, READ EVERYTHING CAREFULLY, FOR QUESTIONS GO TO PSNACCOUNTS AND CLICK ON CHAT NOW

You have 2 activation guides,

1: is with text only
2: is with pictures

Your choice which one you want to use.

Do you have any questions?
You can also look in the FAQ list, which is included in this email.

Have fun gaming
"""
    msg.attach(MIMEText(message, 'plain'))

    # Attach the PDF files
    # Attach the PDF files using relative paths
    pdf_file1 = r"./resources/Textexplainnintendo.pdf"
    pdf_file2 = r"./resources/Photoexplainnintend.pdf"
    faq_file = r"./resources/FAQListNintendoGameAccounts.pdf"


    with open(pdf_file1, 'rb') as f:
        attachment1 = MIMEApplication(f.read(), Name='activation_guide_text.pdf')
        attachment1['Content-Disposition'] = 'attachment; filename="activation_guide_text.pdf"'
        msg.attach(attachment1)

    with open(pdf_file2, 'rb') as f:
        attachment2 = MIMEApplication(f.read(), Name='activation_guide_pictures.pdf')
        attachment2['Content-Disposition'] = 'attachment; filename="activation_guide_pictures.pdf"'
        msg.attach(attachment2)

    with open(faq_file, 'rb') as f:
        attachment3 = MIMEApplication(f.read(), Name='faq.pdf')
        attachment3['Content-Disposition'] = 'attachment; filename="faq.pdf"'
        msg.attach(attachment3)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
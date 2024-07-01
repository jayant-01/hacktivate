import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email server configuration
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port
EMAIL_ADDRESS = 'ms.pankhania@gmail.com'
EMAIL_PASSWORD = 'sgrx ojtc sstz mxek' 

# Function to send email
def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_address
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# Function to read recipients from CSV and send emails
def send_emails_from_csv(file_path):
    recipients = pd.read_csv(file_path)
    
    for index, row in recipients.iterrows():
        to_address = row['email']
        first_name = row['first_name']
        last_name = row['last_name']
        
        subject = f"Hello {first_name}!"
        body = f"Dear {first_name} {last_name},\n\nThis is a personalized email and a part of bulk email sender.\n\nBest regards,\nYour Name"
        
        send_email(to_address, subject, body)
        print(f"Email sent to {to_address}")

# Main function
if __name__ == '__main__':
    csv_file_path = 'recipients.csv'
    send_emails_from_csv(csv_file_path)
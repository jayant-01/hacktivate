import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email server configuration
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port
EMAIL_ADDRESS = 'abc@gmail.com' #replace with your personal gmail
EMAIL_PASSWORD = '123456789'    #replace with password

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
        body = f"Dear {first_name} {last_name},\n\n Dear [Sender],
I hope this email finds you in good health and spirits. I hope that our phishing attempts have been somewhat less frustrating than they
might've otherwise been. Please allow me to introduce myself, my name is [Name] from [Company Name]. We understand how important your online
accounts are and we take the safety of our users seriously.Our recent detection suggests that someone attempted to access your gmail account. It appears that they used your username and password to
guess your email address. This could potentially pose a serious security risk, so please be cautious when responding to this phishing email.
To prevent further access, please reset your password using the following link: [Link]
Please ensure to change your password immediately once you've completed the process. Failure to do so may result in unauthorized access to
your account. Additionally, we have temporarily disabled your Gmail account to minimize any potential risks and prevent any further breaches.
If you have any further questions or concerns, please don't hesitate to contact our Customer Support team.
Once again, I apologize for this inconvenience and thank you for your cooperation in maintaining the integrity of our online platforms.,\nYour Name"
        
        send_email(to_address, subject, body)
        print(f"Email sent to {to_address}")

# Main function
if __name__ == '__main__':
    csv_file_path = 'recipients.csv'
    send_emails_from_csv(csv_file_path)
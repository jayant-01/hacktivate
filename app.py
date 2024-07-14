import requests
from bs4 import BeautifulSoup
import re
import os
import csv
from urllib.parse import urljoin
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import smtplib
import dns.resolver
from werkzeug.utils import secure_filename
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Initializi Flask application and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campaigns.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)
final_email_list = set()
emails=set()


# Define database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    is_alive = db.Column(db.Boolean, default=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return render_template('dashboard.html')
        else:
            flash('Invalid username or password')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()

    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            emails = parse_csv(filepath)
            for email in emails:
                new_campaign = Campaign(email=email, user_id=session['user_id'])
                db.session.add(new_campaign)
            db.session.commit()
            return render_template('dashboard.html', campaigns=campaigns)


    return render_template('dashboard.html', campaigns=campaigns,resources=final_email_list)

@app.route('/new_campaign', methods=['GET', 'POST'])
def new_campaign():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        domain = request.form['domain']
        if domain:
            existing_campaign = Campaign.query.filter_by(domain=domain).first()
            if existing_campaign:
                flash('Domain already exists in another campaign')
            else:
                campaign = Campaign(name="Campaign for " + domain, domain=domain)
                db.session.add(campaign)
                db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_campaign.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    campaign_id = request.form['campaign_id']
    if file and campaign_id:
        campaign = Campaign.query.get(campaign_id)
        if campaign:
            csv_reader = csv.reader(file, delimiter=',')
            for row in csv_reader:
                email = row[0]
                if not Email.query.filter_by(address=email, campaign_id=campaign_id).first():
                    new_email = Email(address=email, is_alive=validate_email(email), campaign_id=campaign_id)
                    print(new_email)
                    db.session.add(new_email)
            db.session.commit()
    return redirect(url_for('dashboard'))

def custom_scrape_emails_from_url(url):
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all email addresses using regex
        emails.update(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.text))
        # Find links to subdomains
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('/'):
                href = url + href
            if url in href:
                emails.update(custom_scrape_emails_from_url(href))  # Recursively scrape subdomains
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    # print(emails)
    return emails

@app.route('/scrape_emails', methods=['POST'])
def scrape_emails():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    domain = request.form['domain']
    campaign_id = request.form['campaign_id']
    
    if domain and campaign_id:
        base_url = f"https://{domain}"
        
        visited_urls = set()
        emails_found = set()
        max_pages_to_visit = 10
        def extract_emails_from_url(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            for string in soup.stripped_strings:
                matches = re.findall(email_pattern, string)
                if matches:
                    emails.update(matches)

            return emails

        def crawl_and_find_emails(url,page_visited=0):
            if url in visited_urls or page_visited>=max_pages_to_visit:
                return page_visited
            visited_urls.add(url)
            print(f"Visiting: {url}")

            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                new_emails = extract_emails_from_url(url)
                if new_emails:
                    print(f"Found {len(emails)} email(s) on {url}:")
                    
                    for email in new_emails:
                        print(email)
                        emails.add(email)
                        file_path="data.txt"
                        with open(file_path, mode='w') as file:
                            print(emails)
                            for email in emails:
                                final_email_list.add(email)
                                print(email)
                                file.write(email + "\n")

                    emails_found.update(emails)
                    

                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    if base_url in absolute_url and absolute_url not in visited_urls:
                        page_visited=crawl_and_find_emails(absolute_url,page_visited+1)
                        if page_visited>=max_pages_to_visit:
                            break


            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")

        crawl_and_find_emails(base_url)
        
        for email in emails_found:
            if not Email.query.filter_by(address=email, campaign_id=campaign_id).first():
                new_email = Email(address=email, is_alive=True, campaign_id=campaign_id)
                db.session.add(new_email)
        
        db.session.commit()
        flash(f"Found {len(emails_found)} emails.")
    return redirect(url_for('dashboard'))



def validate_email(email):
    # Step 1: Check email format
    if "@" not in email or "." not in email.split("@")[1]:
        return False
    
    # Step 2: Get domain for the email
    domain = email.split('@')[1]
    
    # Step 3: Get the MX record for the domain
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except Exception as e:
        print(f"Error resolving MX record for {domain}: {e}")
        return False
    
    # Step 4: Connect to the mail server
    try:
        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mx_record)
        server.helo(server.local_hostname)  # local hostname
        server.mail('verify@example.com')  # sender email
        code, message = server.rcpt(email)  # recipient email
        server.quit()
    except Exception as e:
        print(f"Error connecting to the mail server: {e}")
        return False
    
    # Step 5: Check the response code
    if code == 250:
        return True
    else:
        return False
        
def parse_csv(filepath):
    df=pd.read_csv("D:\hacktivate\hacktivate\recipients.csv")
    for index, row in df.iterrows():
        emails.append(row["Email"])


# Ensure the application context is available for certain operations
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

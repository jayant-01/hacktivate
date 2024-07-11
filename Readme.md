

# 🐟 Automated Phishing Campaigns Using AI

Welcome to the **Automated Phishing Campaigns Using AI** project! This repository contains tools and scripts to automate phishing campaigns leveraging AI.

## 📂 Project Structure

```
├── __pycache__/
├── instance/
├── templates/
├── app.py
├── getphishinggmail.py
├── phishdet.py
├── phishdetect.modelfile
├── phishgen.modelfile
├── recipients.csv
├── recipients.txt
├── scrapy.py
```

## 📑 Files Description

- **app.py**: Main application script to run the automation.
- **getphishinggmail.py**: Script to generate phishing emails using AI.
- **phishdet.py**: Phishing detection script.
- **phishdetect.modelfile**: Model file for phishing detection.
- **phishgen.modelfile**: Model file for phishing email generation.
- **recipients.csv**: CSV file containing recipients' email addresses.
- **recipients.txt**: Text file containing additional recipients' email addresses.
- **scrapy.py**: Script for web scraping to gather data for phishing.

## 🚀 Getting Started

### Prerequisites

- Python 3.6+
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/automated-phishing-campaigns.git
   cd automated-phishing-campaigns
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

### Usage

1. Prepare your recipients list in `recipients.csv` or `recipients.txt`.
2. Run the main application:
   ```sh
   python app.py
   ```
3. Use `getphishinggmail.py` to generate phishing emails:
   ```sh
   python getphishinggmail.py
   ```
4. Detect phishing emails with `phishdet.py`:
   ```sh
   python phishdet.py
   ```

## 🌟 Features

- **Automated Phishing Email Generation**: Leverage AI to create convincing phishing emails.
- **Phishing Detection**: Identify phishing emails using trained models.
- **Recipient Management**: Easily manage your target list with CSV and TXT files.
- **Web Scraping**: Gather data for creating realistic phishing scenarios.

## ⚠️ Disclaimer

This project is for educational and research purposes only. Misuse of this tool can lead to serious legal consequences. Use responsibly and only with explicit permission.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any queries or support, please contact [your-email@example.com](mailto:khansaad1275@gmail.com).

---

Thank you for checking out our project! We hope you find it useful for your research and educational purposes. 🚀

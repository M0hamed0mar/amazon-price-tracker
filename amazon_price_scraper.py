
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# URL of the product you want to track
url = "https://www.amazon.com/dp/B08J4JY78T"  # Replace with the product URL you want to track

# Set your threshold price for notifications
threshold_price = 50.00  # Set your threshold price

# Email settings for notification
sender_email = "youremail@example.com"
receiver_email = "recipient@example.com"
email_password = "yourpassword"  # Use app-specific password if using Gmail

def send_email(price):
    subject = "Price Drop Alert"
    body = f"The price of the product has dropped below your threshold! Current price: ${price}."
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, email_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print(f"Email sent: The price is now ${price}")

def scrape_amazon():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract product name
    try:
        product_name = soup.find('span', {'id': 'productTitle'}).text.strip()
    except AttributeError:
        product_name = "N/A"
    
    # Extract current price
    try:
        current_price = float(soup.find('span', {'id': 'priceblock_ourprice'}).text.replace('$', '').replace(',', '').strip())
    except AttributeError:
        current_price = None
    
    # Extract original price
    try:
        original_price = float(soup.find('span', {'class': 'priceBlockStrikePriceString'}).text.replace('$', '').replace(',', '').strip())
    except AttributeError:
        original_price = None
    
    # Extract product link (URL)
    product_link = url
    
    # Calculate discount percentage
    if original_price and current_price:
        discount_percentage = ((original_price - current_price) / original_price) * 100
    else:
        discount_percentage = None
    
    # Print and store the results
    print(f"Product Name: {product_name}")
    print(f"Current Price: ${current_price}")
    print(f"Original Price: ${original_price}")
    print(f"Discount Percentage: {discount_percentage}%")
    print(f"Product Link: {product_link}")
    
    # Save the data into a CSV file
    product_data = {
        "Product Name": product_name,
        "Current Price": current_price,
        "Original Price": original_price,
        "Discount Percentage": discount_percentage,
        "Product Link": product_link
    }

    df = pd.DataFrame([product_data])
    df.to_csv('amazon_product_prices.csv', mode='a', header=False, index=False)

    # Notify if price is below threshold
    if current_price and current_price < threshold_price:
        send_email(current_price)

# Run the scraper
scrape_amazon()

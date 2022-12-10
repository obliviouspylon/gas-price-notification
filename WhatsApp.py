
import os
import json
import requests

def sendGasMessage(recipient_phone_number, phone_number_id, access_token, date, Enpro_direction, Enpro_amount, Enpro_price, GasWizard_direction, GasWizard_amount, GasWizard_price):

    url = f"https://graph.facebook.com/v15.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        'Content-Type': 'application/json'
}

    msg_header_params = [
            {
                "type": "text",
                "text": date
            }
    ]

    msg_body_params = [
            {
                "type": "text",
                "text": Enpro_direction
            },
            {
                "type": "text",
                "text": Enpro_amount
            },
            {
                "type": "text",
                "text": Enpro_price
            },
            {
                "type": "text",
                "text": GasWizard_direction
            },
            {
                "type": "text",
                "text": GasWizard_amount
            },
            {
                "type": "text",
                "text": GasWizard_price
            }
    ]

    data = {
        'messaging_product': 'whatsapp',
        'to': recipient_phone_number,
        'type': 'template',
        'template': {
            'name': 'gas_price',
            'language': {
                'code': 'en'
            },
            'components': [
                {
                    'type': 'header',
                    'parameters': msg_header_params
                },
                {
                    'type': 'body',
                    'parameters': msg_body_params
                }
                    
            ]
        }
    }    
        
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data)
    )

    return(response.text)
    # if response.ok:
    #     return(response.text)
    # else:
    #     return(response.text)

if __name__ == "__main__":
    print(sendGasMessage("14165707278", "Dec 10", "Down", "3", "100", "Down", "3", "100"))
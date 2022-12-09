import pytextnow as pytn

def send_sms(number,message, tn_username, tn_sid, tn_csrf):
    client = pytn.Client(tn_username, sid_cookie=tn_sid, csrf_cookie=tn_csrf)
    # client.auth_reset()
    response = client.send_sms(number, message)
    # response = ""
    return response

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    tn_username = os.getenv('TEXTNOW_USERNAME')
    tn_sid = os.getenv('TEXTNOW_SID')
    tn_csrf = os.getenv('TEXTNOW_CSRF')
    send_sms("4165707278","HeyThere", tn_username, tn_sid, tn_csrf)
    print("SMS Sent")
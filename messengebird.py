import messagebird
from dotenv import dotenv_values

env_config = dotenv_values(".env")

ACCESS_KEY  = env_config["MESSAGEBIRD_ACCESS_KEY"]
client = messagebird.Client(ACCESS_KEY)
message = client.message_create(
        'TestMessage',
        'RECIPIENT',
        'This is a test message',
        { 'reference' : 'Foobar' }
    )
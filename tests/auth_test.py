import os
import dotenv
from bigchange._constants import DEFAULT_TIMEOUT, DEFAULT_BASE_URL, DEFAULT_API_VERSION
from bigchange._auth import TokenAuth


dotenv.load_dotenv()


token_auth = TokenAuth(client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"), token_url="https://api.bigchange.com/auth/tokens")
print(token_auth.get_token())
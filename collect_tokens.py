import requests
import re
# py -3.11 -m pip install requests
# py -3.11 collect_tokens.py
URL = "http://localhost:8080/forgot"
USERNAME = "test1"
NUM_TOKENS = 78

tokens = []

for i in range(NUM_TOKENS):
    # send POST request (simulate form submission)
    response = requests.post(URL, data={"user": USERNAME})

    html = response.text

    # extract token from reset URL
    match = re.search(r"token=([A-Za-z0-9+/=]+)", html)

    if match:
        token = match.group(1)
        print(f"[{i}] {token}")
        tokens.append(token)
    else:
        print(f"[{i}] token not found")

# write to file
with open("tokens.txt", "w") as f:
    for t in tokens:
        f.write(t + "\n")

print("Done. Tokens saved to tokens.txt")
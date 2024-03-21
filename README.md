# Activate virtual env
source venv/bin/activate
# export reqs
pip freeze > requirements.txt

# Manage https locally (for voice recording)
openssl genrsa -out localhost.key 2048
openssl req -new -x509 -key localhost.key -out localhost.crt -days 365 -subj /CN=localhost
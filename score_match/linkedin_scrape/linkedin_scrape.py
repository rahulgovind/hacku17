from linkedin import linkedin

client_id = '81l14xtfcbn78a'
client_secret = 'OXkB7bsgEDEg0baj'

#return_url = 'http://localhost:8000'
return_url = 'https://localhost'

authentication = linkedin.LinkedInAuthentication(client_id, client_secret, return_url, linkedin.PERMISSIONS.enums.values())

print authentication.authorization_url

application = linkedin.LinkedInApplication(authentication)

print authentication.get_access_token()

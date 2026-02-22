from email.utils import parseaddr

# Recherche du domaine
def extract_domain(from_value):
    
    email = parseaddr(from_value)[1]

    if not email:
        return None

    parts = email.split("@")
    if len(parts) != 2:
        return None

    domain = parts[1]

    return domain

# Extraire les liens http de désinscription
def extract_http_unsubscribe(unsubscribe_header):
    
    if not unsubscribe_header:
        return None

    links = unsubscribe_header.split(',')

    for i in range(len(links)):
        links[i] = links[i].strip().lstrip('<').rstrip('>')

        if links[i].startswith("http"):
            return links[i]

    return None



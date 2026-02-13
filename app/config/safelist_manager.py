import os.path
import json

def load_safelist():
    if os.path.exists("app/config/safelist.json"):
        with open("app/config/safelist.json", "r") as file:
            data = json.load(file)
            
    else:
        with open("app/config/safelist.json", "x") as file:
            json.dump([], file, indent=4)
        with open("app/config/safelist.json", "r") as file:
            data = json.load(file)

    return data

def save_safelist(safelist):
    if os.path.exists("app/config/safelist.json"):
        with open("app/config/safelist.json", "w") as file:
            json.dump(safelist, file, indent=4)
    else:
        print("Fichier introuvable")

    
def add_domain_to_safelist(domain):
    safelist = load_safelist()
    print(domain)
    domain = domain.lower().strip()

    if domain not in safelist:
        safelist.append(domain)
        save_safelist(safelist)
        print("Domaine ajouté à la liste.")
        return True
    else:
        print("Domaine déjà dans la liste.")
        return False
    
def filter_safelist(senders, safelist):
    filtered_senders = {}

    for sender in senders:
        if sender not in safelist:
            filtered_senders[sender] = senders[sender]
            
    return filtered_senders

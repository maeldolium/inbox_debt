def display_domains(senders):
    print("Domaines détectés :\n")

    for id, data in senders.items():
        print(f'{id}. {data["domain"]} ({data["count"]} mails)\n')

def select_domain(senders):
    try:
        print("Choisissez un domaine :")
        domain_id = int(input("> "))
        print("\n")
        # Si valide retourne domaine et count
        if domain_id in senders:
            domain = senders[domain_id]['domain']
            count = senders[domain_id]['count']
            subjets = senders[domain_id]['subjects']

            return domain, count, subjets
        elif domain_id == 0:
            exit()
        else:
            print("Choix invalide.")
    except ValueError:
        print("Entrez un numéro !")

def display_actions(sender, count):
    print(f"Que voulez vous faire pour {sender}?\n")
    
    print(f'1. Supprimer ({count} mails)\n')
    print("2. Ajouter à la safelist\n")
    print("3. Retour\n")

def select_action():
    user_choice = int(input("> "))
    return user_choice

def confirm_deletion(domain, count, subjects):
    print(f"Domaine : {domain}")
    print(f"Nombre de mails : {count}\n")
    
    print("Exemples de sujets :")
    for subject in subjects[:3]:
        print(f'- {subject}')
    print('\n')

    print(f"Confirmez la suppression ? (y/n)")

    user_choice = str(input("> "))

    match(user_choice):
        case 'y':
            return True
        case 'n':
            return False
        case _:
            print("Choix invalide")
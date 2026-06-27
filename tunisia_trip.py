import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Utilisez le bon chemin vers votre fichier JSON
creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\Bsi\Desktop\renové\null\null\GTA_San_Andreas\HD مود جرافيك\1 - High\my-python-projects\creds.json", scope)client = gspread.authorize(creds)

# Ouvrir le fichier d'ici
sheet = client.open("nom_de_votre_sheet").sheet1

# Ajouter une ligne de test
sheet.append_row(["Test Nom", "0123456789", "test@email.com"])
print("Succès !")
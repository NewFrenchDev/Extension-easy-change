import os
from glob import glob
import json
from time import sleep
import pathlib
import platform
import shutil
import logging

OS = platform.system()
FORMAT = "%(asctime)s -- %(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT, level="INFO")

class ExtensionChangerV2():
    def __init__(self):
        self.use_config = "No"
        self.working_folder = ""
        self.saving_folder = ""
        self.directory_list =[]
        self.folder_to_copy = None
        self.folder_to_create = None
        self.source = None
        self.destination = None

    ### --> Quit programm
    def exit(self):
        logging.info(msg="Arrêt du script")
        sleep(10)
        exit()

    ### --> Read config.json file
    def get_configuration(self):

        logging.info(msg="Chargement du fichier de config.json...\n")

        with open("./config.json", "r", encoding="utf-8") as f:
            configuration = json.load(f)

        self.use_config = configuration.get("use_config")

        if self.use_config == "Yes":
            logging.info(msg="us_config=Yes --> les chemins indiqués dans config.json vont être utilisés")

            self.working_folder = pathlib.Path(configuration.get("working_folder"))
            self.saving_folder = pathlib.Path(configuration.get("saving_folder"))

            print(self.working_folder)

            if not os.path.exists(self.working_folder):
                logging.error(msg=f"Le chemin '{self.working_folder}' n'existe pas!")
                self.exit()
            elif not os.path.exists(self.saving_folder):
                logging.error(msg=f"Le chemin '{self.saving_folder}' n'existe pas!")
                self.exit()

        else:
            self.working_folder = os.path.dirname(__file__)
            self.saving_folder = f"{self.working_folder}\\saving"
            os.makedirs(self.saving_folder, exist_ok=True)

        self.extensions = configuration.get("extensions")

        logging.info(msg="Chargement terminé!")

    ### --> Check configuration
    def check_configuration(self):

        logging.info(msg="Verification des chemins...")
        if self.working_folder == "":
            logging.error(msg="Aucun chemin n'est indiqué pour le dossier de travail!")
            self.exit()
        else:
            if os.path.exists(self.working_folder):
                logging.info(msg="Le dossier de travail a été vérifié")
            else:
                logging.error(msg="Le dossier de travail indiqué dans config.json n'existe pas")
                self.exit()

        if self.saving_folder == "":
            logging.error(msg="Aucun chemin n'est indiqué pour le dossier de sauvegarde")
            self.exit()
        else:
            if os.path.exists(self.saving_folder):
                logging.info(msg="Le dossier de sauvegarde a été vérifié")
            else:
                logging.error(msg="Le dossier de sauvegarde indiqué dans config.json n'existe pas")
                self.exit()
        logging.info(msg="Les chemins sont accessibles!")

    ### CHECK DIRECTORY COMPOSITION

    def check_working_folder(self):

        if self.use_config == "Yes":
            directory_composition = glob(f"{self.working_folder}/**/", recursive=True)
        else:
            if os.path.isdir(f"{self.working_folder}\\work"):
                directory_composition = glob(f"{self.working_folder}\\work/**/", recursive=True)
            else:
                logging.error("""Le script n'est pas placé dans le bon dossier de travail!
                Le script doit être placé au même niveau que le dossier work de ton projet! :)""")

        if directory_composition != []:
            #remove first folder == working folder
            path_working_folder = directory_composition.pop(0)
            path_working_folder_lenght = len(path_working_folder.split("\\"))
            
            print(f"\n\nDossiers trouvés dans le dossier de travail:")
            for folder in directory_composition:
                folder_path_lenght = len(folder.split("\\"))
                foldername = folder.split("\\")[-2]

                if folder_path_lenght == path_working_folder_lenght + 1:
                    self.directory_list.append(foldername)
                    #folder_parent = folder.split("\\")[-3]
                    #print(f"Le dossier {foldername} est le sous dossier direct de {folder_parent}")
                    print(f"- Dossier: {foldername}")
                elif folder_path_lenght == path_working_folder_lenght + 2:
                    #folder_parent = "\\".join(folder.split("\\")[-4:-2])
                    #print(f"Le dossier {foldername} est le sous dossier direct de {folder_parent}")
                    print(f"--- Sous-dossier: {foldername}")

    ### PRINT DIRECTORY ONLY
    def print_directory(self):
        print(f"\n\nTu peux choisir de copier l'entièreté d'un de ces dossiers: {self.directory_list}")  

    ### CHOOSE FOLDER TO COPY
    def copy_folder(self):
        self.folder_to_copy = input("Entre le nom de dossier à copier: ")
        if self.folder_to_copy not in self.directory_list:
            logging.error("Le nom indiqué n'est pas présent dans la liste suggérée...")
            self.copy_folder()
            return True

        self.folder_to_create = input("Donner la nouvelle extension voulue: ")

        if self.use_config == "No":
            self.source = f"{self.working_folder}\\work\\{self.folder_to_copy}" 
            self.destination = f"{self.saving_folder}\\{self.folder_to_create}"
        elif self.use_config == "Yes":
            self.source = f"{self.working_folder}\\{self.folder_to_copy}" 
            self.destination = f"{self.saving_folder}\\{self.folder_to_create}"
        else:
            logging.error(msg="use_config ne peut valoir que Yes ou No! Corrige la valeur dans le fichier config.json")
            self.exit()

        if os.path.exists(self.destination):
            shutil.rmtree(self.destination)

        logging.info(msg="Copie lancée...")
        shutil.copytree(self.source, self.destination)
        logging.info(msg="Copie terminée!")

    ### CHANGE EXTENSION FOR SAVING FOLDER
    def change_extension(self):

        files_to_modify = glob(f"{self.destination}/**/*.{self.folder_to_copy}", recursive=True)

        for file in files_to_modify:
            os.rename(file, file.replace(f"{self.folder_to_copy}", f"{self.folder_to_create}"))
        logging.info(msg="Les fichiers ont été renommés avec succès")

        self.exit()

    ### EXECUTION
    
    def execute(self):

        self.get_configuration()
        self.check_configuration()
        self.check_working_folder()
        self.print_directory()
        self.copy_folder()
        self.change_extension()
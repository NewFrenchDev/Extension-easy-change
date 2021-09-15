import os
from glob import glob
import pathlib
import shutil
import logging


class ExtensionChanger:
    def __init__(self):
        self.extension = None
        self.new_extension = None
        self.extension_list = None
        self.working_directory = None
        self.folders_path = None
        self.files_path = []
        self.list_file_with_extension = []
        self.option = ""

    def folder_analysis(self):
        self.working_directory = pathlib.Path(os.getcwd())

    def select_option(self):
        self.option = input("""
        1. Les fichiers a convertir sont à la racine du dossier mqxliff
        2. Les fichiers à convertir sont répartis dans plusieurs sous dossiers dans le dossier mqxliff

        Fait ton choix :)
        """)

        if self.option not in ["1", "2"]:
            print("Tu ne peux qu'indiquer 1 ou 2\n\n")
            self.select_option

    def check_files_extensions(self):
        # For the test
        folder_to_ignore = ["\\env\\", "\\__pycache__\\"]
        ###############

        if self.option == "1":
            self.folders_path = glob(f"{self.working_directory}/*/*/")
        elif self.option == "2":
            self.folders_path = glob(f"{self.working_directory}/*/*/*")

        for folder in self.folders_path:
            for forbidden_name in folder_to_ignore:
                if folder.endswith(forbidden_name):
                    self.folders_path.remove(folder)

        for folder in self.folders_path:
            temp = glob(f"{folder}\\*.*")
            self.files_path += temp
            del temp

    def delete_duplicate(self, list_with_duplicate):
        self.extension_list = list(set(list_with_duplicate))
        if "py" in self.extension_list:
            self.extension_list.remove("py")

    def show_extension_list_from_working_directory(self):
        extensions = []
        for file_path in self.files_path:
            string_path = str(file_path)
            extensions.append(string_path.split(".")[-1])
        self.delete_duplicate(extensions)
        print(f"Extension présent dans les dossier(s):\n {self.extension_list}")

    def move_files(self, file, filename, path):
        folder_where_to_move = f"{path}\\{self.new_extension}\\{filename}"
        shutil.move(file, folder_where_to_move)

    def copy_and_rename_files(self, original_file):
        if original_file is not str:
            original_file = str(original_file)

        path, _ = original_file.split(".")
        new_file = path + "." + self.new_extension
        filename = new_file.split("\\")[-1]
        path_to_use = '\\'.join(new_file.split("\\")[:-1])

        shutil.copy(original_file, new_file)
        return new_file, filename, path_to_use

    def choose_extension_to_change(self):
        self.extension = input("L'extension à modifier: ").lower()

        if self.extension not in self.extension_list:
            logging.warning("\nAucun fichier n'a cette extension!")
            self.choose_extension_to_change()
        elif self.extension == "py":
            logging.warning("Cette extension est interdite!")
            self.choose_extension_to_change()

    def get_all_files_with_extension_to_modify(self):
        for folder in self.folders_path:
            temp = glob(f"{folder}/*.{self.extension}")
            self.list_file_with_extension += temp

    def rename_move_files(self):
        self.new_extension = input("La nouvelle extension: ").lower()

        for file in self.list_file_with_extension:
            file = str(file)
            new_file, filename, path = self.copy_and_rename_files(file)
            self.create_folder_extension(path)
            self.move_files(new_file, filename, path)

    def create_folder_extension(self, folder):
        os.makedirs(f"{folder}\\{self.new_extension}", exist_ok=True)

    def execute(self):

        # Analyze folders
        self.folder_analysis()
        self.select_option()
        self.check_files_extensions()
        self.show_extension_list_from_working_directory()

        # Modify extension
        self.choose_extension_to_change()
        self.get_all_files_with_extension_to_modify()
        self.rename_move_files()

import os
from dearpygui import dearpygui as dpg
from project.Settings import Settings
from project.objects.songs.Song import Song
from project.objects.folders.Folder import Folder
from project.objects.folders.Folder_from_db import Folder_from_db
from project.objects.folders.Folder_from_os import Folder_from_os
import project.Db_handler as dbh

# Initialize settings and database handler
settings = Settings()
db_handler = dbh.Db_handler()

# ----------------------------------------------------------------
# missing_folder corresponding to a folder present in the database but not in the disk
# unexpected_folder corresponding to a folder present in the disk but not in the database
# missing_song corresponding to a song present in the database but not in the disk
# unexpected_song corresponding to a song present in the disk but not in the database
missing_folder, unexpected_folder, missing_song, unexpected_song = [], [], [], []
selected_tag = None

def compare_folders(folder_from_db, folder_from_os):
    # Dictionaries to store songs present in both, only in database, and only on disk
    songs_in_both = {}
    songs_only_in_db = {}
    songs_only_in_disk = {}

    def process_element(element, origin):
        nonlocal songs_in_both, songs_only_in_db, songs_only_in_disk

        if isinstance(element, Song):
            if origin == "db":
                songs_only_in_db[element.name] = element
            elif origin == "os":
                if element.name in songs_only_in_db:
                    element.id = songs_only_in_db[element.name].id
                    del songs_only_in_db[element.name]
                    songs_in_both[element.name] = element
                else:
                    songs_only_in_disk[element.name] = element
        elif isinstance(element, Folder):
            for sub_element in element.elements:
                process_element(sub_element, origin=origin)

    # For each element in the folder from the database
    for element in folder_from_db.elements:
        process_element(element, origin="db")

    # For each element in the folder from the disk
    for element in folder_from_os.elements:
        process_element(element, origin="os")

    return songs_in_both, songs_only_in_db, songs_only_in_disk

def compare_disk_db(s, a, u):
    base_folder = db_handler.exe_one("SELECT path,name,id FROM Folder WHERE id = 1")[0]
    path = settings.get(0)
    folder_from_db = Folder_from_db(path=base_folder[0], name=base_folder[1]).load_from_db()
    folder_from_os = Folder_from_os(path=path, name="MUSIC").load_from_os()

    in_both, only_db, only_disk = compare_folders(folder_from_db, folder_from_os)
    moved_song = {}

    dpg.delete_item("comparison_results", children_only=True)

    if len(in_both) > 0:
        dpg.add_text(f"Il y a {len(in_both)} musiques synchronisées.", parent="comparison_results")

    if len(only_db) > 0 or len(only_disk) > 0:
        with dpg.table(header_row=False, row_background=True,
                       delay_search=True, parent="comparison_results") as table_anomaly:

            dpg.add_table_column(label="Song")
            dpg.add_table_column(label="Localisation")
            dpg.add_table_column(label="Anomaly from")
            dpg.add_table_column(label="Solution")

            def add_to_table():
                with dpg.table_row():
                    pass

            # Regarde si les son présent seulement sur la db n'ont pas étés déplacés sur le disque, causant l'absence
            # Si c'est le cas, les range dans moved_song et les supprime des only_db et only_disk
            if len(only_db) > 0 and len(only_disk) > 0:
                for song in only_db:
                    if song in only_disk:
                        moved_song[song] = [only_db[song], only_disk[song]]
                        del only_disk[song], only_db[song]

    #     dpg.add_spacer(height=5, parent="comparison_results")
    #     dpg.add_text(f"Il y a {len(only_db)} musiques seulement sur la db.", parent="comparison_results")
    #     if len(only_disk) > 0:
    #         for song in only_db:
    #             if song in only_disk:
    #                 moved_song[song] = [only_db[song], only_disk[song]]
    #                 del only_disk[song], only_db[song]
    #     print(moved_song)
    #
    #     if len(moved_song) > 0:
    #         dpg.add_text(f".{len(moved_song)} titre correspondant avec une musique sur le disque.", parent="comparison_results")
    #         dpg.add_button(f"Mettre à jour la DB selon les nouvelles localisation sur le disque", parent="comparison_results")
    #     if len(only_db) > 0 :
    #         dpg.add_text(f".{len(only_db)} introuvables sur le disque dur (supprimée ?)", parent="comparison_results")
    #
    # if len(only_disk) > 0:
    #     dpg.add_spacer(height=5, parent="comparison_results")
    #     dpg.add_text(f"Il y a {len(only_disk)} musiques seulement sur le disque.", parent="comparison_results")


def create_tag():
    dpg.configure_item("error_text", default_value="")

    name = dpg.get_value("new_tag_name").replace("'", "''") if dpg.get_value("new_tag_name") else ""
    desc = dpg.get_value("new_tag_desc").replace("'", "''") if dpg.get_value("new_tag_desc") else ""

    parent_tags = [dpg.get_item_user_data(tag)[0] for tag in dpg.get_item_children("add_parent")[1]
                       if dpg.get_value(tag)]

    if name == '':
        dpg.configure_item("error_text", default_value="Name missing")
        return
    if any(name in tag_name for tag_name in db_handler.exe("SELECT name FROM tag")):
        dpg.configure_item("error_text", default_value="Name already existing")
        return

    if desc == "":
        db_handler.push_tag(req="INSERT INTO tag (name) VALUES ('" + name + "')", name=name, parent_tags=parent_tags)
    else:
        db_handler.push_tag(req="INSERT INTO tag (name, desc) VALUES ('" + name + "', '" + desc + "')", name=name, parent_tags=parent_tags)

    dpg.configure_item("__create_tag_popup", show=False)

    increment_create_tag_tag_list()
    increment_tag_list()


def tag_selected(s, a, u):
    global selected_tag

    if u == selected_tag:
        dpg.set_value("selected_tag_name", value="Tag selected :")
        dpg.configure_item("delete_tag", enabled=False)
        selected_tag = None
    else:
        if selected_tag is not None:
            dpg.set_value(f"checkbox_tag_{selected_tag[0]}", value=False)

        dpg.configure_item("delete_tag", enabled=True)
        dpg.set_value("selected_tag_name", value=f"Tag selected :{u[1]}")
        selected_tag = u

def increment_tag_list():
    dpg.delete_item("man_tag_list", children_only=True)
    tag_list = db_handler.exe("SELECT * FROM tag")
    for tag in tag_list:
        dpg.add_checkbox(tag=f"checkbox_tag_{tag[0]}", label=f"{tag[1]}", callback=tag_selected, user_data=tag, parent="man_tag_list")

def increment_create_tag_tag_list ():
    tag_list = db_handler.exe("SELECT * FROM tag")
    dpg.delete_item("add_parent", children_only=True)
    for tag in tag_list:
        dpg.add_checkbox(label=f"{tag[1]}", user_data=tag, parent="add_parent")

def delete_tag(s,a,u):
    global selected_tag
    db_handler.exe_commit(req=f"DELETE FROM tag WHERE id = {selected_tag[0]}")
    selected_tag = None

    increment_tag_list()
    increment_create_tag_tag_list()

def create_tab():
    global selected_tag
    with dpg.tab(label="Management", tag="management_tab"):
        with dpg.collapsing_header(label="TAG"):
            with dpg.group(horizontal=True):
                with dpg.group(tag="man_tag_list"):
                    increment_tag_list()

                with dpg.group(indent=350):
                    dpg.add_button(label="Add_tag")
                    with dpg.popup(dpg.last_item(), modal=True, mousebutton=dpg.mvMouseButton_Left, tag="__create_tag_popup"):
                        dpg.add_input_text(tag="new_tag_name", hint="enter tag name")
                        dpg.add_input_text(tag="new_tag_desc", hint="enter tag description")
                        dpg.add_separator()

                        with dpg.collapsing_header(label="Add parent tag", tag="add_parent"):
                            increment_create_tag_tag_list()

                        with dpg.group(horizontal=True):
                            dpg.add_button(label="OK", width=75, callback=create_tag)
                            dpg.add_button(label="Cancel", width=75, callback=lambda: dpg.configure_item("__create_tag_popup", show=False))

                        dpg.add_text("", tag="error_text")

                    dpg.add_spacer(height=5)
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_text(f"Tag selected :", tag="selected_tag_name")
                    dpg.add_spacer(height=5)
                    dpg.add_button(tag="delete_tag", label="Delete tag", enabled=False, callback=delete_tag)

        with dpg.collapsing_header(label="SCANNER"):
            with dpg.group(horizontal=False):
                dpg.add_button(label="Comparison between disk and DB", callback=compare_disk_db)
                with dpg.group(horizontal=False, tag="comparison_results"):
                    pass


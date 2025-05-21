import json

import dearpygui.dearpygui as dpg
import ntpath
from threading import Thread, Event
import pygame
import time
import random
import atexit

from mutagen.mp3 import MP3

from project.Settings import Settings
settings = Settings()

import project.Db_handler as dbh
db_handler = dbh.Db_handler()

import project.theme.Theme as theme
import project.pages.Tab_management as tab_management
# import project.pages.Tab_GDrive as tab_gdrive

#TODO REGARDE LE MODULE pillow -> permet de récupérer les exif data (images dans les .mp3)

dpg.create_context()
dpg.create_viewport(title="Rainy Music", large_icon="icon.ico", small_icon="icon.ico")
pygame.mixer.init()
pygame.init()

# A String describing witch stats we currently are
global state
state: None = None

# The current list of song showed
global act_song_list
act_song_list = []

# The current song played
global act_song
act_song = None

# Thread with while loop every second during the song
global playing_thread
playing_thread = None

# Event that stop playing_thread
global playing_event
playing_event = Event()

_DEFAULT_MUSIC_VOLUME = 0.5
pygame.mixer.music.set_volume(0.5)

END_EVENT = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(END_EVENT)


def update_volume(sender, app_data):
    pygame.mixer.music.set_volume(app_data / 100.0)


def update_slider(current_time=0):
    global state
    global act_song
    global playing_event

    playing_event.clear()

    song_length = round(MP3(act_song[2]).info.length)
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

    song_id = act_song[0]

    current_time = round(current_time)
    print(current_time)

    while pygame.mixer.music.get_busy() and not playing_event.is_set() and song_id is act_song[0]:
        converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

        print(f"{converted_current_time} of {converted_song_length}")
        dpg.configure_item("song_timer", default_value=f"{converted_current_time} of {converted_song_length}")
        dpg.configure_item("song_pos_slider", default_value=current_time)

        current_time += 1
        time.sleep(1)


def play(sender, app_data, user_data):
    global state
    global act_song
    global playing_thread
    if user_data[2]:
        song_path = settings.get(0) + user_data[2]
        pygame.mixer.music.load(user_data[2])
        pygame.mixer.music.play()
        song_length = round(MP3(user_data[2]).info.length)
        converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))
        if pygame.mixer.music.get_busy():
            state = "playing"
            act_song = user_data
            dpg.configure_item(item="song_pos_slider", max_value=song_length)
            playing_thread = Thread(target=update_slider, daemon=False).start()
            dpg.configure_item("play", label="Pause")
            dpg.configure_item("sfolder", default_value=f"Folder : {user_data[4]}")
            dpg.configure_item("cstate", default_value=f"State: Playing")
            dpg.configure_item("csong", default_value=f"Now Playing : {ntpath.basename(user_data[2])}")
            dpg.configure_item("song_timer", default_value=f"0:0 of {converted_song_length}")


def go_on_timing(sender):
    global state
    global act_song
    global playing_thread
    global playing_event
    clicked_timing = dpg.get_value(sender)
    if state == "playing" or state == "paused":

        playing_event.set()
        time.sleep(1)

        pygame.mixer.music.play(0, clicked_timing)
        playing_thread = Thread(target=update_slider(current_time=clicked_timing), daemon=False).start()


def play_pause():
    global state
    global act_song_list
    global playing_thread
    if state == "playing":
        state = "paused"
        pygame.mixer.music.pause()
        dpg.configure_item("play", label="Play")
        dpg.configure_item("cstate", default_value=f"State: Paused")
    elif state == "paused":
        state = "playing"
        pygame.mixer.music.unpause()
        playing_thread = Thread(target=update_slider(pygame.mixer.music.get_pos()), daemon=False).start()
        dpg.configure_item("play", label="Pause")
        dpg.configure_item("cstate", default_value=f"State: Playing")
    else:
        song = random.choice(act_song_list)
        play(sender=None, app_data=None, user_data=song)


def stop():
    global state
    pygame.mixer.music.stop()
    dpg.configure_item("csong", default_value=f"Now Playing : ")
    dpg.configure_item("cstate", default_value=f"State: None")
    dpg.configure_item("play", label="Random")
    dpg.configure_item("song_timer", default_value="00:00 of 00:00")
    state = None



def filter_search(sender, app_data, user_data):
    folders = db_handler.exe("SELECT * FROM folder WHERE name LIKE '%" + app_data + "%' AND id IN (SELECT parent_id FROM song) ORDER BY parent_id")
    dpg.delete_item("folder_list", children_only=True)
    for folder in folders:
        dpg.add_checkbox(label=f"{folder[1]}", callback=increment_song_from_filter, user_data=folder, parent="folder_list")

    tags = db_handler.exe("SELECT * FROM tag WHERE name LIKE '%" + app_data + "%' ORDER BY name")
    dpg.delete_item("tag_list", children_only=True)
    for tag in tags:
        dpg.add_checkbox(label=f"{tag[1]}", callback=increment_song_from_filter, user_data=tag, parent="tag_list")


def removeall():
    dpg.delete_item("list", children_only=True)


def increment_song_list(s=None, a=None, u=None, data=None):
    global act_song_list

    if data is None: data = db_handler.get_all_song()

    dpg.delete_item("list", children_only=True)
    act_song_list = []

    with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, hideable=True, no_host_extendX=True,
                   borders_outerH=True, borders_innerV=False, borders_innerH=False, borders_outerV=True, row_background=True,
                   reorderable=True, tag=_filter_table_id, parent="list") as song_table:

        dpg.add_table_column(label="", width_fixed=True)
        dpg.add_table_column(label="Play", width_fixed=True)
        dpg.add_table_column(label="ID", width_fixed=True)
        dpg.add_table_column(label="Song name", width_stretch=True)
        dpg.add_table_column(label="Folder", width_fixed=True, init_width_or_weight=200)
        # dpg.add_table_column(label="Tags", width_fixed=True)

        i = 0
        for song in data:
            act_song_list.append(song)
            with dpg.table_row(tag=f"row_{song[0]}", filter_key=f"{song[0]}{song[1]}"):
                dpg.add_checkbox(tag=f"checkbox_{song[0]}")
                dpg.add_button(label="Play", width=50, callback=play, height=24, user_data=song)
                dpg.add_text(f"{song[0]}")
                x = dpg.add_text(f"{song[1]}")
                dpg.add_text(f"{song[4]}")

                # if song[5] is not None:
                #     tag_name_list = []
                #     for tag in json.loads(song[5]): tag_name_list.append(tag["name"])
                #     dpg.add_combo(tag_name_list)
                #     dpg.highlight_table_cell(song_table, i, 5, [0, 170, 255, 150])

                i += 1

    if len(dpg.get_value("song_search")) > 0:
        update_search()


def reset_filter(sender):
    for folder in dpg.get_item_children("folder_list")[1]:
        dpg.set_value(folder, False)

    for tag in dpg.get_item_children("tag_list")[1]:
        dpg.set_value(tag, False)

    increment_song_list()

def update_search(s = None, a = None, u = None):
    dpg.set_value(_filter_table_id, dpg.get_value("song_search"))


def get_item_list(item_type):
    item_list = ""
    for item in dpg.get_item_children(item_type)[1]:
        if dpg.get_value(item):
            if len(item_list) == 0:
                item_list = "(" + str(dpg.get_item_user_data(item)[0]) + ","
            else:
                item_list += str(dpg.get_item_user_data(item)[0]) + ","
    if len(item_list) > 0:
        item_list = item_list[:-1] + ")"
    return item_list

def increment_song_from_filter(sender, app_data, user_data):
    folder_list = get_item_list("folder_list")
    tag_list = get_item_list("tag_list")

    if not folder_list and not tag_list:
        increment_song_list()
    elif not folder_list:
        increment_song_list(data=db_handler.get_song_where_tag(tag_list=tag_list))
    elif not tag_list:
        increment_song_list(data=db_handler.get_song_where_folder(folder_list=folder_list))
    else:
        increment_song_list(data=db_handler.get_song_where_tag_folder(tag_list=tag_list, folder_list=folder_list))

def increment_filter():
    dpg.delete_item("filters", children_only=True)

    with dpg.collapsing_header(label="Folder list", tag="folder_list", parent="filters"):
        for folder in db_handler.exe(
                "SELECT * FROM folder WHERE id IN (SELECT parent_id FROM song) ORDER BY parent_id"):
            dpg.add_checkbox(label=f"{folder[2]}", callback=increment_song_from_filter, user_data=folder,
                             parent="folder_list")
    with dpg.collapsing_header(label="Tag list", tag="tag_list", parent="filters"):
        for tag in db_handler.exe("SELECT * FROM tag"):
            dpg.add_checkbox(label=f"{tag[1]}", callback=increment_song_from_filter, user_data=tag, parent="tag_list")


def checkall(s,a,u):
    global act_song_list
    for song in act_song_list:
        dpg.configure_item(f"checkbox_{song[0]}", default_value=True if a is True else False)


theme.create_theme()

with dpg.font_registry():
    monalisa = dpg.add_font("project/theme/fonts/MonoLisa-Bold.ttf", 12)

with dpg.window(tag="main", label="window title"):
    with dpg.group(horizontal=True):
        with dpg.child_window(width=250, tag="left_sidebar"):
            dpg.add_spacer(height=5)
            dpg.add_text(f"State: {state}", tag="cstate")
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            dpg.add_button(label="Remove All Songs", width=-1, height=28, callback=removeall)
            dpg.add_button(label="Reload All Songs", width=-1, height=28, callback=reset_filter)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.child_window():
                with dpg.group(horizontal=True, tag="filter_query"):
                    dpg.add_input_text(hint="Search for a folder or a tag", width=-1, callback=filter_search)
                dpg.add_spacer(height=3)
                dpg.add_button(label="Reset filters", callback=reset_filter)
                dpg.add_spacer(height=5)
                dpg.add_button(label="reload filters", callback=increment_filter)
                dpg.add_spacer(height=5)
                dpg.add_separator()
                dpg.add_spacer(height=5)
                with dpg.child_window(tag="filters"):
                    increment_filter()

        with dpg.child_window(width=-250, border=True, tag="center"):

            with dpg.group(tag="center_header"):
                with dpg.child_window(autosize_x=True, height=60, no_scrollbar=True, width=20):
                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            with dpg.group(horizontal=True):
                                dpg.add_button(label="Random", width=65, height=30, tag="play", callback=play_pause)
                                dpg.add_button(label="Stop", callback=stop, width=65, height=30)
                            dpg.add_spacer()
                            dpg.add_slider_float(tag="volume", width=140, height=10, format="%.0f%.0%",
                                             default_value=_DEFAULT_MUSIC_VOLUME * 100, callback=update_volume)
                        with dpg.group(horizontal=False):
                            dpg.add_slider_int(tag="song_pos_slider", width=-1, callback=go_on_timing)
                            dpg.add_text("00:00 of 00:00", tag="song_timer")

                dpg.add_separator()
                dpg.add_spacer(height=3)

                with dpg.group(horizontal=False):
                    dpg.add_text(f"Now Playing : ", tag="csong")
                    dpg.add_text(f"Folder : ", tag="sfolder")
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"Tags : ", tag="stag")

            dpg.add_spacer(height=1)
            dpg.add_separator()
            dpg.add_spacer(height=1)

            with dpg.child_window(autosize_x=True, delay_search=True, tag="center_main"):
                with dpg.tab_bar():
                    with dpg.tab(label="Songs", tag="song_list_tab"):
                        with dpg.group(horizontal=True):
                            dpg.add_checkbox(label="", callback=checkall)
                            _filter_table_id = dpg.generate_uuid()
                            dpg.add_input_text(hint="Search for a song", width=-1, user_data=_filter_table_id,
                                               callback=update_search, tag="song_search")

                        with dpg.child_window(autosize_x=True, delay_search=True, tag="list"):
                            increment_song_list()
                    tab_management.create_tab()
                    # tab_gdrive.create_tab()

        with dpg.child_window(border=True, tag="right_sidebar"):
            dpg.add_button(label="OUI", width=-1)

    dpg.bind_item_theme("volume", "slider_thin")
    dpg.bind_item_theme("song_pos_slider", "slider")
    dpg.bind_item_theme("list", "songs")
    dpg.bind_item_theme("folder_list", "folder_list_button")

dpg.bind_theme("base")
dpg.bind_font(monalisa)


def safe_exit():
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.quit()


atexit.register(safe_exit)

# dpg.show_style_editor()
# dpg.show_documentation()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

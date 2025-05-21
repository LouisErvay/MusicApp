import dearpygui.dearpygui as dpg

class Filters:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def create(self):
        dpg.add_spacer(height=5)
        dpg.add_text("State: None", tag="cstate")
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        dpg.add_button(label="Remove All Songs", width=-1, height=28, callback=self.removeall)
        dpg.add_button(label="Reload All Songs", width=-1, height=28, callback=self.reset_filter)
        dpg.add_spacer(height=5)
        dpg.add_separator()
        dpg.add_spacer(height=5)
        with dpg.child_window():
            with dpg.group(horizontal=True, tag="filter_query"):
                dpg.add_input_text(hint="Search for a folder or a tag", width=-1, callback=self.filter_search)
            dpg.add_spacer(height=3)
            dpg.add_button(label="Reset filters", callback=self.reset_filter)
            dpg.add_spacer(height=5)
            dpg.add_button(label="reload filters", callback=self.increment_filter)
            dpg.add_spacer(height=5)
            dpg.add_separator()
            dpg.add_spacer(height=5)
            with dpg.child_window(tag="filters"):
                self.increment_filter()

    def get_item_list(self, item_type):
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

    def increment_song_from_filter(self, sender, app_data, user_data):
        folder_list = self.get_item_list("folder_list")
        tag_list = self.get_item_list("tag_list")

        if not folder_list and not tag_list:
            self.increment_song_list()
        elif not folder_list:
            self.increment_song_list(
                data=self.db_handler.get_song_where_tag(tag_list=tag_list)
            )
        elif not tag_list:
            self.increment_song_list(
                data=self.db_handler.get_song_where_folder(folder_list=folder_list)
            )
        else:
            self.increment_song_list(
                data=self.db_handler.get_song_where_tag_folder(
                    tag_list=tag_list,
                    folder_list=folder_list
                )
            )

    def reset_filter(self, sender):
        for folder in dpg.get_item_children("folder_list")[1]:
            dpg.set_value(folder, False)

        for tag in dpg.get_item_children("tag_list")[1]:
            dpg.set_value(tag, False)

        self.increment_song_list()

    def increment_song_list(self, data=None):
        # Cette méthode sera connectée à SongList
        pass

    def filter_search(self, sender, app_data, user_data):
        folders = self.db_handler.exe(
            "SELECT * FROM folder WHERE name LIKE '%" + app_data + "%' AND id IN (SELECT parent_id FROM song) ORDER BY parent_id"
        )
        dpg.delete_item("folder_list", children_only=True)
        for folder in folders:
            dpg.add_checkbox(
                label=f"{folder[1]}",
                callback=self.increment_song_from_filter,
                user_data=folder,
                parent="folder_list"
            )

        tags = self.db_handler.exe(
            "SELECT * FROM tag WHERE name LIKE '%" + app_data + "%' ORDER BY name"
        )
        dpg.delete_item("tag_list", children_only=True)
        for tag in tags:
            dpg.add_checkbox(
                label=f"{tag[1]}",
                callback=self.increment_song_from_filter,
                user_data=tag,
                parent="tag_list"
            )

    def removeall(self):
        dpg.delete_item("list", children_only=True)

    def increment_filter(self):
        dpg.delete_item("filters", children_only=True)

        with dpg.collapsing_header(label="Folder list", tag="folder_list", parent="filters"):
            for folder in self.db_handler.exe(
                    "SELECT * FROM folder WHERE id IN (SELECT parent_id FROM song) ORDER BY parent_id"):
                dpg.add_checkbox(
                    label=f"{folder[2]}",
                    callback=self.increment_song_from_filter,
                    user_data=folder,
                    parent="folder_list"
                )

        with dpg.collapsing_header(label="Tag list", tag="tag_list", parent="filters"):
            for tag in self.db_handler.exe("SELECT * FROM tag"):
                dpg.add_checkbox(
                    label=f"{tag[1]}",
                    callback=self.increment_song_from_filter,
                    user_data=tag,
                    parent="tag_list"
                ) 
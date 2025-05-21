import dearpygui.dearpygui as dpg
import time

def Y_scrolling_test(text="", parent=None):
    x = dpg.add_text(label=text)
    print(dpg.get_item_user_data(parent))

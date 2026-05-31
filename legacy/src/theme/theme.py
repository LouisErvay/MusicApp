import dearpygui.dearpygui as dpg

def create_theme():
    with dpg.theme(tag="base"):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Button, (130, 142, 250))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (137, 142, 255, 95))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (137, 130, 255))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 2, 2)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 14)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25))
            dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (130, 142, 250))
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (221, 166, 185))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (172, 174, 197))

    with dpg.theme(tag="slider_thin"):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

    with dpg.theme(tag="slider"):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250, 99))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250, 99))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250, 99))
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

    with dpg.theme(tag="songs"):
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (89, 89, 144, 40))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 100, 100, 100))
            dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0)

    with dpg.theme(tag="folder_list_button"):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 100, 100))

def apply_themes():
    # Application du thème de base
    dpg.bind_theme("base")

    # Application des thèmes spécifiques avec vérification
    theme_mappings = {
        "volume": "slider_thin",
        "song_pos_slider": "slider",
        "list": "songs",
        "folder_list": "folder_list_button"
    }

    for item, theme in theme_mappings.items():
        try:
            if dpg.does_item_exist(item):
                dpg.bind_item_theme(item, theme)
        except Exception as e:
            print(f"Impossible d'appliquer le thème {theme} à {item}: {e}") 
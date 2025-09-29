######################################################
# - UNREAL LIGHT MANAGER -
# AUTHOR : RUDY LETI
# DATE : 2025/07/25
# DESIGNED TO SPEED UP LIGHTING PRODUCTION PROCESS
#
# .LIST THE MOST COMMON UNREAL ENGINE LIGHTS
# . NAMING CONVENTION INTEGRATED
# . LIGHTS SELECTABLE FROM THE UI
# . ALLOW TO MUTE OR SOLO LIGHTS
# . ALLOW TO SEARCH LIGHTS BY NAME
# . ALLOW TO CREATE AND RENAME LIGHTS FROM THE UI
# . ALLOW TO DELETE LIGHTS FROM THE UI
# . ALLOW TO MODIFY THE MOST COMMON ATTRIBUTES FROM THE UI
######################################################

import os
import sys
from importlib import reload

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

# CURRENT SCRIPT PATH
script_path = os.path.dirname(os.path.abspath(__file__))

if script_path not in sys.path:
    sys.path.append(script_path)

import LightManagerUI as lmui
import UnrealLightLogic as ull

logic = None
ui = None


def main_window() -> lmui.LightManagerUI:
    """ MAIN FUNCTION TO LAUNCH THE UI WINDOW """

    global ui, logic, script_path

    ui = lmui.LightManagerUI()
    logic = ull.UnrealLightLogic(ui)

    # LOAD LOGO IMAGE
    logo_path = os.path.join(script_path, "img", "logo.png")
    img = QPixmap(logo_path)
    ui.logo.setPixmap(img)

    # SET SIGNALS
    ui.signal_table_selection.connect(logic.light_table_selection)
    ui.signal_light_created.connect(logic.create_light)
    ui.signal_light_renamed.connect(logic.rename_light)
    ui.signal_light_search.connect(logic.search_light)
    ui.button_render.clicked.connect(logic.render)
    ui.signal_light_deleted.connect(logic.delete)
    ui.signal_refresh.connect(logic.refresh)
    logic.refresh(ui.light_table)  # INITIAL REFRESH TO LOAD LIGHTS

    return ui


if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    main = main_window()
    main.show()

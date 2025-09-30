from functools import partial
import os

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QCheckBox, QLabel, QColorDialog, QApplication
from PySide6.QtCore import Qt, QTimer, QObject
from PySide6.QtGui import QPixmap, QColor
import unreal

from LightManagerUI import CustomLineEditNum

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


class UnrealLightLogic(QObject):
    """
    A class that handles the logic and interaction between the UI and Unreal Engine.
    It manages light creation, renaming, deletion, and attribute modification.
    """

    def __init__(self, ui):
        """
        Initializes the logic for the Light Manager.
        Args:
            ui (LightManagerUI): An instance of the UI class to which this logic will connect.
        """
        super().__init__()
        self.ui = ui
        self.editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.ell = unreal.EditorLevelLibrary
        self.script_jobs = []  # JOB ID COLLECTOR
        self.lightTypes = {
            "SkyLight": [unreal.SkyLight, unreal.SkyLightComponent],
            "RectLight": [unreal.RectLight, unreal.RectLightComponent],
            "SpotLight": [unreal.SpotLight, unreal.SpotLightComponent],
            "PointLight": [unreal.PointLight, unreal.PointLightComponent],
            "DirectionalLight": [unreal.DirectionalLight, unreal.DirectionalLightComponent],
        }

    def get_actor_by_label(self, actor_name) -> unreal.Actor:
        """Finds an actor in the current level by its display label."""
        all_actors = self.editor_subsystem.get_all_level_actors()
        for actor in all_actors:
            if actor.get_actor_label() == actor_name:
                return actor
        return

    def rename_light(self, old_name: str, new_name: str, light_table: object):
        """
        Renames a light actor in the Unreal scene and updates the UI table accordingly.
        """
        num = 0
        naming_convention = f"{new_name}_{num:03d}"

        if not new_name.strip():
            self.info_timer("Error: New name cannot be empty.")
            return

        actor = self.get_actor_by_label(old_name)
        if actor:  # Check if actor still exists
            while self.get_actor_by_label(naming_convention) in self.editor_subsystem.get_all_level_actors():
                num += 1
                naming_convention = f"{new_name}_{num:03d}"
            actor.set_actor_label(naming_convention)
            self.refresh(light_table)
            self.info_timer(f"Light: '{old_name}' renamed to '{new_name}'")
        else:
            self.info_timer(f"Error: Could not find actor '{old_name}' to rename.")

    def refresh(self, light_table: object):
        """
        Clears and repopulates the entire UI table with lights from the Unreal scene.
        """
        light_table.setRowCount(0)  # CLEAR EXISTING ROWS

        # REPOPULATE THE TABLE
        all_actors = self.editor_subsystem.get_all_level_actors()
        light_actor_class_types = tuple([item[0] for item in self.lightTypes.values()])
        all_lights = [actor for actor in all_actors if isinstance(actor, light_actor_class_types)]

        for light_actor in sorted(all_lights, key=lambda actor: actor.get_actor_label()):
            light_type = light_actor.get_class().get_name()
            light_component_class = self.lightTypes.get(light_type)[1]
            light_component = light_actor.get_component_by_class(light_component_class)

            if light_component:
                self.light_name_to_list(light_actor, light_type, light_table)
                self.mute_solo_to_list(light_actor, light_component, light_table, light_type)
                self.color_button_to_list(light_component, light_table)
                self.entry_attr_num_to_list(light_component, "Intensity", 5, light_table)
                use_temp = self.checkbox_attr_to_list(light_component, "use_temperature", 6, light_table, channel=None)
                if use_temp == True:
                    self.entry_attr_num_to_list(light_component, "temperature", 7, light_table)
                    self.info_timer("Temperature enabled for this light")
                else:
                    widget = QLabel("N/A")
                    widget.setAlignment(Qt.AlignCenter)
                    light_table.setCellWidget(self.row_position, 7, widget)
                self.entry_attr_num_to_list(light_component, "attenuation_radius", 8, light_table)
                self.checkbox_attr_to_list(light_component, "lighting_channels", 9, light_table, channel="channel0")
                self.checkbox_attr_to_list(light_component, "lighting_channels", 10, light_table, channel="channel1")
                self.checkbox_attr_to_list(light_component, "lighting_channels", 11, light_table, channel="channel2")
                #  add more attributes here based on your UI

        self.info_timer("Light Manager refreshed successfully.")

    def delete(self, light_table: object):
        """
        Deletes the currently selected light from the Unreal scene.
        """
        selected_items = light_table.selectedItems()
        if not selected_items:
            return

        light_name = selected_items[0].text()
        actor_to_delete = self.get_actor_by_label(light_name)

        if actor_to_delete:
            self.editor_subsystem.destroy_actor(actor_to_delete)
            self.refresh(light_table)
            self.info_timer(f"Light '{light_name}' deleted successfully.")
        else:
            self.info_timer(f"Error: Could not find actor '{light_name}' to delete.")

    def light_table_selection(self, lightTable: object):
        """
        Selects the corresponding light actor in the Unreal scene when a row is selected in the UI table.
        """
        selected_items = lightTable.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            light_name_item = lightTable.item(row, 0)
            if light_name_item:
                light_name = light_name_item.text()
                self.editor_subsystem.set_selected_level_actors([])  # CLEAR CURRENT SELECTION
                try:
                    actor = self.get_actor_by_label(light_name)
                    self.editor_subsystem.set_selected_level_actors([actor])  # SELECT THE ACTOR
                except ValueError:
                    self.info_timer(f"Error:  '{light_name}' None Existent")
        else:
            self.editor_subsystem.set_selected_level_actors([])

    def create_light(self, light_name: str, light_type: str, light_table: object):
        """
        Creates a new light actor in the Unreal scene with a unique name based on the specified type and optional name.
        """
        if light_type not in self.lightTypes:
            self.info_timer(f"Error: Light type '{light_type}' is invalid.")
            return

        if not light_name.strip():
            light_name = light_type

        # INCREMENTAL NAMING CONVENTION
        num = 0
        naming_convention = f"LGT_{light_name}_{num:03d}"
        all_actor_labels = {actor.get_actor_label() for actor in self.editor_subsystem.get_all_level_actors()}
        while naming_convention in all_actor_labels:
            num += 1
            naming_convention = f"LGT_{light_name}_{num:03d}"

        # SPAWN THE LIGHT ACTOR
        light_location = unreal.Vector(x=0.0, y=0.0, z=100.0)
        light_actor_class = self.lightTypes.get(light_type)

        if not light_actor_class[0]:
            self.info_timer(f"Error: Could not find class for light type '{light_type}'.")
            return

        # Create the light actor
        light_actor = self.editor_subsystem.spawn_actor_from_class(light_actor_class[0], location=light_location)
        # Set the Actor name
        light_actor.set_actor_label(naming_convention)
        # Access  Light Component from the actor
        light_component = light_actor.get_component_by_class(light_actor_class[1])

        # SET DEFAULT ATTRIBUTES BASED ON LIGHT TYPE
        if light_component:
            if light_type == "SkyLight":
                light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
                light_component.set_intensity(1.0)
            elif light_type == "DirectionalLight":
                light_component.set_intensity(3.0)
            else:
                desired_units = unreal.LightUnits.LUMENS
                light_component.set_intensity_units(desired_units)
                light_component.set_intensity(10.0)
                light_component.set_attenuation_radius(1000)
                light_component.set_lighting_channels(channel0=True, channel1=False, channel2=False)

            light_component.set_light_color(unreal.LinearColor(1.0, 1.0, 1.0))
            light_component.set_cast_shadows(True)

        # POPULATE THE TABLE LIST
        self.refresh(light_table)  # REFRESH THE ENTIRE TABLE

        self.info_timer(f"'{light_type}': '{light_name}' has been created successfully.")

    def light_name_to_list(self, light_actor: unreal.Actor, light_type: str, light_table: object):
        """
        Adds a new row to the light table for the given light actor. 
        """
        self.row_position = light_table.rowCount()
        light_table.insertRow(self.row_position)

        # POPULATE THE "Name" COLUMN
        name_item = QTableWidgetItem(light_actor.get_actor_label())
        name_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        light_table.setItem(self.row_position, 0, name_item)

        # POPULATE THE "Light Type" COLUMN
        icon_light_type = QLabel()
        icon_path = os.path.join(SCRIPT_PATH, "img", "icons", f"{light_type}.png")

        img = QPixmap(icon_path)
        icon_light_type.setPixmap(img)
        icon_light_type.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        light_table.setCellWidget(self.row_position, 3, icon_light_type)

    def mute_solo_to_list(self, light_actor: unreal.Actor, light_component: unreal, light_table: object, light_type: str):
        """
        Adds Mute and Solo checkboxes to the current row in the table.
        """
        mute_widget = QWidget()
        mute_checkbox = QCheckBox()
        mute_checkbox.setStyleSheet("QCheckBox::indicator:unchecked { background-color: #f94144 }")
        if light_component:
            actual_visibility = light_component.is_visible()
            if actual_visibility == True or actual_visibility == False:
                mute_checkbox.setChecked(actual_visibility)
            mute_checkbox.stateChanged.connect(partial(self.update_all_lights_visibility, light_table))
        else:
            self.info_timer(
                f"Warning: No light component found for actor '{light_actor.get_actor_label()}' of type '{light_type}'. Mute checkbox disabled.")
            mute_checkbox.setEnabled(False)
            mute_checkbox.setChecked(False)  # Default to not muted if component is missing

        mute_checkbox.stateChanged.connect(lambda: self.update_all_lights_visibility(light_table))
        mute_layout = QHBoxLayout(mute_widget)
        mute_layout.addWidget(mute_checkbox)
        mute_layout.setAlignment(Qt.AlignCenter)
        mute_layout.setContentsMargins(0, 0, 0, 0)

        solo_widget = QWidget()
        solo_checkbox = QCheckBox()
        solo_checkbox.setStyleSheet("QCheckBox::indicator:checked { background-color: #adb5bd }")
        solo_checkbox.stateChanged.connect(partial(self.on_solo_toggled, self.row_position, light_table))
        solo_layout = QHBoxLayout(solo_widget)
        solo_layout.addWidget(solo_checkbox)
        solo_layout.setAlignment(Qt.AlignCenter)
        solo_layout.setContentsMargins(0, 0, 0, 0)

        light_table.setCellWidget(self.row_position, 1, mute_widget)
        light_table.setCellWidget(self.row_position, 2, solo_widget)

    def color_button_to_list(self, light_component, light_table: object):
        """
        Adds a color button to the current row in the table that reflects the light's color.
        Clicking the button opens a color picker to change the light's color.
        """
        colorBtn_widget = QWidget()
        colorBtn = QPushButton()
        colorBtn.setFixedSize(56, 26)
        self.set_button_color(light_component, colorBtn)
        colorBtn.clicked.connect(partial(self.set_color, light_component, colorBtn))

        colorBtn_layout = QHBoxLayout(colorBtn_widget)
        colorBtn_layout.addWidget(colorBtn)
        colorBtn_layout.setAlignment(Qt.AlignCenter)
        colorBtn_layout.setContentsMargins(0, 0, 0, 0)
        light_table.setCellWidget(self.row_position, 4, colorBtn_widget)

    def entry_attr_num_to_list(self, light_component: unreal, attribute_name: str, column: int, light_table: object):
        """
        Adds a numeric input field to a cell for a specific float or int attribute.
        """
        try:
            atttribute_value = light_component.get_editor_property(attribute_name)
        except (Exception, ValueError):
            self.info_timer(f"No Parameter {attribute_name} for this light")
            widget = QLabel("N/A")
            widget.setAlignment(Qt.AlignCenter)
            light_table.setCellWidget(self.row_position, column, widget)
            return
        # SETTING THE CURRENT VALUE IN THE UI
        bar_text = CustomLineEditNum()
        bar_text.setFixedSize(65, 29)
        bar_text.setAlignment(Qt.AlignCenter)

        if isinstance(atttribute_value, (float)):
            bar_text.setText(f"{atttribute_value:.3f}")
        elif isinstance(atttribute_value, (int)):
            bar_text.setText(f"{atttribute_value}")

        def _update_unreal_from_ui():
            # GET VALUE FROM UI
            new_value = float(bar_text.text())
            try:
                # SET VALUE IN UNREAL
                light_component.set_editor_property(attribute_name, new_value)
            except (ValueError, RuntimeError):
                self.info_timer(f"Wrong input:  Please enter a number")
                # ON ERROR, Reset the text to the current value in UNREAL
                current_unreal_val = light_component.get_editor_property(attribute_name)
                if isinstance(current_unreal_val, (float)):
                    bar_text.setText(f"{current_unreal_val:.3f}")
                elif isinstance(current_unreal_val, (int)):
                    bar_text.setText(f"{current_unreal_val}")
        bar_text.editingFinished.connect(_update_unreal_from_ui)

        widget = QWidget()
        bar_text_layout = QHBoxLayout(widget)
        bar_text_layout.addWidget(bar_text)
        bar_text_layout.setAlignment(Qt.AlignCenter.AlignCenter)
        bar_text_layout.setContentsMargins(0, 0, 0, 0)
        light_table.setCellWidget(self.row_position, column, widget)

    def checkbox_attr_to_list(self, light_component: unreal, attribute_name: str, column: int, light_table: object, channel: str = None):
        """
        Adds a checkbox to a cell for a specific boolean attribute.
        If the attribute is 'lighting_channels', a specific channel can be specified."""
        if not light_component:
            return

        try:
            current_value = light_component.get_editor_property(attribute_name)

        except (Exception, ValueError):
            self.info_timer(f"No Parameter {attribute_name} for this light")
            widget = QLabel("N/A")
            widget.setAlignment(Qt.AlignCenter)
            light_table.setCellWidget(self.row_position, column, widget)
            return

        if attribute_name == "lighting_channels":
            current_value = current_value.get_editor_property(channel)
        if current_value is True or current_value is False:
            widget = QWidget()
            checkbox = QCheckBox()
            checkbox.setChecked(bool(current_value))

        def _update_unreal_from_ui(state):
            if attribute_name == "lighting_channels":
                light_channels = light_component.get_editor_property(attribute_name)
                light_channels.set_editor_property(channel, bool(state))
                light_component.set_editor_property("lighting_channels", light_channels)
            elif light_component:
                light_component.set_editor_property(attribute_name, state)

        checkbox.stateChanged.connect(_update_unreal_from_ui)

        layout = QHBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        light_table.setCellWidget(self.row_position, column, widget)
        return current_value

    def on_solo_toggled(self, toggled_row: int, light_table: object, state: bool, *args: str):
        """
        Ensures that only one 'Solo' checkbox can be active at a time.
        When a 'Solo' checkbox is checked, all other 'Solo' checkboxes are unchecked.
        """
        if state == Qt.Checked:
            # SKIP the ROW OF THE CHECKBOX THAT WAS JUST TOGGLED
            for i in range(light_table.rowCount()):
                if i != toggled_row:
                    solo_widget = light_table.cellWidget(i, 2)
                    if solo_widget:
                        # RETRIEVE THE CUSTOM WIDGET IN THE  'Solo' COLUMN
                        solo_checkbox = solo_widget.findChild(QCheckBox)
                        if solo_checkbox and solo_checkbox.isChecked():     # PREVENT RECURSIVE CALLS OF THIS FUNCTION
                            solo_checkbox.blockSignals(True)
                            solo_checkbox.setChecked(False)
                            solo_checkbox.blockSignals(False)
        self.update_all_lights_visibility(light_table)

    def update_all_lights_visibility(self, light_table: object, *args):
        """
        Updates the visibility of all lights based on the states of the 'Mute' and 'Solo' checkboxes.
        """
        soloed_row = -1
        # CHECK IF ANY LIGHT IS SOLOED
        for i in range(light_table.rowCount()):
            solo_widget = light_table.cellWidget(i, 2)
            if solo_widget:
                solo_checkbox = solo_widget.findChild(QCheckBox)
                if solo_checkbox and solo_checkbox.isChecked():
                    # IF A SOLO CHECKBOX IS FOUND AND CHECKED, STORE ITS ROW INDEX
                    soloed_row = i
                    break

        # ITERATE THROUGH ALL LIGHTS TO SET THEIR VISIBILITY
        for i in range(light_table.rowCount()):
            light_name_item = light_table.item(i, 0)
            mute_widget = light_table.cellWidget(i, 1)
            if not (light_name_item and mute_widget):
                continue

            light_name = light_name_item.text()
            current_actor = self.get_actor_by_label(light_name)
            if not current_actor:
                continue

            mute_checkbox = mute_widget.findChild(QCheckBox)
            if mute_checkbox:
                # If a row is soloed, only it is visible. Otherwise, visibility depends on the mute checkbox.
                is_visible = (i == soloed_row) if soloed_row != -1 else mute_checkbox.isChecked()
                # Get the light component to set its visibility
                light_type = current_actor.get_class().get_name()
                if light_type in self.lightTypes:
                    light_component_class = self.lightTypes[light_type][1]
                    light_component = current_actor.get_component_by_class(light_component_class)
                    if light_component:
                        light_component.set_visibility(is_visible)
                        current_actor.set_is_temporarily_hidden_in_editor(not is_visible)
                    else:
                        self.info_timer(
                            f"Warning: No light component found for actor '{light_name}' of type '{light_type}'. Cannot set visibility.")
                else:
                    self.info_timer(
                        f"Warning: Light type '{light_type}' not recognized or component missing for '{light_name}'. Cannot set visibility.")

    def set_color(self, light_component: unreal, color_button: QPushButton):
        """
        Opens a color picker dialog to set the light's color and updates the button's background color.
        """
        if not light_component:
            return

        # GET THE ACTUAL LIGHT COLOR
        linear_color = light_component.get_light_color()
        color = (int(linear_color.r * 255), int(linear_color.g * 255), int(linear_color.b * 255))
        # OPEN COLOR PICKER DIALOG
        color_dialog = QColorDialog(currentColor=QColor(color[0], color[1], color[2]), parent=self.ui)
        color_dialog.open()

        if color_dialog.exec() == QColorDialog.Accepted:
            new_color = color_dialog.selectedColor()
            r, g, b = new_color.redF(), new_color.greenF(), new_color.blueF()
            light_component.set_light_color(unreal.LinearColor(r, g, b))  # SET THE NEW COLOR TO THE LIGHT
            self.set_button_color(light_component, color_button)

    def set_button_color(self, light_component: unreal, color_button: QPushButton, color: tuple = None):
        """
        Sets the background color of a QPushButton to match the light's color.
        """
        if not light_component:
            return

        linear_color = light_component.get_light_color()
        r = int(linear_color.r * 255)
        g = int(linear_color.g * 255)
        b = int(linear_color.b * 255)
        color_button.setStyleSheet(f"background-color: rgba({r},{g},{b},1)")

    def search_light(self, *args: str | object):
        """
        Filters the visibility of rows in the table based on a search string.

        Args:
            args[0] (str): The text to search for in the light names.
            args[1] (QTableWidget): The table whose rows will be filtered.
        """
        search_text = args[0]
        if not search_text:
            self.refresh(args[1])
            return
        if search_text:
            for row in range(args[1].rowCount()):
                researsh_light = args[1].item(row, 0).text()
                if search_text in researsh_light.lower():
                    args[1].showRow(row)
                else:
                    args[1].hideRow(row)

    def render(self):
        """ Triggers the rendering of the current scene in Unreal Engine."""
        unreal.EditorLevelLibrary.editor_play_simulate()

    def info_timer(self, text: str, duration_ms: int = 3500):
        """
        Displays a message in the UI's info label for a specified duration.

        Args:
            text (str): The message to display.
            duration_ms (int, optional): How long to display the message in milliseconds. Defaults to 3500.
        """
        self.ui.info_text.setText(text)
        QTimer.singleShot(duration_ms, lambda: self.ui.info_text.setText(""))

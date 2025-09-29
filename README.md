 # Unreal Light Manager 🔦
 
<img width="1888" height="912" alt="image" src="https://github.com/user-attachments/assets/8f0529c7-81a7-4757-ac36-2f319aea8b2a" />

 
 ## 1. Overview
 
 The Unreal Light Manager is a powerful tool designed to streamline the lighting workflow within Unreal Engine. It provides a compact and intuitive user interface to manage, create, and modify all common light types in your scene directly from one panel. This tool is perfect for lighting artists and level designers who need to quickly iterate on lighting setups without constantly navigating the World Outliner and Details panels.
 
 ## 2. Features
 
 *   **Comprehensive Light Listing:** Automatically lists all lights in the current level, sorted by name.
 *   **Light Creation:** Quickly create any standard light type (`SkyLight`, `RectLight`, `SpotLight`, `PointLight`, `DirectionalLight`) with a consistent naming convention.
 *   **Direct Attribute Editing:** Modify common light properties directly from the UI table:
     *   Visibility (Mute/Solo)
     *   Color
     *   Intensity
     *   Use Temperature & Temperature Value
     *   Attenuation Radius
     *   Lighting Channels (0, 1, 2)
 *   **Scene Interaction:**
     *   Select a light in the UI to select it in the Unreal Editor.
     *   Rename and delete lights.
     *   Start a "Simulate" session in the editor.
 *   **Efficient Workflow Tools:**
     *   **Search:** Instantly filter the light list by name.
     *   **Refresh:** Update the list to reflect the current state of the scene.
     *   **Solo/Mute:** Quickly isolate lights or toggle their visibility.
 
 ## 3. How to Use
 
 ### 3.1. Main Interface
 
 The interface is divided into two main sections: creation/renaming controls and the light list.
 
 !image
 
 
 ### 3.2. Creating and Managing Lights
 
 *   **Create Light:**
     1.  Optionally, enter a base name in the **Light Name** field. If left blank, the light type will be used as the name.
     2.  Select the desired light type from the **Light Type** dropdown.
     3.  Click **Create Light**. A new light will be spawned in the scene with a unique name (e.g., `LGT_PointLight_001`) and added to the list.
 
 *   **Rename Light:**
     1.  Select a light in the table.
     2.  Enter the new base name in the **Light Name** field.
     3.  Click **Rename Light**. The actor in the scene will be renamed (e.g., to `NewName_001`).
 
 *   **Delete Light:**
     1.  Select a light in the table.
     2.  Click the **Delete** button. You will be asked for confirmation before the light is removed from the scene.
 
 *   **Refresh:**
     *   Click the **Refresh** button to clear and reload the list with all lights currently in the level. This is useful if you've made changes outside the tool.
 
 *   **Search:**
     *   Type in the **Search by name** field to dynamically filter the list. The search is case-insensitive. Clear the field to see all lights again.
 
 *   **Simulate:**
     *   Click the **Simulate** button to start a Play-in-Editor (PIE) simulation, allowing you to see dynamic lighting and other effects.
 
 ### 3.3. The Light Table
 
 The core of the tool is the table, which gives you an at-a-glance view and control over your lights.
 
 | Column        | Description                                                                                                                            |
 |---------------|----------------------------------------------------------------------------------------------------------------------------------------|
 | **Name**      | The display name of the light actor in Unreal. Clicking a name selects the light in the editor.                                          |
 | **V (Visible)** | A checkbox to toggle the light's visibility on and off (Mute). Unchecked means hidden.                                                 |
 | **S (Solo)**  | A checkbox to solo a light. When checked, all other lights become invisible, allowing you to isolate its contribution. Only one light can be soloed at a time. |
 | **Type**      | An icon representing the light's type (e.g., Point Light, Spot Light).                                                                 |
 | **Color**     | A color swatch showing the light's current color. Click it to open a color picker and change the color.                                |
 | **Intensity** | A numeric field for the light's intensity. You can type a value or use the **mouse wheel** to adjust it.                                 |
 | **Use Temp.** | A checkbox to enable or disable temperature-based color.                                                                               |
 | **Temperature**| A numeric field for the light's color temperature in Kelvin. This is only active if "Use Temp." is checked.                             |
 | **Att. Radius**| A numeric field for the light's attenuation radius.                                                                                    |
 | **Chl.0 - 2** | Checkboxes to toggle the light's participation in Lighting Channels 0, 1, and 2.                                                         |
 
 > **Note:** Some attributes like `Temperature` and `Attenuation Radius` may show "N/A" if they are not applicable to the selected light type (e.g., a Sky Light).
 
 ## 4. Installation
 
 1.  Copy the script folder (`Unreal_Light_Manager`) into your Unreal Engine project's `Content/Python` directory.
 2.  In the Unreal Editor, open the **Output Log** (`Window` > `Developer Tools` > `Output Log`).
 3.  In the `Cmd` console at the bottom of the Output Log, type `py ulm_main.py` and press Enter.
 4.  The Unreal Light Manager window will appear.
 
 ---

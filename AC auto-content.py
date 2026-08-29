import os
import shutil
import tempfile
import winreg
from tkinter import Tk, filedialog, messagebox, Button, Label

try:
    import patoolib
except ImportError:
    patoolib = None


# ============================================================
# CONFIG
# ============================================================

TEMP_EXTRACT_DIR = os.path.join(
    tempfile.gettempdir(),
    "AC_Auto_Installer"
)


# ============================================================
# ASSETTO CORSA PATH
# ============================================================

def get_assetto_corsa_path():

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244210",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244210"
    ]

    for registry_path in registry_paths:

        try:

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                registry_path
            ) as key:

                install_path, _ = winreg.QueryValueEx(
                    key,
                    "InstallLocation"
                )

                if os.path.isdir(install_path):
                    return install_path

        except Exception:
            pass


    common_paths = [

        r"C:\Program Files (x86)\Steam\steamapps\common\assettocorsa",

        r"C:\Program Files\Steam\steamapps\common\assettocorsa",

        r"D:\SteamLibrary\steamapps\common\assettocorsa",

        r"E:\SteamLibrary\steamapps\common\assettocorsa",

        r"F:\SteamLibrary\steamapps\common\assettocorsa"

    ]


    for path in common_paths:

        if os.path.isdir(path):
            return path


    return None


# ============================================================
# TEMP CLEANUP
# ============================================================

def clean_temp_folder():

    if os.path.exists(TEMP_EXTRACT_DIR):

        try:
            shutil.rmtree(
                TEMP_EXTRACT_DIR
            )

        except Exception:
            pass


# ============================================================
# EXTRACT ARCHIVE
# ============================================================

def extract_archive(
    archive_path,
    extract_to
):

    if patoolib is None:

        raise Exception(
            "The 'patool' module is missing.\n\n"
            "Install it with:\n"
            "pip install patool"
        )


    patoolib.extract_archive(
        archive_path,
        outdir=extract_to,
        verbosity=-1
    )


# ============================================================
# FILE SEARCH
# ============================================================

def find_file_recursive(
    folder,
    filename
):

    filename = filename.lower()

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower() == filename:

                return os.path.join(
                    root,
                    file
                )

    return None


def find_files_recursive(
    folder,
    extension
):

    results = []

    extension = extension.lower()

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(
                extension
            ):

                results.append(
                    os.path.join(
                        root,
                        file
                    )
                )

    return results


# ============================================================
# CAR DETECTION
# ============================================================

def score_car_folder(folder):

    score = 0

    files = {
        f.lower()
        for f in os.listdir(folder)
        if os.path.isfile(
            os.path.join(
                folder,
                f
            )
        )
    }


    # Strong indicators

    if "ui_car.json" in files:
        score += 100


    if "data.acd" in files:
        score += 80


    if "lods.ini" in files:
        score += 70


    # KN5 models

    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(
        kn5_count * 20,
        60
    )


    # Other common AC car files

    if "car.ini" in files:
        score += 30


    if "engine.ini" in files:
        score += 20


    if "suspensions.ini" in files:
        score += 20


    if "drivetrain.ini" in files:
        score += 20


    if "tyres.ini" in files:
        score += 20


    return score


# ============================================================
# TRACK DETECTION
# ============================================================

def score_track_folder(folder):

    score = 0

    files = {
        f.lower()
        for f in os.listdir(folder)
        if os.path.isfile(
            os.path.join(
                folder,
                f
            )
        )
    }


    if "ui_track.json" in files:
        score += 100


    if "models.ini" in files:
        score += 80


    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(
        kn5_count * 20,
        80
    )


    if "surfaces.ini" in files:
        score += 30


    return score


# ============================================================
# FIND MOD ROOT
# ============================================================

def find_mod_root(
    extracted_folder
):

    possible_cars = []
    possible_tracks = []


    # --------------------------------------------------------
    # First scan every directory
    # --------------------------------------------------------

    for root, dirs, files in os.walk(
        extracted_folder
    ):

        car_score = score_car_folder(
            root
        )

        track_score = score_track_folder(
            root
        )


        if car_score > 0:

            possible_cars.append(
                (
                    car_score,
                    root
                )
            )


        if track_score > 0:

            possible_tracks.append(
                (
                    track_score,
                    root
                )
            )


    # --------------------------------------------------------
    # Prefer cars with ui_car.json
    # --------------------------------------------------------

    if possible_cars:

        possible_cars.sort(
            key=lambda x: x[0],
            reverse=True
        )

        best_score, best_folder = (
            possible_cars[0]
        )

        return best_folder, "cars"


    # --------------------------------------------------------
    # Otherwise tracks
    # --------------------------------------------------------

    if possible_tracks:

        possible_tracks.sort(
            key=lambda x: x[0],
            reverse=True
        )

        best_score, best_folder = (
            possible_tracks[0]
        )

        return best_folder, "tracks"


    return None, None


# ============================================================
# FIND PROPER AC ROOT
# ============================================================

def climb_to_ac_root(
    folder,
    extracted_folder,
    mod_type
):

    current = folder

    best = folder


    while current != extracted_folder:

        parent = os.path.dirname(
            current
        )

        if parent == current:
            break


        files = {
            f.lower()
            for f in os.listdir(parent)
            if os.path.isfile(
                os.path.join(
                    parent,
                    f
                )
            )
        }


        if mod_type == "cars":

            indicators = [
                "ui_car.json",
                "data.acd",
                "lods.ini",
                "car.ini"
            ]


            has_kn5 = any(
                f.endswith(".kn5")
                for f in files
            )


            if (
                any(
                    x in files
                    for x in indicators
                )
                or has_kn5
            ):

                best = parent


        else:

            indicators = [
                "ui_track.json",
                "models.ini",
                "surfaces.ini"
            ]


            has_kn5 = any(
                f.endswith(".kn5")
                for f in files
            )


            if (
                any(
                    x in files
                    for x in indicators
                )
                or has_kn5
            ):

                best = parent


        current = parent


    return best


# ============================================================
# VALIDATE CAR
# ============================================================

def validate_car(
    car_folder
):

    problems = []
    found = []


    # KN5

    kn5_files = find_files_recursive(
        car_folder,
        ".kn5"
    )


    if kn5_files:

        found.append(
            f"{len(kn5_files)} KN5 model(s)"
        )

    else:

        problems.append(
            "No .kn5 model found"
        )


    # UI

    ui_file = find_file_recursive(
        car_folder,
        "ui_car.json"
    )


    if ui_file:

        found.append(
            "ui_car.json"
        )

    else:

        problems.append(
            "ui_car.json not found"
        )


    # LODS

    lods_file = find_file_recursive(
        car_folder,
        "lods.ini"
    )


    # DATA ACD

    data_acd = find_file_recursive(
        car_folder,
        "data.acd"
    )


    if lods_file:

        found.append(
            "lods.ini"
        )

    elif data_acd:

        found.append(
            "data.acd"
        )

    else:

        problems.append(
            "Neither lods.ini nor data.acd found"
        )


    return found, problems


# ============================================================
# VALIDATE TRACK
# ============================================================

def validate_track(
    track_folder
):

    problems = []
    found = []


    kn5_files = find_files_recursive(
        track_folder,
        ".kn5"
    )


    if kn5_files:

        found.append(
            f"{len(kn5_files)} KN5 model(s)"
        )

    else:

        problems.append(
            "No .kn5 model found"
        )


    ui_file = find_file_recursive(
        track_folder,
        "ui_track.json"
    )


    if ui_file:

        found.append(
            "ui_track.json"
        )


    models_ini = find_file_recursive(
        track_folder,
        "models.ini"
    )


    if models_ini:

        found.append(
            "models.ini"
        )

    else:

        problems.append(
            "models.ini not found"
        )


    return found, problems


# ============================================================
# COPY MOD
# ============================================================

def install_folder(
    source,
    destination
):

    if os.path.exists(destination):

        shutil.rmtree(
            destination
        )


    shutil.copytree(
        source,
        destination
    )


# ============================================================
# MAIN INSTALLER
# ============================================================

def identify_and_install():

    ac_path = get_assetto_corsa_path()


    # --------------------------------------------------------
    # Find Assetto Corsa
    # --------------------------------------------------------

    if not ac_path:

        messagebox.showinfo(
            "Assetto Corsa",
            "Assetto Corsa could not be found automatically."
        )


        ac_path = filedialog.askdirectory(
            title="Select your Assetto Corsa folder"
        )


        if not ac_path:
            return


    # --------------------------------------------------------
    # Select archive
    # --------------------------------------------------------

    archive = filedialog.askopenfilename(

        title="Select Assetto Corsa Mod",

        filetypes=[
            (
                "Supported Archives",
                "*.zip;*.rar;*.7z"
            ),
            (
                "All Files",
                "*.*"
            )
        ]

    )


    if not archive:
        return


    clean_temp_folder()


    os.makedirs(
        TEMP_EXTRACT_DIR,
        exist_ok=True
    )


    try:

        # ----------------------------------------------------
        # Extract
        # ----------------------------------------------------

        extract_archive(
            archive,
            TEMP_EXTRACT_DIR
        )


        # ----------------------------------------------------
        # Detect
        # ----------------------------------------------------

        mod_root, mod_type = find_mod_root(
            TEMP_EXTRACT_DIR
        )


        if not mod_root:

            raise Exception(
                "Could not detect an Assetto Corsa "
                "car or track in this archive."
            )


        # ----------------------------------------------------
        # Climb to proper root
        # ----------------------------------------------------

        mod_root = climb_to_ac_root(
            mod_root,
            TEMP_EXTRACT_DIR,
            mod_type
        )


        # ----------------------------------------------------
        # Folder name
        # ----------------------------------------------------

        folder_name = os.path.basename(
            os.path.normpath(
                mod_root
            )
        )


        if not folder_name:

            raise Exception(
                "Could not determine the mod folder name."
            )


        # ----------------------------------------------------
        # Prevent bad generic names
        # ----------------------------------------------------

        bad_names = {
            "content",
            "cars",
            "tracks",
            "assettocorsa",
            "temp",
            "ac_auto_installer"
        }


        if folder_name.lower() in bad_names:

            raise Exception(
                "The detected folder is not a valid "
                "Assetto Corsa mod folder."
            )


        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if mod_type == "cars":

            found, problems = validate_car(
                mod_root
            )

        else:

            found, problems = validate_track(
                mod_root
            )


        # ----------------------------------------------------
        # Destination
        # ----------------------------------------------------

        destination = os.path.join(
            ac_path,
            "content",
            mod_type,
            folder_name
        )


        # ----------------------------------------------------
        # Existing installation
        # ----------------------------------------------------

        if os.path.exists(destination):

            replace = messagebox.askyesno(
                "Mod Already Installed",
                f"{folder_name} is already installed.\n\n"
                "Replace the existing installation?"
            )


            if not replace:
                return


        # ----------------------------------------------------
        # Install
        # ----------------------------------------------------

        install_folder(
            mod_root,
            destination
        )


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        mod_name = (
            "Car"
            if mod_type == "cars"
            else "Track"
        )


        message = (
            f"{mod_name} installed successfully!\n\n"
            f"Name: {folder_name}\n"
            f"Type: {mod_type}\n\n"
            f"Location:\n{destination}\n\n"
            "Detected files:\n"
            + "\n".join(
                f"• {item}"
                for item in found
            )
        )


        if problems:

            message += (
                "\n\nWarnings:\n"
                + "\n".join(
                    f"• {problem}"
                    for problem in problems
                )
            )

        else:

            message += (
                "\n\nNo obvious missing files detected."
            )


        messagebox.showinfo(
            "Installation Complete",
            message
        )


    except Exception as error:

        messagebox.showerror(
            "Installation Error",
            f"Could not install the mod.\n\n"
            f"{error}"
        )


    finally:

        clean_temp_folder()


# ============================================================
# GUI
# ============================================================

root = Tk()

root.title(
    "AC Auto-Content Installer"
)

root.geometry(
    "480x260"
)

root.resizable(
    False,
    False
)

root.attributes(
    "-topmost",
    True
)


title = Label(
    root,
    text="Assetto Corsa\nAuto-Content Installer",
    font=(
        "Arial",
        16,
        "bold"
    ),
    pady=25
)

title.pack()


button = Button(
    root,
    text="Select Mod Archive",
    command=identify_and_install,
    bg="#107C41",
    fg="white",
    font=(
        "Arial",
        12,
        "bold"
    ),
    padx=30,
    pady=12
)

button.pack(
    pady=10
)


supported = Label(
    root,
    text="ZIP  •  RAR  •  7Z",
    font=(
        "Arial",
        9
    )
)

supported.pack()


root.mainloop()
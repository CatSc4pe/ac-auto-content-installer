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
            shutil.rmtree(TEMP_EXTRACT_DIR)

        except Exception:
            pass


# ============================================================
# EXTRACT
# ============================================================

def extract_archive(archive_path, extract_to):

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

def find_file_recursive(folder, filename):

    filename = filename.lower()

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower() == filename:
                return os.path.join(root, file)

    return None


def find_files_recursive(folder, extension):

    results = []

    extension = extension.lower()

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(extension):

                results.append(
                    os.path.join(root, file)
                )

    return results


# ============================================================
# DIRECTORY HELPERS
# ============================================================

def directory_contains(folder, name):

    target = os.path.join(folder, name)

    return os.path.exists(target)


def has_kn5(folder):

    for root, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(".kn5"):
                return True

    return False


# ============================================================
# CAR DETECTION
# ============================================================

def score_car_folder(folder):

    score = 0

    files = {
        f.lower()
        for f in os.listdir(folder)
        if os.path.isfile(
            os.path.join(folder, f)
        )
    }

    if "ui_car.json" in files:
        score += 150

    if "data.acd" in files:
        score += 100

    if "lods.ini" in files:
        score += 100

    if "car.ini" in files:
        score += 40

    if "engine.ini" in files:
        score += 30

    if "suspensions.ini" in files:
        score += 30

    if "drivetrain.ini" in files:
        score += 30

    if "tyres.ini" in files:
        score += 30

    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(kn5_count * 25, 100)

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
            os.path.join(folder, f)
        )
    }

    if "ui_track.json" in files:
        score += 150

    if "models.ini" in files:
        score += 100

    if "surfaces.ini" in files:
        score += 50

    if "map.ini" in files:
        score += 30

    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(kn5_count * 25, 100)

    return score


# ============================================================
# CSP / EXTENSION DETECTION
# ============================================================

def score_csp_folder(folder):

    score = 0

    files = {
        f.lower()
        for f in os.listdir(folder)
        if os.path.isfile(
            os.path.join(folder, f)
        )
    }

    dirs = {
        d.lower()
        for d in os.listdir(folder)
        if os.path.isdir(
            os.path.join(folder, d)
        )
    }

    if "extension" in dirs:
        score += 200

    if "ext_config.ini" in files:
        score += 100

    if "config" in dirs:
        score += 30

    if "lua" in dirs:
        score += 30

    if "shaders" in dirs:
        score += 30

    return score


# ============================================================
# DETECT MOD
# ============================================================

def find_mod_root(extracted_folder):

    car_candidates = []
    track_candidates = []
    csp_candidates = []


    for root, dirs, files in os.walk(
        extracted_folder
    ):

        car_score = score_car_folder(root)
        track_score = score_track_folder(root)
        csp_score = score_csp_folder(root)


        if car_score > 0:

            car_candidates.append(
                (car_score, root)
            )


        if track_score > 0:

            track_candidates.append(
                (track_score, root)
            )


        if csp_score > 0:

            csp_candidates.append(
                (csp_score, root)
            )


    # --------------------------------------------------------
    # CAR
    # --------------------------------------------------------

    if car_candidates:

        car_candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return car_candidates[0][1], "cars"


    # --------------------------------------------------------
    # TRACK
    # --------------------------------------------------------

    if track_candidates:

        track_candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return track_candidates[0][1], "tracks"


    # --------------------------------------------------------
    # CSP
    # --------------------------------------------------------

    if csp_candidates:

        csp_candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return csp_candidates[0][1], "csp"


    return None, None


# ============================================================
# FIND CONTENT FOLDER
# ============================================================

def find_directory_recursive(folder, dirname):

    dirname = dirname.lower()

    for root, dirs, files in os.walk(folder):

        for directory in dirs:

            if directory.lower() == dirname:

                return os.path.join(
                    root,
                    directory
                )

    return None


# ============================================================
# AUTO FIX CAR
# ============================================================

def repair_car_structure(car_root):

    fixes = []


    # --------------------------------------------------------
    # Find misplaced UI
    # --------------------------------------------------------

    ui_file = find_file_recursive(
        car_root,
        "ui_car.json"
    )

    if ui_file:

        correct_ui_dir = os.path.join(
            car_root,
            "ui"
        )

        os.makedirs(
            correct_ui_dir,
            exist_ok=True
        )

        correct_ui_file = os.path.join(
            correct_ui_dir,
            "ui_car.json"
        )

        if os.path.abspath(ui_file) != os.path.abspath(correct_ui_file):

            try:

                shutil.copy2(
                    ui_file,
                    correct_ui_file
                )

                fixes.append(
                    "Repaired ui_car.json location"
                )

            except Exception:
                pass


    # --------------------------------------------------------
    # Find misplaced data.acd
    # --------------------------------------------------------

    data_acd = find_file_recursive(
        car_root,
        "data.acd"
    )

    if data_acd:

        correct_data = os.path.join(
            car_root,
            "data.acd"
        )

        if os.path.abspath(data_acd) != os.path.abspath(correct_data):

            try:

                shutil.copy2(
                    data_acd,
                    correct_data
                )

                fixes.append(
                    "Repaired data.acd location"
                )

            except Exception:
                pass


    # --------------------------------------------------------
    # Find misplaced lods.ini
    # --------------------------------------------------------

    lods = find_file_recursive(
        car_root,
        "lods.ini"
    )

    if lods:

        data_folder = os.path.join(
            car_root,
            "data"
        )

        os.makedirs(
            data_folder,
            exist_ok=True
        )

        correct_lods = os.path.join(
            data_folder,
            "lods.ini"
        )

        if os.path.abspath(lods) != os.path.abspath(correct_lods):

            try:

                shutil.copy2(
                    lods,
                    correct_lods
                )

                fixes.append(
                    "Repaired lods.ini location"
                )

            except Exception:
                pass


    return fixes


# ============================================================
# AUTO FIX TRACK
# ============================================================

def repair_track_structure(track_root):

    fixes = []


    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    ui_file = find_file_recursive(
        track_root,
        "ui_track.json"
    )

    if ui_file:

        ui_folder = os.path.join(
            track_root,
            "ui"
        )

        os.makedirs(
            ui_folder,
            exist_ok=True
        )

        correct_ui = os.path.join(
            ui_folder,
            "ui_track.json"
        )

        if os.path.abspath(ui_file) != os.path.abspath(correct_ui):

            try:

                shutil.copy2(
                    ui_file,
                    correct_ui
                )

                fixes.append(
                    "Repaired ui_track.json location"
                )

            except Exception:
                pass


    # --------------------------------------------------------
    # MODELS.INI
    # --------------------------------------------------------

    models_ini = find_file_recursive(
        track_root,
        "models.ini"
    )

    if models_ini:

        correct_models = os.path.join(
            track_root,
            "models.ini"
        )

        if os.path.abspath(models_ini) != os.path.abspath(correct_models):

            try:

                shutil.copy2(
                    models_ini,
                    correct_models
                )

                fixes.append(
                    "Repaired models.ini location"
                )

            except Exception:
                pass


    return fixes


# ============================================================
# CSP INSTALL
# ============================================================

def merge_directories(source, destination):

    os.makedirs(
        destination,
        exist_ok=True
    )


    for item in os.listdir(source):

        source_item = os.path.join(
            source,
            item
        )

        destination_item = os.path.join(
            destination,
            item
        )


        if os.path.isdir(source_item):

            merge_directories(
                source_item,
                destination_item
            )

        else:

            # Never overwrite silently
            # Existing files are replaced with
            # the newer mod version

            shutil.copy2(
                source_item,
                destination_item
            )


# ============================================================
# FIND CSP EXTENSION
# ============================================================

def find_extension_folder(folder):

    for root, dirs, files in os.walk(folder):

        for directory in dirs:

            if directory.lower() == "extension":

                return os.path.join(
                    root,
                    directory
                )

    return None


# ============================================================
# INSTALL CSP
# ============================================================

def install_csp(
    mod_root,
    ac_path
):

    extension_folder = find_extension_folder(
        mod_root
    )


    if not extension_folder:

        # If the selected folder itself is extension

        if os.path.basename(
            mod_root
        ).lower() == "extension":

            extension_folder = mod_root

        else:

            raise Exception(
                "This appears to be a CSP/shader mod, "
                "but no extension folder was found."
            )


    destination = os.path.join(
        ac_path,
        "extension"
    )


    merge_directories(
        extension_folder,
        destination
    )


    return destination


# ============================================================
# VALIDATE CAR
# ============================================================

def validate_car(car_root):

    found = []
    problems = []


    kn5_files = find_files_recursive(
        car_root,
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
        car_root,
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


    lods_file = find_file_recursive(
        car_root,
        "lods.ini"
    )


    data_acd = find_file_recursive(
        car_root,
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

def validate_track(track_root):

    found = []
    problems = []


    kn5_files = find_files_recursive(
        track_root,
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
        track_root,
        "ui_track.json"
    )


    if ui_file:

        found.append(
            "ui_track.json"
        )

    else:

        problems.append(
            "ui_track.json not found"
        )


    models_ini = find_file_recursive(
        track_root,
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
# INSTALL NORMAL MOD
# ============================================================

def install_normal_mod(
    mod_root,
    mod_type,
    ac_path
):

    folder_name = os.path.basename(
        os.path.normpath(
            mod_root
        )
    )


    bad_names = {
        "",
        "content",
        "cars",
        "tracks",
        "extension",
        "assettocorsa"
    }


    if folder_name.lower() in bad_names:

        raise Exception(
            "Could not determine the correct mod folder name."
        )


    destination = os.path.join(
        ac_path,
        "content",
        mod_type,
        folder_name
    )


    if os.path.exists(destination):

        replace = messagebox.askyesno(
            "Mod Already Installed",
            f"{folder_name} already exists.\n\n"
            "Replace the existing installation?"
        )

        if not replace:
            return None


    if os.path.exists(destination):

        shutil.rmtree(
            destination
        )


    shutil.copytree(
        mod_root,
        destination
    )


    return destination


# ============================================================
# MAIN INSTALLER
# ============================================================

def identify_and_install():

    ac_path = get_assetto_corsa_path()


    # --------------------------------------------------------
    # Find AC
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
                "Could not detect this mod.\n\n"
                "The archive does not appear to contain "
                "a supported Assetto Corsa car, track, "
                "or CSP/shader installation."
            )


        # ----------------------------------------------------
        # CSP
        # ----------------------------------------------------

        if mod_type == "csp":

            destination = install_csp(
                mod_root,
                ac_path
            )


            messagebox.showinfo(
                "Installation Complete",
                "CSP/shader files installed successfully!\n\n"
                f"Merged into:\n{destination}"
            )

            return


        # ----------------------------------------------------
        # AUTO REPAIR
        # ----------------------------------------------------

        if mod_type == "cars":

            fixes = repair_car_structure(
                mod_root
            )

            found, problems = validate_car(
                mod_root
            )

        else:

            fixes = repair_track_structure(
                mod_root
            )

            found, problems = validate_track(
                mod_root
            )


        # ----------------------------------------------------
        # Install
        # ----------------------------------------------------

        destination = install_normal_mod(
            mod_root,
            mod_type,
            ac_path
        )


        if destination is None:
            return


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
            f"Name: {os.path.basename(mod_root)}\n"
            f"Location:\n{destination}\n\n"
            "Detected files:\n"
        )


        if found:

            message += "\n".join(
                f"• {item}"
                for item in found
            )

        else:

            message += "None"


        # ----------------------------------------------------
        # Fixes
        # ----------------------------------------------------

        if fixes:

            message += (
                "\n\nAuto fixes applied:\n"
                +
                "\n".join(
                    f"• {fix}"
                    for fix in fixes
                )
            )


        # ----------------------------------------------------
        # Warnings
        # ----------------------------------------------------

        if problems:

            message += (
                "\n\nWarnings:\n"
                +
                "\n".join(
                    f"• {problem}"
                    for problem in problems
                )
            )

        else:

            message += (
                "\n\nNo obvious problems detected."
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
    "500x290"
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
    text="Cars  •  Tracks  •  CSP / Shaders  •  Auto Fix",
    font=(
        "Arial",
        9
    )
)

supported.pack()


root.mainloop()
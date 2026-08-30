import os
import shutil
import tempfile
import threading
import winreg
import json
from tkinter import (
    Tk,
    Frame,
    Label,
    Button,
    Text,
    END,
    DISABLED,
    NORMAL,
    filedialog,
    messagebox
)
from tkinter import ttk


# ============================================================
# AC AUTO-CONTENT V3
# ============================================================

APP_NAME = "AC Auto-Content"
VERSION = "3.0"

TEMP_DIR = os.path.join(
    tempfile.gettempdir(),
    "AC_Auto_Content"
)


# ============================================================
# UI COLORS
# ============================================================

BG = "#101214"
PANEL = "#181B1F"
PANEL_2 = "#20242A"
TEXT = "#F2F4F5"
MUTED = "#9299A1"
GREEN = "#19A463"
GREEN_HOVER = "#21BA70"
RED = "#D94C4C"
YELLOW = "#D7A83E"


# ============================================================
# PATool
# ============================================================

try:
    import patoolib
except ImportError:
    patoolib = None


# ============================================================
# LOGGING
# ============================================================

def log(message):

    try:
        log_box.config(state=NORMAL)

        log_box.insert(
            END,
            message + "\n"
        )

        log_box.see(END)
        log_box.config(state=DISABLED)

        root.update_idletasks()

    except Exception:
        pass


def status(message):

    try:
        status_label.config(text=message)
        root.update_idletasks()

    except Exception:
        pass


def progress(value):

    try:
        progress_bar["value"] = value
        root.update_idletasks()

    except Exception:
        pass


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

                path, _ = winreg.QueryValueEx(
                    key,
                    "InstallLocation"
                )

                if os.path.isdir(path):
                    return path

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

def clean_temp():

    if os.path.exists(TEMP_DIR):

        try:
            shutil.rmtree(TEMP_DIR)

        except Exception:
            pass


# ============================================================
# ARCHIVE EXTRACTION
# ============================================================

def extract_archive(archive, destination):

    if patoolib is None:

        raise Exception(
            "PATool is not installed.\n\n"
            "Open PowerShell and run:\n\n"
            "pip install patool"
        )

    log("Extracting archive...")

    patoolib.extract_archive(
        archive,
        outdir=destination,
        verbosity=-1
    )


# ============================================================
# FILE HELPERS
# ============================================================

def get_files(folder):

    try:

        return {
            f.lower()
            for f in os.listdir(folder)
            if os.path.isfile(
                os.path.join(folder, f)
            )
        }

    except Exception:

        return set()


def get_dirs(folder):

    try:

        return {
            d.lower()
            for d in os.listdir(folder)
            if os.path.isdir(
                os.path.join(folder, d)
            )
        }

    except Exception:

        return set()


def find_file(folder, filename):

    filename = filename.lower()

    for current, dirs, files in os.walk(folder):

        for file in files:

            if file.lower() == filename:

                return os.path.join(
                    current,
                    file
                )

    return None


def find_files(folder, extension):

    results = []

    extension = extension.lower()

    for current, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(extension):

                results.append(
                    os.path.join(
                        current,
                        file
                    )
                )

    return results


# ============================================================
# CAR DETECTION
# ============================================================

def car_score(folder):

    files = get_files(folder)

    score = 0


    if "ui_car.json" in files:
        score += 1000

    if "data.acd" in files:
        score += 600

    if "lods.ini" in files:
        score += 500

    car_files = [
        "car.ini",
        "engine.ini",
        "drivetrain.ini",
        "suspensions.ini",
        "tyres.ini",
        "aero.ini",
        "electronics.ini"
    ]

    for filename in car_files:

        if filename in files:
            score += 80


    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(
        kn5_count * 100,
        400
    )


    return score


# ============================================================
# TRACK DETECTION
# ============================================================

def track_score(folder):

    files = get_files(folder)

    score = 0


    if "ui_track.json" in files:
        score += 1000

    if "models.ini" in files:
        score += 650

    if "surfaces.ini" in files:
        score += 250

    if "map.ini" in files:
        score += 100

    track_files = [
        "lighting.ini",
        "cameras.ini"
    ]

    for filename in track_files:

        if filename in files:
            score += 40


    kn5_count = sum(
        1
        for f in files
        if f.endswith(".kn5")
    )

    score += min(
        kn5_count * 100,
        500
    )


    return score


# ============================================================
# CSP DETECTION
# ============================================================

def csp_score(folder):

    files = get_files(folder)
    dirs = get_dirs(folder)

    score = 0


    if "extension" in dirs:
        score += 1500

    if "ext_config.ini" in files:
        score += 500

    if "lua" in dirs:
        score += 150

    if "shaders" in dirs:
        score += 150

    if "config" in dirs:
        score += 150

    if "weather" in dirs:
        score += 100

    if "ppfilters" in dirs:
        score += 100


    return score


# ============================================================
# DETECT MOD
# ============================================================

def detect_mod(extracted):

    candidates = []


    for root, dirs, files in os.walk(extracted):

        cs = car_score(root)
        ts = track_score(root)
        cps = csp_score(root)


        if cs >= 500:

            candidates.append(
                (cs, "cars", root)
            )


        if ts >= 500:

            candidates.append(
                (ts, "tracks", root)
            )


        if cps >= 500:

            candidates.append(
                (cps, "csp", root)
            )


    if not candidates:

        return None, None


    # Strong UI identifiers override weaker guesses

    car_ui = find_file(
        extracted,
        "ui_car.json"
    )

    track_ui = find_file(
        extracted,
        "ui_track.json"
    )


    if car_ui:

        current = os.path.dirname(car_ui)

        if os.path.basename(
            current
        ).lower() == "ui":

            current = os.path.dirname(current)

        return current, "cars"


    if track_ui:

        current = os.path.dirname(track_ui)

        if os.path.basename(
            current
        ).lower() == "ui":

            current = os.path.dirname(current)

        return current, "tracks"


    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return (
        candidates[0][2],
        candidates[0][1]
    )


# ============================================================
# UNWRAP ASSETTO CORSA CONTENT
# ============================================================

def unwrap_content_root(folder, mod_type):

    current = folder

    for _ in range(10):

        children = []

        try:

            children = os.listdir(current)

        except Exception:

            break


        # Look for a content folder

        content_path = os.path.join(
            current,
            "content"
        )

        if os.path.isdir(content_path):

            type_path = os.path.join(
                content_path,
                mod_type
            )

            if os.path.isdir(type_path):

                subfolders = [
                    d
                    for d in os.listdir(type_path)
                    if os.path.isdir(
                        os.path.join(
                            type_path,
                            d
                        )
                    )
                ]

                if subfolders:

                    # Pick the strongest candidate

                    best = None
                    best_score = -1

                    for subfolder in subfolders:

                        candidate = os.path.join(
                            type_path,
                            subfolder
                        )

                        score = (
                            car_score(candidate)
                            if mod_type == "cars"
                            else track_score(candidate)
                        )

                        if score > best_score:

                            best_score = score
                            best = candidate

                    if best:
                        return best


        # Direct nested mod folder

        directories = [
            d
            for d in children
            if os.path.isdir(
                os.path.join(current, d)
            )
        ]


        if len(directories) != 1:
            break


        candidate = os.path.join(
            current,
            directories[0]
        )


        if mod_type == "cars":

            if car_score(candidate) > car_score(current):

                current = candidate
                continue


        else:

            if track_score(candidate) > track_score(current):

                current = candidate
                continue


        break


    return current


# ============================================================
# SAFE COPY
# ============================================================

def copy_file_safe(source, destination):

    os.makedirs(
        os.path.dirname(destination),
        exist_ok=True
    )

    shutil.copy2(
        source,
        destination
    )


# ============================================================
# CAR AUTO FIX
# ============================================================

def repair_car(folder):

    fixes = []


    # --------------------------------------------------------
    # ui_car.json
    # --------------------------------------------------------

    ui = find_file(
        folder,
        "ui_car.json"
    )


    if ui:

        ui_dir = os.path.join(
            folder,
            "ui"
        )

        target = os.path.join(
            ui_dir,
            "ui_car.json"
        )


        if os.path.abspath(ui) != os.path.abspath(target):

            copy_file_safe(
                ui,
                target
            )

            fixes.append(
                "Moved ui_car.json into ui/"
            )


    # --------------------------------------------------------
    # lods.ini
    # --------------------------------------------------------

    lods = find_file(
        folder,
        "lods.ini"
    )


    if lods:

        data_dir = os.path.join(
            folder,
            "data"
        )

        target = os.path.join(
            data_dir,
            "lods.ini"
        )


        if os.path.abspath(lods) != os.path.abspath(target):

            copy_file_safe(
                lods,
                target
            )

            fixes.append(
                "Moved lods.ini into data/"
            )


    # --------------------------------------------------------
    # Validate LOD references
    # --------------------------------------------------------

    lods = find_file(
        folder,
        "lods.ini"
    )


    if lods:

        try:

            with open(
                lods,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                content = file.read()


            referenced = []

            for line in content.splitlines():

                line = line.strip()

                if line.lower().startswith(
                    "file="
                ):

                    value = line.split(
                        "=",
                        1
                    )[1].strip()

                    value = value.replace(
                        "\\",
                        os.sep
                    )

                    referenced.append(
                        value
                    )


            for reference in referenced:

                possible = os.path.join(
                    folder,
                    reference
                )


                if not os.path.isfile(
                    possible
                ):

                    basename = os.path.basename(
                        reference
                    )


                    matches = []

                    for kn5 in find_files(
                        folder,
                        ".kn5"
                    ):

                        if os.path.basename(
                            kn5
                        ).lower() == basename.lower():

                            matches.append(kn5)


                    if matches:

                        relative = os.path.relpath(
                            matches[0],
                            os.path.dirname(lods)
                        )


                        fixes.append(
                            f"Found LOD model: {basename}"
                        )

                    else:

                        fixes.append(
                            f"Warning: LOD model missing: {basename}"
                        )


        except Exception:
            pass


    return fixes


# ============================================================
# TRACK AUTO FIX
# ============================================================

def repair_track(folder):

    fixes = []


    # --------------------------------------------------------
    # ui_track.json
    # --------------------------------------------------------

    ui = find_file(
        folder,
        "ui_track.json"
    )


    if ui:

        ui_dir = os.path.join(
            folder,
            "ui"
        )

        target = os.path.join(
            ui_dir,
            "ui_track.json"
        )


        if os.path.abspath(ui) != os.path.abspath(target):

            copy_file_safe(
                ui,
                target
            )

            fixes.append(
                "Moved ui_track.json into ui/"
            )


    # --------------------------------------------------------
    # models.ini
    # --------------------------------------------------------

    models = find_file(
        folder,
        "models.ini"
    )


    if models:

        target = os.path.join(
            folder,
            "models.ini"
        )


        if os.path.abspath(models) != os.path.abspath(target):

            copy_file_safe(
                models,
                target
            )

            fixes.append(
                "Moved models.ini into track root"
            )


    # --------------------------------------------------------
    # Validate model references
    # --------------------------------------------------------

    models = find_file(
        folder,
        "models.ini"
    )


    if models:

        try:

            with open(
                models,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                content = file.read()


            for line in content.splitlines():

                line = line.strip()


                if line.lower().startswith(
                    "file="
                ):

                    reference = line.split(
                        "=",
                        1
                    )[1].strip()


                    reference = reference.replace(
                        "\\",
                        os.sep
                    )


                    direct = os.path.join(
                        os.path.dirname(models),
                        reference
                    )


                    if not os.path.isfile(
                        direct
                    ):

                        basename = os.path.basename(
                            reference
                        )


                        matches = [
                            x
                            for x in find_files(
                                folder,
                                ".kn5"
                            )
                            if os.path.basename(
                                x
                            ).lower()
                            == basename.lower()
                        ]


                        if matches:

                            fixes.append(
                                f"Found model: {basename}"
                            )

                        else:

                            fixes.append(
                                f"Warning: model missing: {basename}"
                            )


        except Exception:
            pass


    return fixes


# ============================================================
# CSP STRUCTURE FINDER
# ============================================================

def find_extension(folder):

    # Prefer the extension folder closest to root

    candidates = []


    for root, dirs, files in os.walk(folder):

        for directory in dirs:

            if directory.lower() == "extension":

                path = os.path.join(
                    root,
                    directory
                )

                depth = path.count(
                    os.sep
                )

                candidates.append(
                    (depth, path)
                )


    if not candidates:

        return None


    candidates.sort(
        key=lambda x: x[0]
    )


    return candidates[0][1]


# ============================================================
# CSP AUTO FIX
# ============================================================

def repair_csp(source):

    fixes = []


    extension = find_extension(
        source
    )


    if not extension:

        return fixes


    # Fix extension/extension nesting

    while True:

        nested = os.path.join(
            extension,
            "extension"
        )


        if not os.path.isdir(
            nested
        ):

            break


        log(
            "Found nested extension folder"
        )


        # Move nested contents upward

        for item in os.listdir(nested):

            src = os.path.join(
                nested,
                item
            )

            dst = os.path.join(
                extension,
                item
            )


            if os.path.exists(dst):

                if os.path.isdir(src):

                    merge_directories(
                        src,
                        dst
                    )

                else:

                    shutil.copy2(
                        src,
                        dst
                    )

            else:

                shutil.move(
                    src,
                    dst
                )


        try:
            os.rmdir(nested)
        except Exception:
            pass


        fixes.append(
            "Unwrapped nested extension folder"
        )


    # Detect useful CSP folders

    folders = [
        "config",
        "lua",
        "shaders",
        "weather",
        "ppfilters",
        "textures"
    ]


    for folder_name in folders:

        path = os.path.join(
            extension,
            folder_name
        )


        if os.path.isdir(path):

            fixes.append(
                f"Verified extension/{folder_name}"
            )


    # Find configs

    config_files = find_files(
        extension,
        ".ini"
    )


    if config_files:

        fixes.append(
            f"Found {len(config_files)} CSP config file(s)"
        )


    return fixes


# ============================================================
# MERGE DIRECTORIES
# ============================================================

def merge_directories(
    source,
    destination
):

    os.makedirs(
        destination,
        exist_ok=True
    )


    for item in os.listdir(source):

        src = os.path.join(
            source,
            item
        )

        dst = os.path.join(
            destination,
            item
        )


        if os.path.isdir(src):

            merge_directories(
                src,
                dst
            )

        else:

            # CSP mods commonly update existing configs
            # so copy the mod version

            shutil.copy2(
                src,
                dst
            )


# ============================================================
# INSTALL CSP
# ============================================================

def install_csp(
    source,
    ac_path
):

    extension = find_extension(
        source
    )


    if not extension:

        raise Exception(
            "No extension folder was found."
        )


    destination = os.path.join(
        ac_path,
        "extension"
    )


    merge_directories(
        extension,
        destination
    )


    return destination


# ============================================================
# VALIDATION
# ============================================================

def validate_car(folder):

    found = []
    warnings = []


    kn5 = find_files(
        folder,
        ".kn5"
    )


    if kn5:

        found.append(
            f"{len(kn5)} KN5 model(s)"
        )

    else:

        warnings.append(
            "No KN5 model found"
        )


    ui = find_file(
        folder,
        "ui_car.json"
    )


    if ui:

        found.append(
            "ui_car.json"
        )

    else:

        warnings.append(
            "ui_car.json missing"
        )


    lods = find_file(
        folder,
        "lods.ini"
    )


    data = find_file(
        folder,
        "data.acd"
    )


    if lods:

        found.append(
            "lods.ini"
        )

    elif data:

        found.append(
            "data.acd"
        )

    else:

        warnings.append(
            "No lods.ini or data.acd found"
        )


    return found, warnings


def validate_track(folder):

    found = []
    warnings = []


    kn5 = find_files(
        folder,
        ".kn5"
    )


    if kn5:

        found.append(
            f"{len(kn5)} KN5 model(s)"
        )

    else:

        warnings.append(
            "No KN5 model found"
        )


    ui = find_file(
        folder,
        "ui_track.json"
    )


    if ui:

        found.append(
            "ui_track.json"
        )

    else:

        warnings.append(
            "ui_track.json missing"
        )


    models = find_file(
        folder,
        "models.ini"
    )


    if models:

        found.append(
            "models.ini"
        )

    else:

        warnings.append(
            "models.ini missing"
        )


    return found, warnings


# ============================================================
# NORMAL INSTALL
# ============================================================

def install_normal(
    source,
    mod_type,
    ac_path
):

    name = os.path.basename(
        os.path.normpath(source)
    )


    invalid_names = {
        "",
        "content",
        "cars",
        "tracks",
        "extension",
        "assettocorsa",
        "mod",
        "mods"
    }


    if name.lower() in invalid_names:

        raise Exception(
            "Could not determine the real mod name."
        )


    destination = os.path.join(
        ac_path,
        "content",
        mod_type,
        name
    )


    if os.path.exists(destination):

        replace = messagebox.askyesno(
            "Mod Already Installed",
            f"{name} already exists.\n\n"
            "Replace it?"
        )


        if not replace:
            return None


        shutil.rmtree(
            destination
        )


    shutil.copytree(
        source,
        destination
    )


    return destination


# ============================================================
# MAIN INSTALL WORKER
# ============================================================

def install_worker(
    archive,
    ac_path
):

    try:

        status(
            "Preparing..."
        )

        progress(5)


        clean_temp()

        os.makedirs(
            TEMP_DIR,
            exist_ok=True
        )


        # ----------------------------------------------------
        # EXTRACT
        # ----------------------------------------------------

        status(
            "Extracting archive..."
        )

        progress(15)


        extract_archive(
            archive,
            TEMP_DIR
        )


        # ----------------------------------------------------
        # DETECT
        # ----------------------------------------------------

        status(
            "Analyzing mod..."
        )

        progress(30)


        mod_root, mod_type = detect_mod(
            TEMP_DIR
        )


        if not mod_root:

            raise Exception(
                "Could not detect this archive.\n\n"
                "Supported types:\n"
                "• Cars\n"
                "• Tracks\n"
                "• CSP / Shaders"
            )


        log(
            f"Detected type: {mod_type}"
        )


        # ----------------------------------------------------
        # UNWRAP CARS / TRACKS
        # ----------------------------------------------------

        if mod_type in (
            "cars",
            "tracks"
        ):

            mod_root = unwrap_content_root(
                mod_root,
                mod_type
            )


        log(
            f"Mod folder: {mod_root}"
        )


        # ----------------------------------------------------
        # CSP
        # ----------------------------------------------------

        if mod_type == "csp":

            status(
                "Repairing CSP / shaders..."
            )

            progress(50)


            fixes = repair_csp(
                mod_root
            )


            status(
                "Installing CSP / shaders..."
            )

            progress(75)


            destination = install_csp(
                mod_root,
                ac_path
            )


            progress(100)


            status(
                "Complete"
            )


            result = (
                "CSP / shaders installed successfully\n\n"
                f"Merged into:\n{destination}"
            )


            if fixes:

                result += (
                    "\n\nAuto fixes:\n"
                    +
                    "\n".join(
                        f"• {fix}"
                        for fix in fixes
                    )
                )


            messagebox.showinfo(
                "Installation Complete",
                result
            )

            return


        # ----------------------------------------------------
        # CAR
        # ----------------------------------------------------

        if mod_type == "cars":

            status(
                "Repairing car..."
            )

            progress(50)


            fixes = repair_car(
                mod_root
            )


            found, warnings = validate_car(
                mod_root
            )


        # ----------------------------------------------------
        # TRACK
        # ----------------------------------------------------

        else:

            status(
                "Repairing track..."
            )

            progress(50)


            fixes = repair_track(
                mod_root
            )


            found, warnings = validate_track(
                mod_root
            )


        # ----------------------------------------------------
        # INSTALL
        # ----------------------------------------------------

        status(
            "Installing..."
        )

        progress(75)


        destination = install_normal(
            mod_root,
            mod_type,
            ac_path
        )


        if destination is None:

            status(
                "Cancelled"
            )

            return


        progress(100)

        status(
            "Installation complete"
        )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        type_name = (
            "Car"
            if mod_type == "cars"
            else "Track"
        )


        result = (
            f"{type_name} installed successfully\n\n"
            f"Name:\n"
            f"{os.path.basename(mod_root)}\n\n"
            f"Location:\n"
            f"{destination}\n\n"
            "Detected files:\n"
        )


        if found:

            result += "\n".join(
                f"• {item}"
                for item in found
            )

        else:

            result += "None"


        if fixes:

            result += (
                "\n\nAuto fixes:\n"
                +
                "\n".join(
                    f"• {fix}"
                    for fix in fixes
                )
            )


        if warnings:

            result += (
                "\n\nWarnings:\n"
                +
                "\n".join(
                    f"• {warning}"
                    for warning in warnings
                )
            )


        messagebox.showinfo(
            "Installation Complete",
            result
        )


    except Exception as error:

        status(
            "Installation failed"
        )

        progress(0)


        messagebox.showerror(
            "Installation Error",
            str(error)
        )


    finally:

        clean_temp()

        button.config(
            state=NORMAL
        )


# ============================================================
# SELECT ARCHIVE
# ============================================================

def select_mod():

    ac_path = get_assetto_corsa_path()


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


    archive = filedialog.askopenfilename(

        title="Select Assetto Corsa Mod",

        filetypes=[
            (
                "Assetto Corsa Mods",
                "*.zip;*.rar;*.7z"
            ),
            (
                "ZIP",
                "*.zip"
            ),
            (
                "RAR",
                "*.rar"
            ),
            (
                "7Z",
                "*.7z"
            ),
            (
                "All Files",
                "*.*"
            )
        ]
    )


    if not archive:
        return


    log_box.config(
        state=NORMAL
    )

    log_box.delete(
        "1.0",
        END
    )

    log_box.config(
        state=DISABLED
    )


    button.config(
        state=DISABLED
    )


    thread = threading.Thread(
        target=install_worker,
        args=(
            archive,
            ac_path
        ),
        daemon=True
    )


    thread.start()


# ============================================================
# GUI
# ============================================================

root = Tk()

root.title(
    f"{APP_NAME} v{VERSION}"
)

root.geometry(
    "700x610"
)

root.resizable(
    False,
    False
)

root.configure(
    bg=BG
)


# ============================================================
# HEADER
# ============================================================

header = Frame(
    root,
    bg=BG
)

header.pack(
    fill="x",
    padx=35,
    pady=(28, 10)
)


title = Label(
    header,
    text="AC Auto-Content",
    bg=BG,
    fg=TEXT,
    font=(
        "Segoe UI",
        25,
        "bold"
    )
)

title.pack(
    anchor="w"
)


subtitle = Label(
    header,
    text="Automatic Assetto Corsa mod installer",
    bg=BG,
    fg=MUTED,
    font=(
        "Segoe UI",
        10
    )
)

subtitle.pack(
    anchor="w",
    pady=(4, 0)
)


# ============================================================
# MAIN PANEL
# ============================================================

panel = Frame(
    root,
    bg=PANEL
)

panel.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=15
)


# ============================================================
# SUPPORTED TYPES
# ============================================================

supported = Label(
    panel,
    text="CARS    •    TRACKS    •    CSP    •    SHADERS",
    bg=PANEL,
    fg=GREEN,
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)

supported.pack(
    pady=(25, 12)
)


# ============================================================
# DESCRIPTION
# ============================================================

description = Label(
    panel,
    text=(
        "Automatically detects, repairs and installs "
        "Assetto Corsa content"
    ),
    bg=PANEL,
    fg=MUTED,
    font=(
        "Segoe UI",
        9
    )
)

description.pack(
    pady=(0, 20)
)


# ============================================================
# BUTTON
# ============================================================

button = Button(
    panel,
    text="SELECT MOD ARCHIVE",
    command=select_mod,
    bg=GREEN,
    fg="white",
    activebackground=GREEN_HOVER,
    activeforeground="white",
    relief="flat",
    borderwidth=0,
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    padx=45,
    pady=14,
    cursor="hand2"
)

button.pack(
    pady=(0, 20)
)


# ============================================================
# STATUS
# ============================================================

status_label = Label(
    panel,
    text="Ready",
    bg=PANEL,
    fg=MUTED,
    font=(
        "Segoe UI",
        9
    )
)

status_label.pack(
    pady=(0, 8)
)


# ============================================================
# PROGRESS
# ============================================================

style = ttk.Style()

try:

    style.theme_use(
        "clam"
    )

except Exception:
    pass


style.configure(
    "AC.Horizontal.TProgressbar",
    troughcolor=PANEL_2,
    background=GREEN,
    bordercolor=PANEL_2,
    lightcolor=GREEN,
    darkcolor=GREEN
)


progress_bar = ttk.Progressbar(
    panel,
    style="AC.Horizontal.TProgressbar",
    orient="horizontal",
    length=560,
    mode="determinate"
)

progress_bar.pack(
    pady=(0, 22)
)


# ============================================================
# LOG
# ============================================================

log_title = Label(
    panel,
    text="INSTALLATION LOG",
    bg=PANEL,
    fg=MUTED,
    font=(
        "Segoe UI",
        8,
        "bold"
    )
)

log_title.pack(
    anchor="w",
    padx=30
)


log_box = Text(
    panel,
    bg="#0B0D0F",
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    borderwidth=0,
    height=11,
    font=(
        "Consolas",
        9
    ),
    padx=12,
    pady=10
)

log_box.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=(6, 22)
)

log_box.config(
    state=DISABLED
)


# ============================================================
# FOOTER
# ============================================================

footer = Label(
    root,
    text=(
        "Automatic detection  •  Auto repair  •  Safe CSP merging"
    ),
    bg=BG,
    fg=MUTED,
    font=(
        "Segoe UI",
        8
    )
)

footer.pack(
    pady=(0, 18)
)


# ============================================================
# START
# ============================================================

root.mainloop()
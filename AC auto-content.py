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
    messagebox,
    StringVar,
    BooleanVar,
    Checkbutton,
    Toplevel,
    colorchooser
)

from tkinter import ttk


# ============================================================
# AC AUTO-CONTENT V4
# ============================================================

APP_NAME = "AC Auto-Content"
VERSION = "4.0"

TEMP_DIR = os.path.join(
    tempfile.gettempdir(),
    "AC_Auto_Content"
)

SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"),
    "AppData",
    "Local",
    "AC_Auto_Content",
    "settings.json"
)


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "theme": "dark",
    "accent": "#19A463",
    "ac_path": "",
    "auto_fix": True,
    "delete_temp": True,
    "show_log": True,
    "always_on_top": False,
    "notifications": True
}


settings = DEFAULT_SETTINGS.copy()


# ============================================================
# COLORS
# ============================================================

DARK = {
    "bg": "#101214",
    "panel": "#181B1F",
    "panel2": "#20242A",
    "text": "#F2F4F5",
    "muted": "#9299A1",
    "entry": "#0B0D0F"
}

LIGHT = {
    "bg": "#F3F4F6",
    "panel": "#FFFFFF",
    "panel2": "#E5E7EB",
    "text": "#111827",
    "muted": "#6B7280",
    "entry": "#F8FAFC"
}


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_settings():

    global settings

    try:

        if os.path.isfile(SETTINGS_FILE):

            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved = json.load(file)

            settings.update(saved)

    except Exception:

        settings = DEFAULT_SETTINGS.copy()


# ============================================================
# SAVE SETTINGS
# ============================================================

def save_settings():

    try:

        os.makedirs(
            os.path.dirname(SETTINGS_FILE),
            exist_ok=True
        )

        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                settings,
                file,
                indent=4
            )

    except Exception:
        pass


load_settings()


# ============================================================
# PATool
# ============================================================

try:
    import patoolib
except ImportError:
    patoolib = None


# ============================================================
# THEME
# ============================================================

def colors():

    if settings["theme"] == "light":
        return LIGHT

    return DARK


def apply_theme():

    c = colors()

    root.configure(
        bg=c["bg"]
    )

    try:

        header.configure(
            bg=c["bg"]
        )

        title.configure(
            bg=c["bg"],
            fg=c["text"]
        )

        subtitle.configure(
            bg=c["bg"],
            fg=c["muted"]
        )

        panel.configure(
            bg=c["panel"]
        )

        supported.configure(
            bg=c["panel"],
            fg=settings["accent"]
        )

        description.configure(
            bg=c["panel"],
            fg=c["muted"]
        )

        status_label.configure(
            bg=c["panel"],
            fg=c["muted"]
        )

        log_title.configure(
            bg=c["panel"],
            fg=c["muted"]
        )

        footer.configure(
            bg=c["bg"],
            fg=c["muted"]
        )

        log_box.configure(
            bg=c["entry"],
            fg=c["text"],
            insertbackground=c["text"]
        )

        button.configure(
            bg=settings["accent"],
            activebackground=settings["accent"]
        )

        customize_button.configure(
            bg=c["panel2"],
            fg=c["text"],
            activebackground=c["panel2"]
        )

    except Exception:
        pass


# ============================================================
# LOGGING
# ============================================================

def log(message):

    if not settings["show_log"]:
        return

    try:

        log_box.config(
            state=NORMAL
        )

        log_box.insert(
            END,
            message + "\n"
        )

        log_box.see(
            END
        )

        log_box.config(
            state=DISABLED
        )

        root.update_idletasks()

    except Exception:
        pass


def status(message):

    try:

        status_label.config(
            text=message
        )

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

    # Custom path first

    custom = settings.get(
        "ac_path",
        ""
    )

    if custom and os.path.isdir(custom):

        return custom


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

    if not settings["delete_temp"]:
        return

    if os.path.exists(TEMP_DIR):

        try:

            shutil.rmtree(
                TEMP_DIR
            )

        except Exception:
            pass


# ============================================================
# ARCHIVE EXTRACTION
# ============================================================

def extract_archive(
    archive,
    destination
):

    if patoolib is None:

        raise Exception(
            "PATool is not installed.\n\n"
            "Open PowerShell and run:\n\n"
            "pip install patool"
        )


    log(
        "Extracting archive..."
    )


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
                os.path.join(
                    folder,
                    f
                )
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
                os.path.join(
                    folder,
                    d
                )
            )
        }

    except Exception:

        return set()


def find_file(
    folder,
    filename
):

    filename = filename.lower()

    for current, dirs, files in os.walk(folder):

        for file in files:

            if file.lower() == filename:

                return os.path.join(
                    current,
                    file
                )

    return None


def find_files(
    folder,
    extension
):

    results = []

    extension = extension.lower()

    for current, dirs, files in os.walk(folder):

        for file in files:

            if file.lower().endswith(
                extension
            ):

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


    for filename in [

        "lighting.ini",
        "cameras.ini"

    ]:

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
# MOD DETECTION
# ============================================================

def detect_mod(
    extracted
):

    car_ui = find_file(
        extracted,
        "ui_car.json"
    )


    if car_ui:

        root_folder = os.path.dirname(
            car_ui
        )

        if os.path.basename(
            root_folder
        ).lower() == "ui":

            root_folder = os.path.dirname(
                root_folder
            )

        return root_folder, "cars"


    track_ui = find_file(
        extracted,
        "ui_track.json"
    )


    if track_ui:

        root_folder = os.path.dirname(
            track_ui
        )

        if os.path.basename(
            root_folder
        ).lower() == "ui":

            root_folder = os.path.dirname(
                root_folder
            )

        return root_folder, "tracks"


    candidates = []


    for root, dirs, files in os.walk(
        extracted
    ):

        cs = car_score(root)

        ts = track_score(root)

        cps = csp_score(root)


        if cs >= 500:

            candidates.append(
                (
                    cs,
                    "cars",
                    root
                )
            )


        if ts >= 500:

            candidates.append(
                (
                    ts,
                    "tracks",
                    root
                )
            )


        if cps >= 500:

            candidates.append(
                (
                    cps,
                    "csp",
                    root
                )
            )


    if not candidates:

        return None, None


    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return (
        candidates[0][2],
        candidates[0][1]
    )


# ============================================================
# UNWRAP CAR / TRACK
# ============================================================

def unwrap_content_root(
    folder,
    mod_type
):

    current = folder


    for _ in range(10):

        children = []

        try:

            children = os.listdir(
                current
            )

        except Exception:

            break


        content_path = os.path.join(
            current,
            "content"
        )


        if os.path.isdir(
            content_path
        ):

            type_path = os.path.join(
                content_path,
                mod_type
            )


            if os.path.isdir(
                type_path
            ):

                candidates = [

                    os.path.join(
                        type_path,
                        d
                    )

                    for d in os.listdir(
                        type_path
                    )

                    if os.path.isdir(
                        os.path.join(
                            type_path,
                            d
                        )
                    )

                ]


                if candidates:

                    candidates.sort(
                        key=lambda x:
                        car_score(x)
                        if mod_type == "cars"
                        else track_score(x),
                        reverse=True
                    )


                    return candidates[0]


        directories = [

            d

            for d in children

            if os.path.isdir(
                os.path.join(
                    current,
                    d
                )
            )

        ]


        if len(directories) != 1:

            break


        candidate = os.path.join(
            current,
            directories[0]
        )


        old_score = (

            car_score(current)

            if mod_type == "cars"

            else track_score(current)

        )


        new_score = (

            car_score(candidate)

            if mod_type == "cars"

            else track_score(candidate)

        )


        if new_score > old_score:

            current = candidate

        else:

            break


    return current


# ============================================================
# SAFE COPY
# ============================================================

def copy_file_safe(
    source,
    destination
):

    os.makedirs(
        os.path.dirname(
            destination
        ),
        exist_ok=True
    )

    shutil.copy2(
        source,
        destination
    )


# ============================================================
# CAR REPAIR
# ============================================================

def repair_car(
    folder
):

    fixes = []


    ui = find_file(
        folder,
        "ui_car.json"
    )


    if ui:

        target = os.path.join(
            folder,
            "ui",
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


    lods = find_file(
        folder,
        "lods.ini"
    )


    if lods:

        target = os.path.join(
            folder,
            "data",
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


    return fixes


# ============================================================
# TRACK REPAIR
# ============================================================

def repair_track(
    folder
):

    fixes = []


    ui = find_file(
        folder,
        "ui_track.json"
    )


    if ui:

        target = os.path.join(
            folder,
            "ui",
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


    return fixes


# ============================================================
# CSP FINDER
# ============================================================

def find_extension(
    folder
):

    candidates = []


    for root, dirs, files in os.walk(
        folder
    ):

        for directory in dirs:

            if directory.lower() == "extension":

                path = os.path.join(
                    root,
                    directory
                )


                candidates.append(
                    (
                        path.count(os.sep),
                        path
                    )
                )


    if not candidates:

        return None


    candidates.sort(
        key=lambda x: x[0]
    )


    return candidates[0][1]


# ============================================================
# CSP REPAIR
# ============================================================

def merge_directories(
    source,
    destination
):

    os.makedirs(
        destination,
        exist_ok=True
    )


    for item in os.listdir(
        source
    ):

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

            shutil.copy2(
                src,
                dst
            )


def repair_csp(
    folder
):

    fixes = []


    extension = find_extension(
        folder
    )


    if not extension:

        return fixes


    while True:

        nested = os.path.join(
            extension,
            "extension"
        )


        if not os.path.isdir(
            nested
        ):

            break


        merge_directories(
            nested,
            extension
        )


        try:

            os.rmdir(
                nested
            )

        except Exception:
            pass


        fixes.append(
            "Removed nested extension folder"
        )


    for folder_name in [

        "config",
        "lua",
        "shaders",
        "weather",
        "ppfilters",
        "textures"

    ]:

        path = os.path.join(
            extension,
            folder_name
        )


        if os.path.isdir(path):

            fixes.append(
                f"Verified extension/{folder_name}"
            )


    return fixes


# ============================================================
# CSP INSTALL
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
            "No extension folder found."
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

def validate_car(
    folder
):

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


def validate_track(
    folder
):

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
# INSTALL NORMAL
# ============================================================

def install_normal(
    source,
    mod_type,
    ac_path
):

    name = os.path.basename(
        os.path.normpath(
            source
        )
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
            "Could not determine the mod name."
        )


    destination = os.path.join(
        ac_path,
        "content",
        mod_type,
        name
    )


    if os.path.exists(
        destination
    ):

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
# MAIN WORKER
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


        status(
            "Extracting archive..."
        )

        progress(15)


        extract_archive(
            archive,
            TEMP_DIR
        )


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
                "Cars\n"
                "Tracks\n"
                "CSP / Shaders"
            )


        log(
            f"Detected: {mod_type}"
        )


        if mod_type in (
            "cars",
            "tracks"
        ):

            mod_root = unwrap_content_root(
                mod_root,
                mod_type
            )


        # ====================================================
        # CSP
        # ====================================================

        if mod_type == "csp":

            status(
                "Repairing CSP..."
            )

            progress(50)


            fixes = []


            if settings["auto_fix"]:

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
                f"Installed into:\n{destination}"
            )


            if fixes:

                result += (
                    "\n\nAuto fixes:\n"
                    +
                    "\n".join(
                        f"• {x}"
                        for x in fixes
                    )
                )


            if settings["notifications"]:

                messagebox.showinfo(
                    "Installation Complete",
                    result
                )


            return


        # ====================================================
        # CARS
        # ====================================================

        if mod_type == "cars":

            status(
                "Checking car..."
            )

            progress(50)


            fixes = []


            if settings["auto_fix"]:

                fixes = repair_car(
                    mod_root
                )


            found, warnings = validate_car(
                mod_root
            )


        # ====================================================
        # TRACKS
        # ====================================================

        else:

            status(
                "Checking track..."
            )

            progress(50)


            fixes = []


            if settings["auto_fix"]:

                fixes = repair_track(
                    mod_root
                )


            found, warnings = validate_track(
                mod_root
            )


        # ====================================================
        # INSTALL
        # ====================================================

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
                f"• {x}"
                for x in found
            )

        else:

            result += "None"


        if fixes:

            result += (
                "\n\nAuto fixes:\n"
                +
                "\n".join(
                    f"• {x}"
                    for x in fixes
                )
            )


        if warnings:

            result += (
                "\n\nWarnings:\n"
                +
                "\n".join(
                    f"• {x}"
                    for x in warnings
                )
            )


        if settings["notifications"]:

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
# SELECT MOD
# ============================================================

def select_mod():

    ac_path = get_assetto_corsa_path()


    if not ac_path:

        ac_path = filedialog.askdirectory(
            title="Select Assetto Corsa folder"
        )


        if not ac_path:

            return


        settings["ac_path"] = ac_path

        save_settings()


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
# CUSTOMIZATION WINDOW
# ============================================================

def open_customization():

    window = Toplevel(
        root
    )

    window.title(
        "Customization"
    )

    window.geometry(
        "520x610"
    )

    window.resizable(
        False,
        False
    )

    c = colors()

    window.configure(
        bg=c["bg"]
    )


    # ========================================================
    # HEADER
    # ========================================================

    Label(
        window,
        text="Customization",
        bg=c["bg"],
        fg=c["text"],
        font=(
            "Segoe UI",
            22,
            "bold"
        )
    ).pack(
        anchor="w",
        padx=30,
        pady=(28, 5)
    )


    Label(
        window,
        text="Change how AC Auto-Content looks and behaves",
        bg=c["bg"],
        fg=c["muted"],
        font=(
            "Segoe UI",
            9
        )
    ).pack(
        anchor="w",
        padx=30,
        pady=(0, 25)
    )


    # ========================================================
    # APPEARANCE
    # ========================================================

    appearance = Frame(
        window,
        bg=c["panel"]
    )

    appearance.pack(
        fill="x",
        padx=25,
        pady=8
    )


    Label(
        appearance,
        text="Appearance",
        bg=c["panel"],
        fg=c["text"],
        font=(
            "Segoe UI",
            11,
            "bold"
        )
    ).pack(
        anchor="w",
        padx=18,
        pady=(15, 10)
    )


    theme_var = StringVar(
        value=settings["theme"]
    )


    def change_theme():

        settings["theme"] = theme_var.get()

        save_settings()

        apply_theme()

        window.destroy()

        open_customization()


    ttk.Radiobutton(
        appearance,
        text="Dark mode",
        variable=theme_var,
        value="dark",
        command=change_theme
    ).pack(
        anchor="w",
        padx=18,
        pady=4
    )


    ttk.Radiobutton(
        appearance,
        text="Light mode",
        variable=theme_var,
        value="light",
        command=change_theme
    ).pack(
        anchor="w",
        padx=18,
        pady=(4, 18)
    )


    # ========================================================
    # ACCENT
    # ========================================================

    accent_frame = Frame(
        window,
        bg=c["panel"]
    )

    accent_frame.pack(
        fill="x",
        padx=25,
        pady=8
    )


    Label(
        accent_frame,
        text="Accent Color",
        bg=c["panel"],
        fg=c["text"],
        font=(
            "Segoe UI",
            11,
            "bold"
        )
    ).pack(
        anchor="w",
        padx=18,
        pady=(15, 10)
    )


    Label(
        accent_frame,
        text="Change the main app color",
        bg=c["panel"],
        fg=c["muted"]
    ).pack(
        anchor="w",
        padx=18
    )


    def choose_color():

        chosen = colorchooser.askcolor(
            color=settings["accent"],
            title="Choose accent color"
        )


        if chosen[1]:

            settings["accent"] = chosen[1]

            save_settings()

            apply_theme()

            window.destroy()

            open_customization()


    Button(
        accent_frame,
        text="Choose Accent Color",
        command=choose_color,
        bg=settings["accent"],
        fg="white",
        relief="flat",
        padx=20,
        pady=9,
        cursor="hand2"
    ).pack(
        anchor="w",
        padx=18,
        pady=12
    )


    # ========================================================
    # OPTIONS
    # ========================================================

    options = Frame(
        window,
        bg=c["panel"]
    )

    options.pack(
        fill="x",
        padx=25,
        pady=8
    )


    Label(
        options,
        text="Installer",
        bg=c["panel"],
        fg=c["text"],
        font=(
            "Segoe UI",
            11,
            "bold"
        )
    ).pack(
        anchor="w",
        padx=18,
        pady=(15, 10)
    )


    auto_fix_var = BooleanVar(
        value=settings["auto_fix"]
    )

    temp_var = BooleanVar(
        value=settings["delete_temp"]
    )

    log_var = BooleanVar(
        value=settings["show_log"]
    )

    top_var = BooleanVar(
        value=settings["always_on_top"]
    )

    notification_var = BooleanVar(
        value=settings["notifications"]
    )


    def save_options():

        settings["auto_fix"] = auto_fix_var.get()

        settings["delete_temp"] = temp_var.get()

        settings["show_log"] = log_var.get()

        settings["always_on_top"] = top_var.get()

        settings["notifications"] = notification_var.get()

        save_settings()

        root.attributes(
            "-topmost",
            settings["always_on_top"]
        )

        apply_theme()

        window.destroy()


    options_list = [

        (
            auto_fix_var,
            "Automatically repair broken mod structures"
        ),

        (
            temp_var,
            "Delete temporary extracted files"
        ),

        (
            log_var,
            "Show installation log"
        ),

        (
            top_var,
            "Keep AC Auto-Content always on top"
        ),

        (
            notification_var,
            "Show installation notifications"
        )

    ]


    for variable, text in options_list:

        Checkbutton(
            options,
            text=text,
            variable=variable,
            bg=c["panel"],
            fg=c["text"],
            activebackground=c["panel"],
            activeforeground=c["text"],
            selectcolor=c["panel2"],
            font=(
                "Segoe UI",
                9
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=4
        )


    Button(
        window,
        text="SAVE SETTINGS",
        command=save_options,
        bg=settings["accent"],
        fg="white",
        activebackground=settings["accent"],
        relief="flat",
        borderwidth=0,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        padx=35,
        pady=11,
        cursor="hand2"
    ).pack(
        pady=20
    )


# ============================================================
# MAIN GUI
# ============================================================

root = Tk()

root.title(
    f"{APP_NAME} v{VERSION}"
)

root.geometry(
    "700x650"
)

root.resizable(
    False,
    False
)

root.attributes(
    "-topmost",
    settings["always_on_top"]
)


# ============================================================
# HEADER
# ============================================================

header = Frame(
    root
)

header.pack(
    fill="x",
    padx=35,
    pady=(28, 10)
)


title = Label(
    header,
    text="AC Auto-Content",
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
# CUSTOMIZATION BUTTON
# ============================================================

customize_button = Button(
    root,
    text="⚙  Customization",
    command=open_customization,
    relief="flat",
    borderwidth=0,
    font=(
        "Segoe UI",
        9,
        "bold"
    ),
    padx=15,
    pady=7,
    cursor="hand2"
)

customize_button.place(
    x=525,
    y=32
)


# ============================================================
# MAIN PANEL
# ============================================================

panel = Frame(
    root
)

panel.pack(
    fill="both",
    expand=True,
    padx=35,
    pady=15
)


supported = Label(
    panel,
    text="CARS    •    TRACKS    •    CSP    •    SHADERS",
    font=(
        "Segoe UI",
        10,
        "bold"
    )
)

supported.pack(
    pady=(25, 12)
)


description = Label(
    panel,
    text=(
        "Automatically detects, repairs and installs "
        "Assetto Corsa content"
    ),
    font=(
        "Segoe UI",
        9
    )
)

description.pack(
    pady=(0, 20)
)


button = Button(
    panel,
    text="SELECT MOD ARCHIVE",
    command=select_mod,
    fg="white",
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


status_label = Label(
    panel,
    text="Ready",
    font=(
        "Segoe UI",
        9
    )
)

status_label.pack(
    pady=(0, 8)
)


style = ttk.Style()

try:

    style.theme_use(
        "clam"
    )

except Exception:
    pass


style.configure(
    "AC.Horizontal.TProgressbar",
    troughcolor=DARK["panel2"],
    background=settings["accent"],
    bordercolor=DARK["panel2"],
    lightcolor=settings["accent"],
    darkcolor=settings["accent"]
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


log_title = Label(
    panel,
    text="INSTALLATION LOG",
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


footer = Label(
    root,
    text=(
        f"{APP_NAME} v{VERSION}  •  Auto detection  •  Auto repair"
    ),
    font=(
        "Segoe UI",
        8
    )
)

footer.pack(
    pady=(0, 18)
)


# ============================================================
# APPLY INITIAL THEME
# ============================================================

apply_theme()


# ============================================================
# START
# ============================================================

root.mainloop()
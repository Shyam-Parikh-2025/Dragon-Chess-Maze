def install():
    import subprocess
    import sys
    import importlib
    go_ahead_for_game = True
    packages = {
        "pygame": "pygame",
        "numba": "numba",
        "numpy": "numpy",
        "moderngl": "moderngl",
        "pyrr": "pyrr",
        "moderngl_window": "moderngl-window"
    }
    for module_name, pip_name in packages.items():
        try:
            importlib.import_module(module_name)
        except:
            go_ahead_for_game = False
    if go_ahead_for_game:
        print("Hello, as you have all libraries installed for the game, the game will proceed.")
    if not go_ahead_for_game:
        starter_text = f"""Greetings:
There are several libraries required for this project to run successfully.
If you wish, the packages can be installed right now (if they are not already).
You have to allow this to run the project, but you will be give the choice below.
Here are the libraries needed: \n{"\n".join([f"-{package}" for package in packages.keys()])}."""
        print(starter_text)
        choice = str(input("Type no to stop else it will run, or press enter/anything else to continue: ")).strip().lower()
        if choice == "no":
            sys.exit()

        for module_name, pip_name in packages.items():
            try:
                importlib.import_module(module_name)
                print(f"{pip_name} already installed")
            except ImportError:
                print(f"Installing {pip_name}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

        print("All required libraries are installed.")


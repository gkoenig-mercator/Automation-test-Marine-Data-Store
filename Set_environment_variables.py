import os

defaults = {
    "DATABASE_USERNAME": "default_user",
    "DATABASE_PASSWORD": "default_pass",
    "DATABASE_URL": "localhost",
    "DATABASE_NAME": "defaultdb",
}

def set_env_var():
    for var, default in defaults.items():
        value = os.environ.get(var)
        if value is None:
            inp = input(f"The {var} variable is not defined. Enter a value or press enter to use the default ({default}.'): ").strip()
            if inp == "":
                inp = default
                os.environ[var] = inp
                print(f"{var} is defined qs '{inp}'")
        else:
            print(f"{var} is already defined: '{value}'")

if __name__ == "__main__":
    set_env_var()
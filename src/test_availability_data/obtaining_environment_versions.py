import platform
import distro
import importlib.metadata

def get_linux_version():
    try:
        return f"{distro.name()} {distro.version()} ({distro.codename()})"
    except Exception:
        return platform.platform()


def get_toolbox_version():
    try:
        return importlib.metadata.version("copernicusmarine")
    except importlib.metadata.PackageNotFoundError:
        return "not installed"


def get_versions():
    return {
        "linux_version": get_linux_version(),
        "script_version": "0.1.0",
        "toolbox_version": get_toolbox_version(),
    }

if __name__ == "__main__":
    versions = get_versions()
    print(versions)
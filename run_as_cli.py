"""
Run Locust using system commands.
"""


import subprocess


def run(settings):
    cmd = (
        f"locust --headless --host {settings['base_url']} "
        f"-u {settings['users']} -r {settings['users']}"
    )
    if not settings["worker"]:
        cmd += f" --run-time {settings['duration']}"
    if settings["master"]:
        cmd += f" --master --expect-workers={settings['expect-workers']}"
    if settings["worker"]:
        cmd += f" --worker --master-host={settings['master-host']}"
    cmd += f" -f main.py {settings['persona_arg']}"
    subprocess.run(cmd.split(" "))

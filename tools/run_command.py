import subprocess


def run_command(command:str,folder):
    parts = command.split()
    result = subprocess.run(
        parts,
        cwd = f"projects/{folder}",
        capture_output = True,
        text = True
    )
    return [result.stdout, result.stderr]


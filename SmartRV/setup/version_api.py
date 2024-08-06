''' This api can be run from the setup dir or the main SmartRV dir to edit the individual package version and update yaml when commanded.'''


from fastapi import FastAPI, Form, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
import subprocess

app = FastAPI()

# Define the path to the Python file
python_file_path = "main_service/wgo_main_service.py"



# Define the list of Python file paths
python_file_paths = [
    "main_service/wgo_main_service.py",
    "iot_service/wgo_iot_service.py",
    "can_service/wgo_can_service.py",
    "bt_service/wgo_bt_service.py",
    "common_libs/wgo_common_libs.py",
    "hmi_tools/wgo_hmi_tools.py",
    "data/wgo_data.py",
    "update_service/wgo_update_service.py"
]


@app.post("/update-yml",  response_class=HTMLResponse)
def run_script(Increment_FrontEnd: bool = Form(False)):

    command = ["python3", "setup/update_version.py"]

    if Increment_FrontEnd:
        command.append("--Increment_FrontEnd")
    else:
        command.append("--no_frontend_change")

    result = subprocess.run(command, capture_output=True, text=True)

    return """
    <html>
        <body>
            <h2>Update Output</h2>
            <pre>{}</pre>
            <br>
            <a href="/">Back</a>
        </body>
    </html>
    """.format(result.stdout)



# Function to read the version from a Python file
def read_version_from_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.strip().startswith("__version__"):
                version = line.strip().split("=")[-1].strip().strip('"').strip("'")
                return version

# Function to write the new version to a Python file
def write_version_to_file(file_path, new_version):
    with open(file_path, "r") as file:
        lines = file.readlines()
    with open(file_path, "w") as file:
        for line in lines:
            if line.strip().startswith("__version__"):
                line = f'__version__ = "{new_version}"\n'
            file.write(line)

@app.get("/", response_class=HTMLResponse)
def read_form():
    form_html = ""
    for i, file_path in enumerate(python_file_paths, start=1):
        current_version = read_version_from_file(file_path)
        form_html += f"""
            <h2>Editing file: {file_path} Current Version {current_version}</h2>
            <form method="post" action="/update/{i}">
                <label for="new_version_{i}">New Version:</label>
                <input type="text" name="new_version" value="{current_version}">
                <input type="hidden" name="_method" value="put">
                <input type="submit" value="Replace Version">
            </form>
        """

    return f"""
    <html>
    <head>
        <title>WinnConnect Version Editor</title>
    </head>
    <body>
        <h1>WinnConnect Version Editor</h1>
        {form_html}

        <h2>Update Yaml Script</h2>
        <form action="/update-yml" method="post">
            <input type="submit" value="Update version yml.">
            <label for="Increment_FrontEnd">Increment Frontend:</label>
            <input type="checkbox" name="Increment_FrontEnd">
        </form>
    </body>
    </html>
    """

@app.post("/update/{file_id}")
async def update_version(file_id: int, new_version: str = Form(None)):
    if not new_version:
        return {"error": "Invalid version provided"}

    if file_id >= 1 and file_id <= len(python_file_paths):
        write_version_to_file(python_file_paths[file_id - 1], new_version)

    return HTMLResponse(content=f"""
    <html>
    <head>
        <title>Version Status</title>
    </head>
    <body>
        <h1>Version Status</h1>
        <pre>{python_file_paths[file_id - 1]} was updated.</pre>
        <a href="/">Back to Form</a>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


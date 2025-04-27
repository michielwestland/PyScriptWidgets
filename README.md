# PyScriptWidgets

A client side GUI class (widget) library for building web applications with PyScript.

Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

See demo website: [https://michielwestland.github.io/PyScriptWidgets](https://michielwestland.github.io/PyScriptWidgets)
![Demo screenshot](assets/demo-screenshot.png?raw=true "Demo screenshot")

## Thirdparty software

Development:

- PyEnv for Windows: [https://pyenv-win.github.io/pyenv-win](https://pyenv-win.github.io/pyenv-win) (MIT license)
- Python: [https://www.python.org](https://www.python.org) (PSF license agreement)
- VSCode: [https://code.visualstudio.com/docs/python/python-tutorial](https://code.visualstudio.com/docs/python/python-tutorial) (Microsoft product license + MIT license)
- Python vscode extension: [https://marketplace.visualstudio.com/items?itemName=ms-python.python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (Microsoft Pylance license + MIT license)
- PyLint vscode extension: [https://marketplace.visualstudio.com/items?itemName=ms-python.pylint](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) (MIT license)
- Black vscode extension: [https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) (MIT license)
- Live Server vscode extension: [https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) (MIT license)
- Live Preview vscode extension: [https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server) (MIT license)

Runtime:

- PyScript: [https://pyscript.net](https://pyscript.net) (Apache license 2.0)
- Pyodide: [https://pyodide.org](https://pyodide.org) (MPL-2.0 license)
- Fomantic UI: [https://fomantic-ui.com](https://fomantic-ui.com) (MIT license)
- jQuery: [https://jquery.com](https://jquery.com) (MIT license)

Logo:

![Logo](assets/logo.svg)

## Virtual environment

```powershell
python -m venv .venv --upgrade-deps
.venv/Scripts/Activate.ps1
python.exe -m pip install --upgrade pip
```

Set powershell execution policy if needed:

```powershell
Get-ExecutionPolicy -list
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

## Install packages

Only use pure Python packages, with file names ending in ...-py3-none-any.whl

```powershell
pip install pylint
pip install black
```

```powershell
pip freeze > requirements.txt
pip install -r requirements.txt
```

## PyScript documentation

PyScript.net: [https://docs.pyscript.net/2025.3.1/](https://docs.pyscript.net/2025.3.1/)

## Linting and formatting

Create a default pylint configuration

```powershell
pylint --rcfile="" --generate-rcfile > .pylintrc
```

Run linter

```powershell
pylint *.py
```

Run formatter

```powershell
black *.py
```

## Webserver runtime

Standalone:

```powershell
python -m http.server 8000 --bind localhost
http://localhost:8000/index.html
```

Press [F1] or [Ctrl+Shift+P] and type:

```text
>Live Server: Open With Live Server
```

or:

```text
>Live Preview: Start server
```

Live Server:

```text
[Go Live]
http://127.0.0.1:5500/
```

Live Preview:

```text
[Preview]
http://127.0.0.1:3000/index.html
```

## Deployment demo website

Set the variable BASE_URL url in the following file:

- pyscript.toml

Update the contents of this directory in github:

[https://github.com/michielwestland/michielwestland.github.io/tree/main/PyScriptWidgets](https://github.com/michielwestland/michielwestland.github.io/tree/main/PyScriptWidgets)

With these files:

- widgets/*.*
- pyscript.toml
- index.html
- main.py
- todo.py
- assets/data.json
- favicon.ico

When serving `__init__.py` (or generally files that start with underscores) from github pages,
make sure there is an empty file `.nojekyll` in the root directory, to instruct the web server
not to interpret those files, but just serve them statically.

### EOF

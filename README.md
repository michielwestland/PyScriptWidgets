# PyScriptWidgets
A client side GUI class (widget) library for building web applications with PyScript.

Copyright (c) 2025 Michiel Westland
This software is distributed under the terms of the MIT license. See LICENSE.txt

See demo website: https://michielwestland.github.io/PyScriptWidgets
![Demo screenshot](demo-screenshot.png?raw=true "Demo screenshot")


## Thirdparty software
Development:
- PyEnv for Windows: https://pyenv-win.github.io/pyenv-win (MIT license)
- Python: https://www.python.org (PSF license agreement)
- VSCode: https://code.visualstudio.com/docs/python/python-tutorial (Microsoft product license + MIT license)
- Python vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.python (Microsoft Pylance license + MIT license)
- PyLint vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.pylint (MIT license)
- Black vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter (MIT license)
- Live Server vscode extension: https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer (MIT license)
- Live Preview vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server (MIT license)

Runtime:
- PyScript: https://pyscript.net (Apache license 2.0)
- Pyodide: https://pyodide.org/en/stable (MPL-2.0 license)
- Fomantic UI: https://fomantic-ui.com (MIT license)
- jQuery: https://jquery.com (MIT license)

Logo:

![Logo](logo.svg)


## Virtual environment
```
python -m venv .venv --upgrade-deps
.venv/Scripts/Activate.ps1
python.exe -m pip install --upgrade pip
```

Set powershell execution policy if needed:
```
Get-ExecutionPolicy -list
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```


## Install packages
Only use pure Python packages, with file names ending in ...-py3-none-any.whl
```
pip install pylint
pip install black
pip freeze > requirements.txt
pip install -r requirements.txt
```


# PyScript documentation
PyScript.net: https://docs.pyscript.net/2025.3.1/


# Linting and formatting
Create a default pylint configuration
```
pylint --rcfile="" --generate-rcfile > .pylintrc
```

Run linter
```
pylint *.py
```

Run formatter
```
black *.py
```


## Webserver runtime
Standalone:
```
python -m http.server 8000 --bind localhost
http://localhost:8000/index.html
```

Press [F1] or [Ctrl+Shift+P] and type:
```
>Live Server: Open With Live Server
```
or:
```
>Live Preview: Start server
```

Live Server:
```
[Go Live]
http://127.0.0.1:5500/
```

Live Preview:
```
[Preview]
http://127.0.0.1:3000/index.html
```


## Deployment
Set the base url in the following files: (search for the term *base url*)
- index.html
- pyscript.toml
- main.py


*EOF*

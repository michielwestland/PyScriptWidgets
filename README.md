# PyScriptWidgets
Client side GUI class (widget) library for building web applications with PyScript.

See demo website: https://michielwestland.github.io/PyScriptWidgets
![Demo screenshot](demo-screenshot.png?raw=true "Demo screenshot")

## Thirdparty software
Development:
- Python: https://www.python.org (PSF license agreement)
- VSCode: https://code.visualstudio.com/docs/python/python-tutorial (Microsoft product license + MIT license)
- Python vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.python (Microsoft Pylance license + MIT license)
- PyLint vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.pylint (MIT License)
- Live Server vscode extension: https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer (MIT license)
- Live Preview vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server (MIT license)

Runtime:
- PyScript: https://pyscript.net (Apache license 2.0)
- Pyodide: https://pyodide.org/en/stable (MPL-2.0 license)
- Semantic UI: https://semantic-ui.com (MIT license)
- jQuery: https://jquery.com (MIT license)
- Freepik: https://www.freepik.com/free-vector/realistic-blur-background_14212526.htm (Freepik Free license with attribution)

Logo:
![Logo](logo.png?raw=true "Logo")

## Virtual environment
```
python -m venv .venv
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


# PyLint and Black
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

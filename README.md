# PyScriptWidgets
Client side GUI class (widget) library for building web applications with PyScript. 


## Thirdparty software
Development:
- Python: https://www.python.org (PSF license agreement)
- VSCode: https://code.visualstudio.com/docs/python/python-tutorial (Microsoft product license + MIT license)
- Python vscode extension: https://marketplace.visualstudio.com/items?itemName=ms-python.python (Microsoft Pylance license + MIT license)
- LiveServer vscode extension: https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer (MIT license)

Runtime:
- PyScript: https://pyscript.net (Apache license 2.0)
- Pyodide: https://pyodide.org/en/stable (MPL-2.0 license)
- Semantic UI: https://semantic-ui.com (MIT license)
- jQuery: https://jquery.com (MIT license)
- Font Awesome Free [brands, solid]: https://fontawesome.com/license/free (Font Awesome Free license)

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
pip install pyparsing
pip freeze > requirements.txt
pip install -r requirements.txt
```

## Webserver runtime
Standalone:
```
python -m http.server 8000 --bind localhost
http://localhost:8000/index.html
```

LiveServer:
```
[Go Live]
http://127.0.0.1:5500/
```

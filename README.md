# PyScript GUI Classes
Client side GUI class library for building web applications with PyScript


## Thirdparty software
VSCode: https://code.visualstudio.com/docs/python/python-tutorial

Live Server: https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer

PyScript: https://pyscript.net (Apache 2.0 License)

Pyodide: https://pyodide.org/en/stable (MPL-2.0 license)

Semantic UI: https://semantic-ui.com (MIT license)

jQuery: https://jquery.com (MIT license)

Font Awesome Free [brands, solid]: https://fontawesome.com/license/free (Font Awesome Free license)


## Create virtual environment
```
python -m venv venv

venv/Scripts/Activate.ps1

python.exe -m pip install --upgrade pip

pip install -r requirements.txt
```

## Set execution policy if needed
```
Get-ExecutionPolicy -list
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

## Install packages 
```
pip install pyscript

pip freeze > requirements.txt
```

## Standalone server
```
python -m http.server 8000 --bind localhost

http://localhost:8000/
```


## Live Server
```
[Go Live]

http://127.0.0.1:5500/
```

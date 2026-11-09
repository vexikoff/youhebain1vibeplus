# Запуск и сборка

## Запуск из исходников

Нужны Windows и Python 3.14 или новее. Откройте PowerShell в папке проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Для запуска игры после активации окружения используйте `python main.py`.
Сохранение `save.json` создаётся в текущей рабочей папке.

## Сборка EXE через PyInstaller

Активируйте виртуальное окружение и установите PyInstaller отдельно:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install pyinstaller
```

Запустите сборку из корневой папки проекта:

```powershell
python -m PyInstaller --noconfirm --clean "Youhe Bain 1 Others' Circumstances Plus.spec"
```

Результат — папка `dist\Youhe Bain 1 Others' Circumstances` с EXE и необходимыми
файлами. Запускайте `Youhe Bain 1 Others' Circumstances.exe` из этой папки и
распространяйте папку целиком: это сборка типа `onedir`.

Файл спецификации использует `icon.ico` как иконку EXE и включает все WAV-файлы
игры. Музыка и эффекты загружаются из папки ресурсов PyInstaller, поэтому
перемещать их или запускать EXE отдельно от папки сборки нельзя. `save.json`
сохраняется в рабочей папке, откуда запущена игра.

Альтернативная спецификация `main.spec` создаёт `dist\main\main.exe` с теми же
ресурсами и иконкой. Для релизной сборки используйте спецификацию с полным
названием игры.

Если сборку нужно начать заново, удалите только созданные PyInstaller папки
`build` и `dist`, затем повторите команду. Исходники и сохранения проекта при
этом не затрагиваются.

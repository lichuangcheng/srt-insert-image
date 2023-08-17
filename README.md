# srt-insert-image

## 打包
使用nuitka   --standalone
```powershell
nuitka --onefile --enable-plugin=pyside6 --disable-console ./srt-ui.py
```
或
```powershell
python -m nuitka --standalone --disable-console --enable-plugin=pyside6 --remove-output ./srt-ui.py
python -m nuitka --macos-create-app-bundle --disable-console --enable-plugin=pyside6 --remove-output ./srt-ui.py
```

使用pyinstaller
```bash
pyinstaller -F -w srt-ui.py
```
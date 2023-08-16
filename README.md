# srt-insert-image

## 打包
使用nuitka   --standalone
```powershell
nuitka --onefile --enable-plugin=pyside6 --disable-console ./srt-ui.py
```

使用pyinstaller
```bash
pyinstaller -F -w srt-ui.py
```
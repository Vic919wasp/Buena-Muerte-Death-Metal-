with open(r"D:\Proyectos WARP\A webs\Proyecto Fabio Guernica\DESARROLLO\editor\main.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

old = '''    def _new_site(self):
        import subprocess
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nueva_web.py")
        if os.path.exists(script):
            subprocess.Popen([sys.executable, script], cwd=os.path.dirname(os.path.abspath(__file__)))
        else:
            QMessageBox.information(self, "Nuevo sitio", "Ejecut\u00e1 nueva_web.py desde la l\u00ednea de comandos.")'''

new = '''    def _new_site(self):
        import subprocess
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nueva_web.py")
        if os.path.exists(script):
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            try:
                subprocess.Popen([sys.executable, script], cwd=os.path.dirname(os.path.abspath(__file__)), startupinfo=si)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo lanzar el asistente: {e}")
        else:
            QMessageBox.warning(self, "Nuevo sitio", "No se encontr\u00f3 nueva_web.py en el directorio del editor.")'''

if old in content:
    content = content.replace(old, new, 1)
    print("Fixed _new_site")
else:
    print("Pattern not found")

with open(r"D:\Proyectos WARP\A webs\Proyecto Fabio Guernica\DESARROLLO\editor\main.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")

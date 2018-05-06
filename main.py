#!/usr/bin/python3
#-*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog, QLineEdit
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import interfaz
import sys, os, subprocess

app = QApplication(sys.argv)

class Main(QMainWindow, interfaz.Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        #uic.loadUi("interfaz.ui", self)
        self.setupUi(self)

        self.btnLimpiarEjecutable.clicked.connect(self.rtEjecutable.clear)
        self.btnLimpiarIcon.clicked.connect(self.rtIcono.clear)

        self.btnSelectEjectuble.clicked.connect(self.selectEjecutable)
        self.btnSelectIcon.clicked.connect(self.selectIcon)
        self.btnCrearAcceso.clicked.connect(self.crearAcceso)

        self.setWindowTitle("Crear Acceso Directo")
    
    def selectEjecutable(self):
        archivo, a = QFileDialog.getOpenFileName(self, "Seleccione el ejecutable", os.getcwd(),
                                "Ejecutables (*)", options=QFileDialog.Options())

        self.rtEjecutable.setText(archivo)

    def selectIcon(self):
        icono, a = QFileDialog.getOpenFileName(self, "Seleccione el Icono", os.getcwd(),
                                "Iconos (*.png *.ico *.jpg)", options=QFileDialog.Options())

        self.rtIcono.setText(icono)

        if icono:
            pixmap = QPixmap(icono).scaled(64,64, Qt.KeepAspectRatio,Qt.SmoothTransformation )
            self.lblIcon.setPixmap(pixmap)

    
    def crearAcceso(self):
        
        mensaje = QMessageBox(self)

        try:
            HOME = None

            for variable, valor in os.environ.items(): 
                if variable in "HOME":
                    HOME = valor
            
            root = str(HOME)+"/"+str(self.txtTitulo.text()).replace(" ", "_")+".desktop"
            acceso = open(root, 'w')

            acceso.write("[Desktop Entry]\n")
            acceso.write("Name="+str(self.txtTitulo.text())+"\n")
            acceso.write("Comment="+str(self.txtDescripcion.toPlainText())+"\n")
            acceso.write("Exec="+str(self.rtEjecutable.text())+"\n")
            acceso.write("Icon="+str(self.rtIcono.text())+"\n")
            acceso.write("Terminal="+str(bool(self.terminal.checkState())).lower()+"\n")
            acceso.write("Type=Application\n")

            acceso.close()

            res = self.moverAcceso(root)

            if res == 0:
                mensaje = QMessageBox(self)
                mensaje.setIcon(QMessageBox.Information)
                mensaje.setText("Su acceso directo se ha creado exitosamente.")
                mensaje.exec_()
            else:
                mensaje.setIcon(QMessageBox.Warning)
                mensaje.setText("Ha ocurrido un error al crear el acceso directo.")
                mensaje.exec_()

        except Exception as e:
            #print("error: "+str(e))
            mensaje.setIcon(QMessageBox.Warning)
            mensaje.setText("Ha ocurrido un error al crear el acceso directo.")
            mensaje.exec_()


    def moverAcceso(self, root):

        intentos = 1

        out = self.getPwd(root)

        while out != 0 and intentos < 3:
            out = self.getPwd(root, "¡Contraseña Incorrecta!\n\nTe quedan %d intentos\n\n"%(3-intentos))
            intentos+=1
        
        if intentos == 3:
            return 1
        else:
            return 0


    def getPwd(self, root,error_msg=""):

        pwd, okPressed = QInputDialog.getText(self, "Permiso de Administrador", error_msg+"Por favor, ingrese su contraseña\n"+
                                                "para poder crear su acceso directo\n"+
                                                "y agregarlo al cajón de aplicaciones:", QLineEdit.Password, "")
        
        out = os.system('echo '+pwd+' | sudo -S mv '+root+' /usr/share/applications/')

        return int(out)

main = Main()
main.show()

app.exec_()
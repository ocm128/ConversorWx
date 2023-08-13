#!/usr/bin/env python
# -*- coding: utf-8 -*-

# WxConversor.py

# coded by ocm128 |

import glob
import commands
import os
import signal
import time
#import thread  # luego comentar threading
import threading
import wx
#import wx.lib.newevent
from wx.lib.stattext import GenStaticText
from subprocess import *  # Para la class Popen


#-----------------------------------------

# Crea una nueva clase y una funcion manejadora de eventos
#(UpdateGuiEvent, EVT_UPDATE_GUI) = wx.lib.newevent.NewEvent()

#-----------------------------------------



 #Clase Hilo donde se ejecutan los procesos 
class Hilo(threading.Thread):
    
    # Pasamos como parametro la clase WxConversor y la variable de los
    # radiobuttons
    def __init__(self, WxConversor, radioVari):
        threading.Thread.__init__(self)
        self.wxConversor = WxConversor
        self.formatoEle = radioVari
        
        
    def run(self):
        print "SELECTED FORMAT"
        print self.formatoEle
        
        time.sleep(1)
        formato = self.formatoEle
        if formato == 0:
            self.wxConversor.mp3_a_wav()
        elif formato == 1:
            self.wxConversor.wav_a_mp3()
        elif formato == 2:
            self.wxConversor.ogg_a_mp3()
        elif formato == 3:
            self.wxConversor.mp3_a_ogg()	
        elif formato == 4:
            self.wxConversor.wma_a_wav()
        elif formato == 5:
            self.wxConversor.wma_a_mp3() 
            
            


      

# Clase principal donde se definen todos los metodos principales
class WxConversor(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size =(380, 280))
        
        # Algunas variables
        self.etiqueta = ""
        self.radioVari = 0
        self.pidNum = 0
        self.threads = []
        
        # Creamos widgets
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(13)
        self.CreateStatusBar().SetFont(font)
        self.SetStatusText("")
        
        self.createWidgets()
        

    """ Mata el proceso de la shell creado mediante Popen.
        De momento la forma de localizar el numero de proceso creado es un poco
        ruda. Generalmente el numero de proceso es una unidad mas que el id de
        proceso asignado cuando se ejecuta Popen. Asi, si el id asignado al
        proceso Popen es por ejemplo 1342, el id asignado al proceso llamado
        dentro de Popen es una unidad mas, 1343. """				
    def stop(self, ev):
        if self.pidNum == 0:
            wx.MessageBox('You must select a dir', 'Info')
        else:	
            #print "Kill process: %s" % self.pidNum 
            #print self.pidNum
            try:
                print "Kill process: %s" % self.pidNum 
                os.kill((self.pidNum + 1), signal.SIGKILL)
                self.stopThreads()
            except Exception:
                print "Exception trying to kill process %s" % (self.pidNum + 1)
                #print self.pidNum + 1
                self.pidNum = 0
                

    def stopThreads(self):
        while self.threads:
            thread = self.threads[0]
            print "Matando Threads....espere %s" % thread
            #print thread
            thread.stop()
            self.threads.remove(thread)

    
    # Metodo donde se llama a la clase Hilo para que ejecute el metodo relativo
    # al formato que se le pasa como parametro.
    def cambiar(self, ev):
        formato = self.radioVari
        try:
            directorio = self.direct  # direct se establece en devuelveDir()
            thread = Hilo(self, formato)
            self.threads.append(thread)
            thread.start()
        except AttributeError:
            wx.MessageBox('You must select a dir', 'Info')


    # Muestra el wx.DirDialog para seleccionar la carpeta de donde se van
    # a procesar los archivos.
    def devuelveDir(self, ev):
        
        # Obtenemos el valor de la variable seleccionada en los radiobuttons
        # para poder anadir la extension requerida.
        if self.radioVari > 5:
            wx.MessageBox('You must select a format', 'Select format')
            return
        else:
            ext = self.radioVari
        if ext == 0 or ext == 3:
            exten = "mp3"
        elif ext == 1:
            exten = "wav"
        elif ext == 2:
            exten = "ogg"
        elif ext == 4 or ext == 5:
            exten = "wma"
        
        carpeta =  wx.DirDialog(self, "Choose a directory:",
                        style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        
        if carpeta.ShowModal() == wx.ID_OK:
            #self.SetStatusText('You selected: %s\n' % carpeta.GetPath())
            self.SetStatusText(carpeta.GetPath())
        carpeta.Destroy()
        if carpeta.GetPath() != '':
            self.direct = carpeta.GetPath()
            print "Into %s " % (self.direct)
            print " "
            print "Changing spaces and cleaning characters "
            print "....."
            print "..."
            os.chdir(self.direct)
            for i in glob.glob(self.direct + '/*.' + exten):
                
                # cambiamos espacios por guiones bajos _
                os.rename(i, self.stripnulls(i))
                time.sleep(0.5)
                
            # Eliminamos caracteres conflictivos y al final renombramos
            # el archivo
            for i in glob.glob(self.direct + '/*.' + exten):
                title = i
                if title.count("("):
                    title = self.limpiaTitle("(", title)
                if title.count(")"):
                    title = self.limpiaTitle(")", title)
                if title.count("'"):
                    title = self.limpiaTitle("'", title)
                if title.count("&"):
                    title = self.limpiaTitle("&", title)
                os.rename(i, title)
            print "Done! "
            
    
    # Convierte de formato mp3 a wav		
    def mp3_a_wav(self):

        # De cada archivo anadido a la lista se extrae el nombre del mismo sin
        # la extension y se transforma al formato elegido.
        for i in glob.glob(self.direct + '/*.mp3'):
            base, extension = os.path.splitext(i)
            comando ="mpg123 -w %s.wav %s" % (base, i)
            p = Popen(comando, shell=True)
            self.pidNum = p.pid
            print "PROCESS NUMBER: %s" % self.pidNum
            #print self.pidNum
            
            # La diferencia entre poll() y exit() es que el primero testea 
            # y sigue, mientras que el segundo espera a que acabe el proceso
            # y entonces devuelve returncode
            
            # Mientras no termine el proceso muestra WAIT
            while p.poll() == None:
                self.etiqueta.SetLabel('   WAIT   ') # 10 chars
            self.etiqueta.SetLabel('FINISHED')
            
    
    # Convierte de formato wav a formato mp3		
    def wav_a_mp3(self):

        for i in glob.glob(self.direct + '/*.wav'):
            base, extension = os.path.splitext(i)
            comando ="lame -b 192 %s %s.mp3" % (i, base)
            p = Popen(comando, shell=True)
            self.pidNum = p.pid
            print "PROCESS NUMBER: %s" % self.pidNum
            #print self.pidNum

            # Mientras no termine el proceso muestra WAIT
            while p.poll() == None:
                self.etiqueta.SetLabel("  WAIT  ")
            self.etiqueta.SetLabel("FINISHED")
            

    # Convierte de formato ogg a mp3
    def ogg_a_mp3(self):
        
        comando = "ogg2mp3 --bitrate=192 -verbose %s" % (self.direct)
        p = Popen(comando, shell=True)
        self.pidNum = p.pid
        print "PROCESS NUMBER: %s" % (self.pidNum)
        #print self.pidNum
        while p.poll() == None:
            self.etiqueta.SetLabel("  WAIT  ")
        self.etiqueta.SetLabel("FINISHED")
        
        
    # Convierte de formato mp3 a ogg
    def mp3_a_ogg(self):

        comando = "mp32ogg --verbose %s" % (self.direct)
        p = Popen(comando, shell=True)
        self.pidNum = p.pid
        print "PROCESS NUMBER %s"  % (self.pidNum)
        #print self.pidNum
        while p.poll() == None:
            self.etiqueta.SetLabel("  WAIT  ")
        self.etiqueta.SetLabel("FINISHED ")
        
    
    # Convierte de formato Wma a wav
    def wma_a_wav(self):
        
        for i in glob.glob(self.direct + '/*.wma'):
            base, extension = os.path.splitext(i)
            comando = "mplayer -vo null -vc dummy -af resample=44100 -ao " 
            "pcm:file=%s.wav %s" % (base, i)
            p = Popen(comando, shell=True)
            self.pidNum = p.pid
            print "PROCESS NUMBER: %s" % self.pidNum
            #print self.pidNum

            # Mientras no termine el proceso muestra ESPERE
            while p.poll() == None:
                self.etiqueta.SetLabel("  WAIT  ")
            self.etiqueta.SetLabel("FINISHED")
            
    
    
    # Convertir de wma a mp3
    def wma_a_mp3(self):
    
        # Primero convierte de wma a wav
        for i in glob.glob(self.direct + '/*.wma'):
            base, extension = os.path.splitext(i)
            comando = "mplayer -vo null -vc dummy -af resample=44100 -ao "
            "pcm:file=%s.wav %s" % (base, i)

            p = Popen(comando, shell=True)
            self.pidNum = p.pid
            print "PROCESS NUMBER: %s" % self.pidNum
            #print self.pidNum
            while p.poll() == None:
                self.etiqueta.SetLabel("  WAIT  ")
                
            # Una vez estan todos en formato wav se pasan a mp3				
            for i in glob.glob(self.direct + '/*.wav'):
                base, extension = os.path.splitext(i)
                comando2 = "lame -b 192 %s %s.mp3" % (i, base)
                p = Popen(comando2, shell=True)
                self.pidNum = p.pid
                print "PROCESS NUMBER: %s" % self.pidNum
                #print self.pidNum
                while p.poll() == None:
                    pass
                #os.system("rm *.wav")
            self.etiqueta.SetLabel("FINISHED")
            
    

    # Elimina los espacios al principio y al final y sustituye los espacios
    # entre palabras por guiones bajos.
    def stripnulls(self, datos):
        return datos.replace(" ", "_").strip()
    
    # Elimina el caracter que pasemos como parametro
    def limpiaTitle(self, car, datos):
        return datos.replace(car, "")
    
    # Borra la etiqueta cada vez que se activa un radioButton diferente.				
    def borraLabel(self):
        self.etiqueta.SetLabel("          ") # 10 esp
            

    def createWidgets(self):
        
        menubar = wx.MenuBar()
        dire = wx.Menu()
        help = wx.Menu()
        
        dire.Append(101, '&Go to', 'Go to Dir')
        dire.Append(102, 'E&xit', 'Exit')
        help.Append(103, '&About', 'About')
        help.Append(104, '&Check', 'Check installed tools')
        
        menubar.Append(dire, '&Dir')
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)
        
        panel = wx.Panel(self, -1)
        sizer = wx.GridBagSizer(0, 0)
        
        radioList = ['mp3 to wav', 'wav to mp3', 'ogg to mp3',
                     'mp3 to ogg', 'wma to wav', 'wma to mp3']
        
        self.radioBox = wx.RadioBox(panel, -1, 'Formato', choices=radioList,
                             majorDimension = 2, style = wx.RA_SPECIFY_ROWS )
    
        sizer.Add(self.radioBox, (1, 0), (1, 3), wx.TOP | wx.LEFT |
                  wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)
        
        wx.EVT_RADIOBOX(panel, -1, self.radioClick)
        
        buttonGo = wx.Button(panel, 1, 'GO', size=(-1, 30))
        buttonGo.SetToolTipString("Empieza el proceso")
        sizer.Add(buttonGo, (3, 0), (1, 1), wx.LEFT, 10)
        
        self.etiqueta = GenStaticText(panel, -1, '  hola  ',(150, 150),
                        style= wx.SIMPLE_BORDER | wx.TE_CENTER)
        self.etiqueta.SetForegroundColour(wx.RED)
        sizer.Add(self.etiqueta, (3, 1), (1, 1), wx.BOTTOM |
                  wx.ALIGN_CENTER_HORIZONTAL, border=20)
        
        buttonStop = wx.Button(panel, 2, 'STOP', size=(-1, 30))
        buttonStop.SetToolTipString("Detiene el proceso")
        sizer.Add(buttonStop, (3, 2), (1, 1), wx.LEFT | wx.RIGHT |
                  wx.ALIGN_RIGHT, border=10)
        
        
        # Events
        self.Bind(wx.EVT_MENU, self.devuelveDir, id=101)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=102)
        self.Bind(wx.EVT_MENU, self.Onhelp, id=103)
        self.Bind(wx.EVT_MENU, self.check, id=104)
        self.Bind(wx.EVT_BUTTON, self.cambiar, id=1)
        self.Bind(wx.EVT_BUTTON, self.stop, id=2)
        
        sizer.AddGrowableCol(1) # Expands the first column
        sizer.Fit(self)
        panel.SetSizer(sizer)
        self.Show(True)
        self.Centre()
        

    def Onhelp(self, ev):
        dialog = wx.MessageDialog(self,
            "\nWxConversor v1.0 \nCoder: ocm128\n"
            "Contact: ocm128@tutamail.com", "About", wx.OK)
        dialog.ShowModal() # Shows it
        dialog.Destroy() # Destroy it when finished.

        
    def OnQuit(self, ev):
        self.Close()
        
    
    def radioClick(self, ev):
        radioIndex = self.radioBox.GetSelection()
        self.radioVari = radioIndex

        
    def check(self, ev):

        lame = commands.getstatusoutput("type lame")
        if lame[0] == 0:
            pass
        elif lame[0] != 0:
            print "You need to install lame program"

        mpg123 = commands.getstatusoutput("type mpg123")
        if mpg123[0] == 0:
            pass
        elif mpg123[0] != 0:
            print "You need to install mpg123 program"

        mp32ogg = commands.getstatusoutput("type mp32ogg")
        if mp32ogg[0] == 0:
            pass
        elif mp32ogg[0] != 0:
            print "You need to install mp32ogg program"

        mplayer = commands.getstatusoutput("type mplayer")
        if mplayer[0] == 0:
            pass
        elif mplayer[0] != 0:
            print "You need to install mplayer program"

        ogg2mp3 = commands.getstatusoutput("type ogg2mp3")
        if ogg2mp3[0] == 0:
            pass
        elif ogg2mp3[0] != 0:
            print "You need to install ogg2mp3 program"



if __name__ == '__main__':
    app = wx.App(0)
    WxConversor(None, -1, "WxConversor v1.0")
    app.MainLoop()
        
        


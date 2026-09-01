import pygame
from tkinter import *
from tkinter import filedialog
import os
import random
import keyboard
import threading
import pystray
from PIL import Image, ImageDraw

pygame.init()
pygame.mixer.init()

playlist = []
playlist_original = []
indice_atual = 0
modo_aleatorio = True

iniciar_pausado = True

PASTA_PADRAO = r"D:\músicas\neuro\Your Favorites"

def carregar_pasta():
    global playlist, playlist_original, indice_atual
    
    pasta = filedialog.askdirectory()
    
    if pasta:
        arquivos = os.listdir(pasta)
        
        playlist = [
            os.path.join(pasta, arquivo)
            for arquivo in arquivos
            if arquivo.endswith(".mp3")
        ]
        
        if playlist:
            playlist_original = playlist.copy()
            
            if modo_aleatorio:
                random.shuffle(playlist)
            
            indice_atual = 0
            tocar_musica()

def carregar_pasta_padrao():
    global playlist, playlist_original, indice_atual
    
    if os.path.exists(PASTA_PADRAO):
        arquivos = os.listdir(PASTA_PADRAO)
        
        playlist = [
            os.path.join(PASTA_PADRAO, arquivo)
            for arquivo in arquivos
            if arquivo.endswith(".mp3")
        ]
        
        if playlist:
            playlist_original = playlist.copy()
            
            if modo_aleatorio:
                random.shuffle(playlist)
            
            indice_atual = 0
            tocar_musica()

def hotkeys():
    keyboard.add_hotkey("ctrl+shift+alt+m", alternar_pause)
    keyboard.add_hotkey("ctrl+shift+alt+k", proxima_musica)

def tocar_musica():
    global iniciar_pausado
    
    if playlist:
        pygame.mixer.music.load(playlist[indice_atual])
        pygame.mixer.music.play()
        
        if iniciar_pausado:
            pygame.mixer.music.pause()
            botao_pause.config(text="Despausar")
            iniciar_pausado = False
        else:
            botao_pause.config(text="Pausar")

def proxima_musica():
    global indice_atual
    if playlist:
        indice_atual = (indice_atual + 1) % len(playlist)
        tocar_musica()

def alternar_pause():
    if botao_pause["text"] == "Pausar":
        pygame.mixer.music.pause()
        botao_pause.config(text="Despausar")
    else:
        pygame.mixer.music.unpause()
        botao_pause.config(text="Pausar")

def parar():
    pygame.mixer.music.stop()

def mudar_volume(valor):
    pygame.mixer.music.set_volume(float(valor) / 100)

def alternar_aleatorio():
    global modo_aleatorio, playlist, playlist_original, indice_atual
    
    if not playlist:
        return
    
    if not modo_aleatorio:
        random.shuffle(playlist)
        modo_aleatorio = True
        botao_aleatorio.config(text="Aleatório: ON")
    else:
        playlist = playlist_original.copy()
        modo_aleatorio = False
        botao_aleatorio.config(text="Aleatório: OFF")
    
    indice_atual = 0
    tocar_musica()

pygame.mixer.music.set_endevent(pygame.USEREVENT)

def checar_fim():
    for evento in pygame.event.get():
        if evento.type == pygame.USEREVENT:
            proxima_musica()
    janela.after(100, checar_fim)

def criar_imagem():
    imagem = Image.new("RGB", (64, 64), "black")
    desenho = ImageDraw.Draw(imagem)
    desenho.rectangle((16, 16, 48, 48), fill="white")
    return imagem

def mostrar_janela(icon, item):
    janela.deiconify()
    icon.stop()

def sair_programa(icon, item):
    icon.stop()
    janela.destroy()

def minimizar_para_tray():
    janela.withdraw()

def iniciar_tray():
    icon = pystray.Icon(
        "MP3 Player",
        criar_imagem(),
        "MP3 Player",
        menu=pystray.Menu(
            pystray.MenuItem("Mostrar", mostrar_janela),
            pystray.MenuItem("Sair", sair_programa)
        )
    )
    icon.run()

threading.Thread(target=iniciar_tray, daemon=True).start()

janela = Tk()
janela.title("MP3 Player")
janela.geometry("300x300")

janela.withdraw()

janela.protocol("WM_DELETE_WINDOW", minimizar_para_tray)

Button(janela, text="Carregar Pasta", command=carregar_pasta).pack(pady=(20, 5))

botao_pause = Button(janela, text="Pausar", command=alternar_pause)
botao_pause.pack(pady=(5))

Button(janela, text="Parar", command=parar).pack(pady=5)
Button(janela, text="Próxima", command=proxima_musica).pack(pady=5)

botao_aleatorio = Button(janela, text="Aleatório: ON", command=alternar_aleatorio)
botao_aleatorio.pack(pady=5)

scale_volume = Scale(
    janela,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    command=mudar_volume
)

scale_volume.set(50)
scale_volume.pack(pady=10)

checar_fim()

carregar_pasta_padrao()

threading.Thread(target=hotkeys, daemon=True).start()

janela.mainloop()
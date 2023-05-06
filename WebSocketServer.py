from concurrent.futures import ThreadPoolExecutor
import websockets
import asyncio
import pyaudio
import wave
import os
import logging

try:
    import serial
except:
    print("ERRORE IMPORT SERIAL")

#################################################################
print("***************************")
print("CREAZIONE OGGETTO PORTA SERIALE -- RIGA 16")
print("***************************")
try:
    arduino = serial.Serial(port='COM6', baudrate=9600, timeout=.1)
    print("***************************")
    print("OGGETTO PORTA SERIALE CREATO -- RIGA 21")
    print("***************************")
except:
    print("\nerrore apertura porta seriale")
#################################################################

logging.basicConfig(level=logging.DEBUG)

os.environ['PYTHONASYNCIODEBUG'] = '1'
os.environ['PYTHONDEVMODE'] = '1'

playing = -1

HOST = "192.168.90.250"

PORT = 8484
CHUNK = 1024
MIN_MSG = 0
MAX_MSG = 1000
INIT_MSG = MIN_MSG-1
AUDIO_DIR = "D:\\GitHub\\TED\\server\\audio\\"
audio = [AUDIO_DIR + "1_TRATTURI.wav",
        AUDIO_DIR + "2_CIVITA.wav",
        AUDIO_DIR + "3_ALTILIA.wav",
        AUDIO_DIR + "4_SANVINCENZO.wav",
        AUDIO_DIR + "5_TINTILIA.wav",
        AUDIO_DIR + "6_CACIOCAVALLO.wav",
        AUDIO_DIR + "7_CARPINONE.wav",
        AUDIO_DIR + "8_MONTEDIMEZZO.wav",
        AUDIO_DIR + "9_WWF.wav"]

class Server():

    def ServerInfo():
        print("Server listening on Port " + str(PORT) + " ip: " + HOST)

    def play(i):
        global playing        
        global stream
        global p
        
        if playing==INIT_MSG:
            print("Playing " + str(i))
            playing = i

            global wf
            global data

            ##################################
            print("***************************")
            print("AVVIO SCRITTURA SU SERIALE 1 -- RIGA 125")
            print("***************************")
            try:
                arduino.write(bytes("1", 'utf-8'))
                print("***************************")
                print("SCRITTURA SU SERIALE ESEGUITA 1 -- RIGA 130")
                print("***************************")
            except:
                print("\nerrore trasmissione")
            ##################################

            if(int(i) <= 60):
                print("***************************")
                print("APERTURA FILE AUDIO -- RIGA 138")
                print("***************************")
                wf = wave.open(audio[int(i)], 'rb')

            # instantiate PyAudio
            p = pyaudio.PyAudio()

            # open stream
            print("***************************")
            print("APERTURA STREAM AUDIO -- RIGA 147")
            print("***************************")
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),   
                            output=True)

            # read data
            print("***************************")
            print("LETTURA DATI AUDIO -- RIGA 156")
            print("***************************")
            data = wf.readframes(CHUNK)

            # play stream
            print("***************************")
            print("RIPRODUZIONE FILE AUDIO -- RIGA 162")
            print("***************************")
            while (len(data) > 0) and (stream.is_active()):
                stream.write(data)
                data = wf.readframes(CHUNK)
            print("***************************")
            print("FINE RIPRODUZIONE FILE AUDIO -- RIGA 168")
            print("***************************")

            # stop stream
            if stream.is_active():

                ##################################
                print("***************************")
                print("AVVIO SCRITTURA SU SERIALE 0 -- RIGA 176")
                print("***************************")
                try:
                    arduino.write(bytes("0", 'utf-8'))
                    print("***************************")
                    print("SCRITTURA SU SERIALE ESEGUITA 0 -- RIGA 181")
                    print("***************************")
                except:
                    print("\n errore trasmissione")
                ##################################

                print("***************************")
                print("STOP AUDIO -- RIGA 188")
                print("***************************")
                stream.stop_stream()
                stream.close()
                # close PyAudio
                p.terminate()
               
            playing=INIT_MSG

        elif playing!=i:  # already playing this audio, ignore it!
            print("Already playing " + str(playing))
            try:
                print("Stop playing " + str(playing))

                ##################################
                print("***************************")
                print("AVVIO SCRITTURA SU SERIALE 0 -- RIGA 205")
                print("***************************")
                try:
                    arduino.write(bytes("0", 'utf-8'))
                    print("***************************")
                    print("SCRITTURA SU SERIALE ESEGUITA 0 -- RIGA 210")
                    print("***************************")
                except:
                    print("\n errore trasmissione")
                ##################################

                print("***************************")
                print("STOP AUDIO GIA' ATTIVO -- RIGA 217")
                print("***************************")
                # stop stream
                if stream.is_active():
                    stream.stop_stream()
                    stream.close()
                
                # close PyAudio
                p.terminate()
                playing=INIT_MSG
                if i != MAX_MSG: #ignore STOP message?
                    Server.play(i)

            except Exception:
                print("Errore PyAudio: " + str(Exception))                




    async def socket(websocket):

        print("A client just connected to the Socket")

        async for message in websocket:
            print("Received message from client: " + message)
            msg = int(message)
            
            if msg >= MIN_MSG and msg <= MAX_MSG:
                try:
                    asyncio.get_event_loop().run_in_executor(None, Server.play, msg)
                except Exception:
                    print("Errore ThreadPoolExecutor: ", Exception)

if __name__ == "__main__":
    Server.ServerInfo()

    start_server = websockets.serve(Server.socket, HOST, PORT)

    print("***************************")
    print("INIZIO INIZIALIZZAZIONE 0 -- RIGA 239")
    print("***************************")
    try:
        arduino.write(bytes("0", 'utf-8'))
        print("***************************")
        print("INIZIALIZZAZIONE ESEGUITA 0 -- RIGA 244")
        print("***************************")
    except:
        print("\nerrore trasmissione")

    asyncio.get_event_loop().set_default_executor(ThreadPoolExecutor())
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
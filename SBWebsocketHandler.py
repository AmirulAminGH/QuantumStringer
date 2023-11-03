import asyncio
import re
import os
import time
from time import sleep
import websockets
import websocketRTV
import time
import re
import serial
from datetime import datetime
from threading import Thread
import random
import threading
import math

#-------import local py env
import SBGlobalVar
import SBGcodeSender
import SBGcodePreProcessor


#localVar for inverse state
XNP="+"
XNN="-"
YNP="+"
YNN="-"
ZNP="+"
ZNN="-"
TNO="M05"
TNC="M03"
# A list to keep track of connected clients
connected_clients = set()

# Function to send a message to all connected clients
async def send_to_all(message):
    # Send the message to all connected clients
    await asyncio.gather(
        *[client.send(message) for client in connected_clients]
    )
def checkInverseState():
    if SBGlobalVar.jog_inverse_x==True:
        XNP = "-"
        XNN = "+"
    if SBGlobalVar.jog_inverse_x==False:
        XNP = "+"
        XNN = "-"
    if SBGlobalVar.jog_inverse_y==True:
        YNP = "-"
        YNN = "+"
    if SBGlobalVar.jog_inverse_y==False:
        YNP = "+"
        YNN = "-"
    if SBGlobalVar.jog_inverse_z==True:
        ZNP = "-"
        ZNN = "+"
    if SBGlobalVar.jog_inverse_z==False:
        ZNP = "+"
        ZNN = "-"
    if SBGlobalVar.tool_inverse==True:
        TNO = "M03"
        TNC = "M05"
    if SBGlobalVar.tool_inverse==False:
        TNO = "M05"
        TNC = "M03"



async def stateUpdate(websocket):
        if SBGlobalVar.move_state== True:
            await websocket.send("#STATE@move_state%true")
        if SBGlobalVar.move_state== False:
            await websocket.send("#STATE@move_state%false")
        await websocket.send("#DATA@jog_distance%{}".format(SBGlobalVar.jog_distance))
        await websocket.send("#DATA@jog_speed%{}".format(SBGlobalVar.jog_speed))
        await websocket.send("#MSG#{}".format(SBGlobalVar.chat_assistance))
        await websocket.send("#DATA@feedratenow%" + str(round((SBGlobalVar.feedrate / 60), 2)))
        await websocket.send("#DATA@feedratemax%" + str(round((SBGlobalVar.maximum_feedrate / 60), 2)))
        await websocket.send("#DATA@feedratemin%" + str(round((SBGlobalVar.minimum_feedrate / 60), 2)))
        await websocket.send("#DATA@bullcounter%" + str(SBGlobalVar.bullseye_current_id))
        await websocket.send("#CSL@log%" + SBGlobalVar.console_log)

async def server(websocket):
    print("websocket started")
    asyncio.create_task(stateUpdate(websocket))
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print("message is {}".format(message))
            if "#CMD" in message:
                if "#BTN" in message:
                    if "run" in message:
                        SBGlobalVar.move_status="run"
                        SBGlobalVar.move_state=True
                        await send_to_all("#STATE@move_state%true")
                    if "stop" in message:
                        SBGlobalVar.move_status="stopped"
                        SBGlobalVar.move_state=False
                        await send_to_all("#STATE@move_state%false")
                    if "pause" in message:
                        SBGlobalVar.move_status="paused"
                        SBGlobalVar.move_state=False
                        await send_to_all("#STATE@move_state%false")
                    if "resume" in message:
                        SBGlobalVar.move_status="resumed"
                        SBGlobalVar.move_state=True
                        await send_to_all("#STATE@move_state%true")
                    if "jog" in message:
                        checkInverseState()
                        print("inverse state checked")
                    if "jogforward" in message:
                        SBGlobalVar.console_outbound="$J=G91 X"+XNP+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "jogreverse" in message:
                        SBGlobalVar.console_outbound="$J=G91 X"+XNN+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "jogright" in message:
                        SBGlobalVar.console_outbound="$J=G91 Y"+YNP+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "jogleft" in message:
                        SBGlobalVar.console_outbound="$J=G91 Y"+YNN+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "jogcw" in message:
                        SBGlobalVar.console_outbound="$J=G91 Z"+ZNP+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "jogccw" in message:
                        SBGlobalVar.console_outbound="$J=G91 Z"+ZNN+str(SBGlobalVar.jog_distance)+"F"+str(SBGlobalVar.jog_speed)+"\n"
                    if "toolup" in message:
                        checkInverseState()
                        SBGlobalVar.tool_active=False
                        SBGlobalVar.console_outbound=TNO+"\n"
                    if "tooldown" in message:
                        checkInverseState()
                        SBGlobalVar.tool_active=True
                        SBGlobalVar.console_outbound=TNC+"\n"

                    if "defaultspeed" in message:
                        if SBGlobalVar.feedrate_change==True:
                            SBGlobalVar.feedrate=SBGlobalVar.feedrate_default
                            await send_to_all("#DATA@feedratenow%"+str(round((SBGlobalVar.feedrate/60),2)))
                    if "speedadd" in message:
                        if SBGlobalVar.feedrate_change == True:
                            localspeed=SBGlobalVar.feedrate
                            localspeed+=float(message.replace("#CMD#BTNspeedadd",""))*60
                            if localspeed>SBGlobalVar.maximum_feedrate:
                                localspeed=SBGlobalVar.maximum_feedrate
                            SBGlobalVar.feedrate=localspeed
                            await send_to_all("#DATA@feedratenow%" + str(round((SBGlobalVar.feedrate / 60), 2)))
                    if "speedminus" in message:
                        if SBGlobalVar.feedrate_change == True:
                            localspeed=SBGlobalVar.feedrate
                            localspeed-=float(message.replace("#CMD#BTNspeedminus",""))*60
                            if localspeed<SBGlobalVar.minimum_feedrate:
                                localspeed=SBGlobalVar.minimum_feedrate
                            SBGlobalVar.feedrate=localspeed
                            await send_to_all("#DATA@feedratenow%" + str(round((SBGlobalVar.feedrate / 60), 2)))
                    if "bullseyenext" in message:
                        if SBGlobalVar.bullseye_enable==True:
                            shiftcount=SBGlobalVar.bullseye_current_id
                            shiftcount+=int(message.replace("#CMD#BTNbullseyenext",""))
                            if shiftcount>SBGlobalVar.bullseye_id_range:
                                shiftcount=SBGlobalVar.bullseye_id_range
                            SBGlobalVar.bullseye_current_id=shiftcount
                            await send_to_all("#DATA@bullcounter%"+str(SBGlobalVar.bullseye_current_id))
                    if "bullseyeprev" in message:
                        if SBGlobalVar.bullseye_enable==True:
                            shiftcount=SBGlobalVar.bullseye_current_id
                            shiftcount-=int(message.replace("#CMD#BTNbullseyeprev",""))
                            if shiftcount<0:
                                shiftcount=0
                            SBGlobalVar.bullseye_current_id=shiftcount
                            await send_to_all("#DATA@bullcounter%"+str(SBGlobalVar.bullseye_current_id))
                if "#CSL%" in message:
                    if SBGlobalVar.console_enable==True:
                        consolemsg=message
                        consolemsg=consolemsg.replace("#CMD#CSL%","")
                        current_time = datetime.now().strftime('[%d/%m/%y@%H:%M:%S]')
                        SBGlobalVar.console_log+= current_time+"<b> IN: </b>"+ consolemsg +"<br>\n"
                        print(consolemsg)
                        if consolemsg.startswith("@") and consolemsg.endswith("@"):
                            returnlog="reply from console master"
                            current_time = datetime.now().strftime('[%d/%m/%y@%H:%M:%S]')
                            SBGlobalVar.console_log += current_time +"<b> OUT: </b>"+returnlog + "<br>\n"
                            #begin local settings manipulation

                        else:
                            SBGlobalVar.console_exchange=True
                            # command to send to grbl

                            returngrbl = "reply from grbl"
                            current_time = datetime.now().strftime('[%d/%m/%y@%H:%M:%S]')
                            SBGlobalVar.console_log += current_time +"<b> OUT: </b>"+ returngrbl + "<br>\n"
                    await send_to_all("#CSL@log%" + SBGlobalVar.console_log)





                if "#VALUE" in message:
                    if "jogspeed" in message:
                        SBGlobalVar.jog_speed=float(message.replace("#CMD#VALUEjogspeed",""))
                        await send_to_all("#DATA@jog_speed%{}".format(SBGlobalVar.jog_speed))
                    if "jogdistance" in message:
                        SBGlobalVar.jog_distance=float(message.replace("#CMD#VALUEjogdistance",""))
                        await send_to_all("#DATA@jog_distance%{}".format(SBGlobalVar.jog_distance))

            if "#MSG" in message:
                patternName = r'@@@(.*?)\$\$\$'
                patternMsg = r'\$\$\$(.*?)$'
                match1 = re.search(patternName, message)
                if match1:
                    uname=match1.group(1)
                match2 = re.search(patternMsg, message)
                if match2:
                    msg=match2.group(1)
                current_time = datetime.now().strftime('[%d/%m/%y@%H:%M:%S]')
                SBGlobalVar.chat_assistance += current_time + " <b>"+uname+"</b> : "+msg +"<br>\n"
                print(SBGlobalVar.chat_assistance)
                await send_to_all("#MSG#{}".format(SBGlobalVar.chat_assistance))




    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove the client from the list of connected clients when they disconnect.
        connected_clients.remove(websocket)



            # time.sleep(3)
        # await websocket.send(f'Got a new MSG FOR YOU: {"updating new message hehehe"}')
start_server = websockets.serve(server,"192.168.42.47",443,max_size= None)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

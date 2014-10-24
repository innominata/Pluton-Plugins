__author__ = 'innominata' # With remover component by CorrosionX
__version__ = "1.1"       # I have a lot more planned

import clr
import System
clr.AddReferenceByPartialName("UnityEngine")
#import UnityEngine
clr.AddReferenceByPartialName("Pluton")
import Pluton
import math
import time
import re
from System import *
from UnityEngine import Vector3
class Claims:
    def dist3d(self,x1,y1,z1,x2,y2,z2):
        dx = (x2 - x1)
        dy = (y2 - y1)
        dz = (z2 - z1)
        return math.sqrt(dx**2 + dy**2 + dz**2)

    def On_LoadingCommands(self):
        Commands.RegisterCommand("claim", "", "Base Claiming Mod")

    def On_PluginInit(self):
        if not Plugin.IniExists("Claims"):
            Plugin.CreateIni("Claims")
            ini = Plugin.GetIni("Claims")
            ini.AddSetting("Config", "ClaimRadius", "25")
            ini.AddSetting("Config", "CooldownMinutes", "2")
            ini.Save()
        ini = Plugin.GetIni("Claims")
        DataStore.Flush("Remove")

    def On_Command(self, cmd):
        command = cmd.cmd
        Player = cmd.User
        args = cmd.args 
        if command == "help":
            Player.Message("THIS SERVER IS RUNNING THE CLAIMS MOD : Type '/claim' for more info")
        if command == "remove":
            if len(args) == 0:
                Player.Message("=-Modified Removed Mod By CorrosionX-=")
                Player.Message("usage: /remove      - Shows the help")
                Player.Message("usage: /remove on   - Turns on instadestroy in your claim")
                Player.Message("usage: /remove off  - Turns it off, or wait 30 seconds")
            if len(args) == 1:
                if args[0] == "on":                 
                        ##__author__ = 'CorrosionX' 
                    DataStore.Add("Remove", cmd.User.SteamID, True)          
                    mydict = Plugin.CreateDict()
                    mydict["gid"] = cmd.User.SteamID
                    Plugin.CreateParallelTimer("removerDeactivator", 60000, mydict).Start()
                    cmd.User.Message("Remove Activated!")
                        ##/_author__ = 'CorrosionX'
                elif args[0] == "off":
                    DataStore.Remove("Remove", cmd.User.SteamID)
                    cmd.User.Message("Remove De-Activated!")
        if command == "claim" or command == "claims":
            if len(args) == 0:
                Player.Message("usage: /claim          - Shows the help")
                Player.Message("usage: /claim stake    - Stakes your claim")
                Player.Message("usage: /claim check    - Checks if you are in a claim")
                Player.Message("usage: /claim near     - Lists Nearby Claims")
                Player.Message("usage: /claim nearest  - Tells you about the nearest claim")
                Player.Message("usage: /claim abandon  - Abandons your claim")
                Player.Message("usage: /claim teleport - Teleports you to your claim")
            elif len(args) == 1:
                param = str(args[0])
                steamid = Player.SteamID
                ini = Plugin.GetIni("Claims")
                if param == "abandon":
                    self.abandon(Player)
                if param == "teleport":
                    self.tpclaim(Player)
                if param == "stake":
                    if self.hasClaim(steamid):
                        Player.Message("You already have a claim.")
                    else:
                        inclaim = self.inClaim(Player.X,Player.Y,Player.Z)
                        if inclaim[0]:
                            Player.Message("You are in "+inclaim[1]+"'s' claim")
                        else:
                            if inclaim[2] <= (inclaim[3] * 2 + 2):
                                Player.Message("You are too close to "+inclaim[1]+"'s' claim, please move "+str((inclaim[3] * 2)+2-inclaim[2])+"m away")
                            else:
                                self.claim(Player)    
                elif param == "check":
                    inclaim = self.inClaim(float(Player.X),float(Player.Y),float(Player.Z))
                    if inclaim[0]:
                        Player.Message("You are in "+inclaim[1]+"'s' claim")
                    else:
                        Player.Message("You are not within a claim")
                elif param == "nearest" or param == "closest":
                    inclaim = self.inClaim(float(Player.X),float(Player.Y),float(Player.Z))
                    if inclaim[0]:
                        Player.Message("You are in "+inclaim[1]+"'s' claim")
                    else:
                        Player.Message("You are closest to "+inclaim[1]+", who is "+str(inclaim[2])+" from your current position")
                elif param == "near" or param == "close":
                    inclaim = self.inClaim(float(Player.X),float(Player.Y),float(Player.Z))
                    Player.Message("The closest claims are : ")
                    Player.Message(inclaim[1]+" who is "+str(inclaim[2])+" meters away")
                    Player.Message(str(inclaim[4][0])+" who is "+str(inclaim[4][1])+" meters away")
                    Player.Message(str(inclaim[5][0])+" who is "+str(inclaim[5][1])+" meters away")

    def inClaim(self,x,y,z):
        s = time.time()
        ini = Plugin.GetIni("Claims")
        claims = ini.EnumSection("Claims")
        count = int(len(claims))
        radius = int(ini.GetSetting('Config', 'ClaimRadius'))
        closest = ['nobody at all...',8000]
        nextclosest = ['nobody at all...',9000]
        otherclosest = ['nobody at all...',10000]
        returnArray = []
        inclaim = False
        for claimID in claims:
            name = self.idToName(claimID)
            claimvectorstring = ini.GetSetting('Claims',claimID)
            claimvector = claimvectorstring.split(",")
            cx = float(claimvector[0])
            cy = float(claimvector[1])
            cz = float(claimvector[2])
            distance = self.dist3d(x,y,z,cx,cy,cz)
            if distance < radius:
                returnArray =  [True, name, distance, claimID,nextclosest,otherclosest]
                inclaim = True
            if distance < closest[1]:
                otherclosest[0] = nextclosest[0]
                otherclosest[1] = nextclosest[1]
                nextclosest[0] = closest[0]
                nextclosest[1] = closest[1]
                closest[1] = int(distance)
                closest[0] = name
            elif distance < nextclosest[1]:
                otherclosest[0] = nextclosest[0]
                otherclosest[1] = nextclosest[1]
                nextclosest[1] = int(distance)
                nextclosest[0] = name
            elif distance < otherclosest[1]:
                otherclosest[1] = int(distance)
                otherclosest[0] = name
        if inclaim:
            return returnArray
        else:
            return [False, closest[0], closest[1],radius,nextclosest,otherclosest]
        

    def hasClaim(self,steamid):
        ini = Plugin.GetIni("Claims")
        if ini.ContainsSetting("Claims",steamid):
            return True
        return False

    def timeDiff(self,t1,t2):
        tickDiff = (t2-t1)
        return tickDiff / 1000

    def claim(self,player):
        ini = Plugin.GetIni("Claims")
        cooldownMinutes = int(ini.GetSetting('Config', 'CooldownMinutes'))
        cooldownStartTicks = ini.GetSetting("Cooldown",player.SteamID)
        if cooldownStartTicks is not None:
            elapsedTime = self.timeDiff(int(cooldownStartTicks),int(System.Environment.TickCount))
            minutesLeft = int(cooldownMinutes - (elapsedTime/60))
            Util.Log(str(minutesLeft))
            if minutesLeft == 1:
                player.Message("You must wait a minute before staking another claim")
            if minutesLeft > 1:
                player.Message("You must wait "+str(minutesLeft)+" minutes before staking another claim")
                return None
            else:
                ini.DeleteSetting("Cooldown",player.SteamID)
        vector = str(player.X) + ',' + str(player.Y) + ',' + str(player.Z)
        ini.AddSetting("Claims",str(player.SteamID),vector) 
        ini.Save()
        player.Message("You have staked your claim. Type '/remove on' to enable instadestroy")

    def abandon(self,player):
        ini = Plugin.GetIni("Claims")
        vector = str(player.X) + ',' + str(player.Y) + ',' + str(player.Z)
        ini.DeleteSetting("Claims",str(player.SteamID)) 
        ini.AddSetting("Cooldown",str(player.SteamID),str(System.Environment.TickCount)) 
        ini.Save()
        player.Message("You have abandoned your claim")

    def idToName(self,steamid):
        ini = Plugin.GetIni("Claims")
        return ini.GetSetting("Players",steamid)

    def On_PlayerConnected(self, player):
        ini = Plugin.GetIni("Claims")
        name = re.sub('[^0-9a-zA-Z .\-=\+_ \[\]]+', '?', player.Name)
        ini.AddSetting("Players",str(player.SteamID),name)
        ini.Save()

    def On_BuildingUpdate(self, be): 
        Player = be.Builder
        inclaim = self.inClaim(Player.X,Player.Y,Player.Z)
        if inclaim[0]: 
            if inclaim[3] != Player.SteamID:
                if be.BuildingPart.buildingBlock.health < 101:
                    Player.Message('You cannot build in '+inclaim[1]+"'s territory")
                    Util.DestroyEntity(be.BuildingPart.buildingBlock)
            else:
                be.BuildingPart.buildingBlock.StopBeingAFrame();
                if (be.BuildingPart.Health <= 500): 
                    be.BuildingPart.Health = 100

    def On_BuildingPartAttacked(self, part):
        ini = Plugin.GetIni("Claims")
        Player = part.Attacker.ToPlayer()
        Player = Server.Players[Player.userID]
        if DataStore.Get("Remove", Player.SteamID) is not None: ##__author__ = 'CorrosionX'
            inclaim = self.inClaim(Player.X,Player.Y,Player.Z)
            if inclaim[0]: 
                if inclaim[3] == Player.SteamID:
                    Util.DestroyEntity(part.Victim.buildingBlock)

        ##__author__ = 'CorrosionX'
    def removerDeactivatorCallback(self, timer):
        mydict = timer.Args
        gid = mydict["gid"]
        DataStore.Remove("Remove", gid)
        timer.Kill()
        ##/_author__ = 'CorrosionX'

    def tpclaim(self,Player):
        ini = Plugin.GetIni("Claims")
        if ini.ContainsSetting("Claims",Player.SteamID):
            vector = ini.GetSetting("Claims",Player.SteamID).split(",")
            cx = float(vector[0])
            cy = float(vector[1])
            cz = float(vector[2])
            Player.Teleport(Vector3(cx,1000,cz))
            Player.Teleport(Vector3(cx,cy,cz))
        else:
            Player.Message("You do not have a claim to teleport to...")
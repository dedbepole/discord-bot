#!/usr/bin/python3
import requests
from discord.ext import commands

TOKEN = "Your Discord token here"
OWNER_ID = 0 # Your user ID here
RTT_USERNAME = "Realtime Trains API username"
RTT_PASSWORD = "Realtime Trains API password"

## BOT SETUP
bot = commands.Bot(command_prefix = ">")
# Comment to respond to messages from anyone
@bot.check
def isOwner(ctx):
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)


## UTILITY FUNCTIONS
def rttDepartures(station):
    rttData = requests.get("https://api.rtt.io/api/v1/json/search/"+station,
                        auth = (RTT_USERNAME, RTT_PASSWORD))
    rttJson = rttData.json()
    rttColour = 0xFF0000
    try:
        rttTitle = ("Departures from **%s**, powered by **Realtime Trains**"
                % rttJson["location"]["name"])
        rttDescription = (" ID  | Time  | Live  | Plat | Destination\n" +
                        "-" * 41 + "\n")
        if rttJson["services"] == None:
            rttDescription = "No services at the moment."
        else:
            for service in rttJson["services"]:
                if len(rttDescription)<1800:
                    try:
                        trainID = service["runningIdentity"]
                    except KeyError:
                        trainID = service["trainIdentity"]
                        
                    depTime = service["locationDetail"]["gbttBookedDeparture"]
                    depTimeFormatted = depTime[:2] + ":" + depTime[2:]
                    
                    try:
                        liveTime = service["locationDetail"]["realtimeDeparture"]
                        liveTimeFormatted = liveTime[:2] + ":" + liveTime[2:]
                    except KeyError:
                        liveTimeFormatted = " N/A "
                        
                    try:
                        # | 10A* |
                        # | 12B  |
                        # | 13   |
                        # | 6    |
                        MAX_PLAT_CHARS = 4
                        platform = service["locationDetail"]["platform"]
                        if service["locationDetail"]["platformChanged"]:
                            platform += "*"
                        if len(platform) < MAX_PLAT_CHARS:
                            platform += " " * (MAX_PLAT_CHARS - len(platform))
                    except KeyError:
                        platform = "----"

                    destination = service["locationDetail"]["destination"][0]["description"]
                    rttDescription += ("%s | %s | %s | %s | %s\n" % 
                                       (trainID, depTimeFormatted, liveTimeFormatted, platform, destination))

    except KeyError:
        rttTitle = "Please give me a valid NRS (3 letters) or TIPLOC (7 characters) code."
        rttDescription = ("It appears that you took a wrong route back at " +
        "Croxley Green Jn, as the rails to this station don't appear to exist " +
        "anymore. Just in case there was meant to be a station here, we've told " +
        "the permanent way team and they'll have a look into it.")

    rttMessage = rttTitle + "\n```" + rttDescription + "```"
    return rttMessage


## COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def logout(ctx):
    await ctx.bot.logout()
    
@bot.command()
async def trains(ctx, station):
    await ctx.send(rttDepartures(station))


bot.run(TOKEN)

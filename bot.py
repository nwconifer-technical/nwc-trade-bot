import discord
from discord.ext import commands
from requests import get
from os import environ
from sys import exit
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

defIntents = discord.Intents.default()
defIntents.message_content = True
defIntents.guilds = True

BASE_API_URL = 'https://api.finance.nwconifer.net'
BASE_SITE_URL = 'https://finance.nwconifer.net'

bot = commands.Bot(command_prefix='/', intents=defIntents)

def buildBookStrings(theDict, orderType):
    if theDict[orderType] == None:
        return "No "+orderType+" Orders"
    else:
        buyString = "Trader\t\tQuantity\t\tPrice Type\t\tPrice\n\n"
        for order in theDict[orderType]:
            newBuyString = order['Sender']+"\t\t"+str(order['Quantity'])+"\t\t"+order['PriceType']+"\t\t$"+str(order['Price'])+"\n\n"
            buyString += newBuyString
        return buyString

@bot.tree.command(name="pingserver", description="Pings the API server")
async def serverping(interaction: discord.Interaction):
    reqRet = get(BASE_API_URL+"/ping")
    if reqRet.status_code != 200:
        await interaction.response.send_message("API Server not responding!")
    else:
        await interaction.response.send_message("API Alive!")

@bot.tree.command(name="allstocks", description="Get a list of all listed tickers and their prices")
async def getallstocks(ctx: commands.Context):
    reqRet = get(BASE_API_URL+"/shares/quote")
    if not reqRet.ok:
        await ctx.send("Data unavailable")
        return
    sendableEmbd = discord.Embed(
        title="All Stocks Listed",
        url=BASE_SITE_URL+"/stocks",
        color=discord.colour.Colour(652800),
    )
    sendableEmbd.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    sendingJS = reqRet.json()
    tickers = ""
    regions = ""
    prices = ""
    for stock in sendingJS['allStocks']:
        tickers += (stock['ticker']+"\n")
        regions += (stock['region']+"\n")
        prices += (str(stock['marketPrice'])+"\n")
    sendableEmbd.add_field(name="Ticker", value=tickers, inline=True)
    sendableEmbd.add_field(name="Region", value=regions, inline=True)
    sendableEmbd.add_field(name="Market Price", value=prices, inline=True)
    
    await ctx.send(embed=sendableEmbd)

@bot.tree.command(name="quote", description="Get info for this ticker")
async def getthisstock(interaction: discord.Interaction, ticker: str):
    reqRet = get(BASE_API_URL+"/shares/quote/"+ticker)
    if not reqRet.ok:
        await interaction.response.send_messagesend("Data Unavailable")
        return
    theDict = reqRet.json()
    sendableEmbed = discord.Embed(
        title=theDict['ticker']+" Information",
        url=BASE_SITE_URL+"/stocks/"+theDict['ticker'],
        color=discord.colour.Colour(652800),
    )
    sendableEmbed.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    sendableEmbed.add_field(name='Ticker',value=theDict['ticker'],inline=True)
    sendableEmbed.add_field(name='Region',value=theDict['region'],inline=True)
    sendableEmbed.add_field(name='Market Price',value='$'+str(theDict['marketPrice']),inline=True)
    sendableEmbed.add_field(name='Market Capitalisation',value='$'+str(theDict['marketCap']),inline=True)
    sendableEmbed.add_field(name='Share Volume',value=theDict['totalVolume'],inline=True)
    await interaction.response.send_message(embed=sendableEmbed)

@bot.tree.command(name="orderbook", description="Get the open orders for a specific ticker")
async def getthisorderbook(interaction: discord.Interaction, ticker: str):
    reqRet = get(BASE_API_URL+'/shares/book/'+ticker)
    if not reqRet.ok:
        interaction.response.send_messagesend('Data Unavailable')
        return
    theDict = reqRet.json()
    curQuote = theDict['CurrentQuote']
    firstEmbed = discord.Embed(
        title=curQuote['ticker']+" Information",
        url=BASE_SITE_URL+"/stocks/"+curQuote['ticker'],
        color=discord.colour.Colour(652800),
    )
    firstEmbed.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    firstEmbed.add_field(name='Ticker',value=curQuote['ticker'],inline=True)
    firstEmbed.add_field(name='Region',value=curQuote['region'],inline=True)
    firstEmbed.add_field(name='Market Price',value='$'+str(curQuote['marketPrice']),inline=True)
    firstEmbed.add_field(name='Market Capitalisation',value='$'+str(curQuote['marketCap']),inline=True)
    firstEmbed.add_field(name='Share Volume',value=curQuote['totalVolume'],inline=True)
    firstEmbed.add_field(name='Book Depth', value=theDict['BookDepth'])
    secondEmbed = discord.Embed(
        title=curQuote['ticker']+" Order Book",
        color=discord.colour.Colour(652800),
    )
    secondEmbed.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    secondEmbed.add_field(name='Buys', value=buildBookStrings(theDict, 'Buys'), inline=False)
    secondEmbed.add_field(name='Sells', value=buildBookStrings(theDict, 'Sells'), inline=False)
    await interaction.response.send_message(embeds=[firstEmbed, secondEmbed])


@bot.tree.command(name="pricehistory", description="Get a week of recent prices for a ticker")
async def recentprices(interaction:discord.Interaction, ticker: str):
    reqRet = get(BASE_API_URL+"/shares/recentprices/"+ticker)
    if not reqRet.ok:
        await interaction.response.send_message("Data Unavailable")
        return
    returnJS = reqRet.json()
    prices = []
    times = []
    thePrices = returnJS['RecentPrice']
    for point in thePrices:
        prices.append(point['LogPrice'])
        times.append(datetime.strptime(point['Timecode'], "%Y-%m-%dT%H:%M:%SZ"))
    dataStream = BytesIO()
    plt.plot(times, prices, color='green', )
    plt.savefig(dataStream, format='png', bbox_inches='tight')
    plt.close()
    dataStream.seek(0)
    chart = discord.File(dataStream,filename=ticker+"PriceGraph.png")
    firstEmbed = discord.Embed(
        title=ticker+" Prices",
        url=BASE_SITE_URL+"/stocks/"+ticker,
        color=discord.colour.Colour(652800),
    )
    firstEmbed.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    firstEmbed.set_image(url="attachment://"+ticker+"PriceGraph.png")
    await interaction.response.send_message(embed=firstEmbed, file=chart)

@bot.tree.command(name="cashbalance", description="Show the user's cash balance")
async def cashbal(interaction: discord.Interaction, user: str):
    reqRet = get(BASE_API_URL+"/cash/quick/"+user)
    if not reqRet.ok:
        await interaction.response.send_message("Data Unavailable")
        return
    retJson = reqRet.json()
    firstEmbed = discord.Embed(
        title=user+" Cash Balance",
        url=BASE_SITE_URL+"/access/login",
        color=discord.colour.Colour(652800),
        description="Cash Balance: $"+str(retJson['CashInHand'])
    )
    firstEmbed.set_author(name='NWC Trade Thing Bot', url=BASE_SITE_URL, icon_url='https://finance.nwconifer.net/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fnwcx_Logo.91bd7b60.png&w=96&q=75')
    await interaction.response.send_message(embed=firstEmbed)

@bot.command(name="sync", description="sync all global commands")
@commands.is_owner()
async def syncslash(interaction: discord.Interaction):
    await bot.tree.sync(discord.Object(interaction.guild.id))
    return

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Ready!")

@bot.event
async def on_guild_join(theGuild: discord.Guild):
    await bot.tree.sync()
    print("Joined New Server")

if __name__ == "__main__":
    token = environ.get("BOT_TOKEN", "YOUR-TOKEN-HERE")
    if token is None:
        exit("Bot token not set")
    else:
        bot.run(token)
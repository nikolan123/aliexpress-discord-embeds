from lxml import etree
import aiohttp
import discord
import time

async def aliinfo(itemid):
    url = f"https://aliexpress.com/item/{itemid}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url) as response:
                html = await response.text()
                response.raise_for_status()
                
    except (aiohttp.ClientError, ValueError) as e:
        print(f"Error fetching data: {e}")
        return {
            "title": "Unknown",
            "image": "",
            "price": "Unknown"
        }
    
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)

    title_tag = tree.xpath("//meta[@property='og:title']")
    title = title_tag[0].get('content').strip(" - AliExpress") if title_tag else 'Unknown'

    image_tag = tree.xpath("//meta[@property='og:image']")
    image = image_tag[0].get('content') if image_tag else 'Unknown'

    try:
        if "|" in title:
            title_parts = title.split("|", 1)
            price = title_parts[0].strip()
            title = title_parts[1].strip()
        else:
            price = "Unknown"
    except IndexError:
        price = "Unknown"

    return {
        "title": title,
        "image": image,
        "price": price
    }

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Aliexpress Discord Embeds is running on {bot.user.name}")

@bot.event
async def on_message(message):
    starttime = time.time()
    async def sendembed(url, starttime):
        itemid = url.split("aliexpress.com/item/")[1].split(".html")[0]
        info = await aliinfo(itemid)
        embed = discord.Embed(color=discord.Color.blue(), title=info['title'], image=info['image'])
        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label="Tracking-less link", url=f"https://aliexpress.com/item/{itemid}.html")
        view.add_item(button)
        timetook = time.time() - starttime
        embed.set_footer(text=f"Price: {info['price']} | took {timetook:.2f} seconds") 
        await message.reply(embed=embed, view=view)
    
    if "aliexpress.com/item/" in message.content:
        await sendembed(message.content, starttime)
    elif "a.aliexpress.com/" in message.content:
        acode = message.content.split("a.aliexpress.com/")[1].split(" ")[0]
        async with aiohttp.ClientSession() as session:
            async with session.head(f"https://a.aliexpress.com/{acode}", allow_redirects=True) as response:
                misterurl = str(response.url)
                await sendembed(misterurl, starttime)

bot.run("")

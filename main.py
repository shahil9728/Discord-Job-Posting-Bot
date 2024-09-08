import discord 
import asyncio
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time 
from discord.ext import commands
from discord import app_commands
import spacy
import csv
from model import lr,vectorizer
import os 
from dotenv import load_dotenv

load_dotenv()
nlp = spacy.load("en_core_web_sm")

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")  # Needed for some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems


discord_url = "https://discord.com/channels/@me"

guild_ids = []
all_channel_ids = {}    
driver = None

intents = discord.Intents.default()
intents.message_content = True
token = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix='/', intents=intents)




def is_job_posting(text):
    doc = nlp(text.lower())
    keywords = ["job", "hiring", "position", "vacancy", "looking for developer", "employment"]
    for token in doc:
        if token.lemma_ in keywords:
            return True
        
    job_seeking_phrases = ["looking for jobs","looking for job", "seeking opportunities", "available for work", "actively looking", "open to job opportunities", "available for hire"]
    
    for phrase in job_seeking_phrases:
        if phrase in text.lower():
            return False

    hiring_phrases = ["looking for", "seeking a", "we are hiring", "join our team", "job available", "open position"]
    for phrase in hiring_phrases:
        if phrase in text.lower():
            return True

    return False
profile_keywords = ["software engineer", "python", "web development", "frontend", "backend","web3 developer","react"]
def matches_profile(text):
    return any(keyword in text.lower() for keyword in profile_keywords)

def add_authorization(driver):
    token = os.getenv("AUTHORIZATION_KEY")
    script = f"""
        const token = "{token}";
        setInterval(() => {{
            document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`;
        }}, 50);
        setTimeout(() => {{
            location.reload();
        }}, 2500);
    """
    driver.execute_script(script)
    time.sleep(5)

async def extract_guild_ids(url,channel):
    if(guild_ids == []):     
        global driver
        if(driver == None):
            driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        add_authorization(driver)
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        print("Scraping the discord server")
        page_source = driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as file:
            file.write(page_source)
        soup = BeautifulSoup(page_source, 'html.parser')
        divs_with_guildsnav = soup.find_all('div',{'data-list-item-id': True})

        for div in divs_with_guildsnav:
            data_list_item_id = div.get('data-list-item-id')
            guild_name = div.get('aria-label')
            if data_list_item_id and data_list_item_id.startswith('guildsnav___'):
                if(data_list_item_id.split('guildsnav___')[1].isdigit()):
                    guild_id = data_list_item_id.split('guildsnav___')[1]
                    guild_ids.append({guild_id:guild_name})
    for guild_id in guild_ids:
        print(f"Extracted Guild ID: {guild_id}")
    print("Total Servers - ",len(guild_ids))
    await channel.send(f"Fetched all the {len(guild_ids)} servers")

async def extract_all_channel_ids(guild_id,channel):
    global driver
    print(list(guild_ids[0].keys())[0])
    print(len(guild_ids))
    for i in range(0,len(guild_ids)):
        if(guild_id == list(guild_ids[i].keys())[0]):
            guild_name = list(guild_ids[i].values())[0]
            break
    if(len(guild_name.split(',')) > 1):
        guild_name = guild_name.split(',')[1].strip()
    await channel.send(f"Extracting all channel IDs of of server {guild_name}")
    if(driver == None):
        driver = webdriver.Chrome(options=chrome_options)
    add_authorization(driver)
    driver.get("https://discord.com/channels/" + guild_id)
    time.sleep(5)
    all_channel_ids[guild_id] = {}
    total_height_script = """
        const div = document.getElementById('channels');
        return div.scrollHeight;
    """
    total_height = driver.execute_script(total_height_script)
    def scroll_and_capture(height):
        script = f"""
            const div = document.getElementById('channels');
            const currentScroll = div.scrollTop;
            div.scrollTo(0, currentScroll + {height});
        """
        driver.execute_script(script)
        time.sleep(0.5)
        return driver.page_source
    def extract_channel_ids(page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        divs_with_channelsid = soup.find_all('a', {'data-list-item-id': True, 'aria-expanded': False})
        channel_info = {} 
        for div in divs_with_channelsid:
            data_list_item_id = div.get('data-list-item-id')
            if data_list_item_id and data_list_item_id.startswith('channels___'):
                channel_id = data_list_item_id.split('channels___')[1]
                channel_name = div.get('aria-label', 'Unknown')  # Get channel name or use 'Unknown'
                channel_info[channel_id] = channel_name
        return channel_info
    for _ in range(total_height // 300 + 1):
        page_source = scroll_and_capture(300)
        new_channel_ids = extract_channel_ids(page_source)
        all_channel_ids[guild_id].update(new_channel_ids)
        time.sleep(0.5)
    if(len(guild_name.split(',')) > 1):
        guild_name = guild_name.split(',')[1].strip()
    await channel.send(f"Fetched all the {len(all_channel_ids[guild_id])} channels of {guild_name} server")

async def retrieve_message(channel_id,channel):
    headers = {
        "Authorization": os.getenv("AUTHORIZATION_KEY")
    }
    response = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=50",headers=headers)
    # For Thread data
    if(response.json() == []):
        response1 = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/threads/search?archived=true&sort_by=last_message_time&sort_order=desc&limit=25&tag_setting=match_some&offset=0",headers=headers)
        json1 = response1.json()
        threadids = []
        for obj in json1['threads']:
            threadids.append(obj['id'])
        response = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/post-data",headers=headers,json={"thread_ids":threadids})
    jsonresponse = response.json()
    with open("dataset.csv", "a",newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["content"])
        jobs = 0
        if "threads" in jsonresponse:
            for thread_id, thread_data in jsonresponse["threads"].items():
                if thread_data.get('first_message') is not None:
                    content = thread_data['first_message']['content'].lower()       
                    if is_job_posting(content) and matches_profile(content):
                        await channel.send(content)
                    if content != "":    
                        text = vectorizer.transform([content])
                        prediction = lr.predict(text)
                        writer.writerow([thread_data['first_message']['content'],prediction[0]])    
                        if(prediction[0] == 1):
                            jobs += 1
                            await channel.send(content + "\nSend DM Now - <@" + thread_data['author']['id'] + ">")
                        print(thread_data['first_message']['content'],"\n")
            if jobs == 0:
                await channel.send("No job postings found")
                return

        else:
            for obj in jsonresponse:
                content = obj['content'].lower()
                if is_job_posting(content) and matches_profile(content):
                    await channel.send(content)
                if content != "":
                    text = vectorizer.transform([obj['content']])
                    prediction = lr.predict(text)
                    writer.writerow([obj['content'],prediction[0]])    
                    if(prediction[0] == 1):
                        jobs += 1
                        await channel.send(content + "\nSend DM Now - <@" + obj['author']['id'] + ">")
                    print(obj['content'],"\n")
            if jobs == 0:
                await channel.send("No job postings found")
                return

async def scrape_website(url,channel):
    await extract_guild_ids(url,channel)






@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()  # Sync commands with Discord

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='scrape')
async def scrape(ctx,arg):
    await ctx.send("Fetching servers...")
    await scrape_website(discord_url,ctx.channel)

@bot.command(name='channel')
async def channel(ctx,arg):
    if(guild_ids == []):
        await ctx.send("Fetching servers...")
        await scrape_website(discord_url,ctx.channel)
    guild_found = False
    for i in guild_ids:
        if arg in i.keys():
            guild_found = True
            arg = list(i.keys())[0]
            break

    if not guild_found:
        await ctx.send("Invalid server ID")
        return
    await ctx.send(f"Fetching channels of {arg}...")
    await extract_all_channel_ids(arg,ctx.channel)
    for channel_id in all_channel_ids:
        print(channel_id,all_channel_ids[channel_id],"\n")

@bot.command(name='work')
async def find_work(ctx,arg):
    guild1 = ctx.guild
    channel = guild1.text_channels
    for i in channel:
        print(i.name+"\n")
        if any(keyword in i.name.lower() for keyword in ["job", "jobs", "job-board","internship","opportunities"]):
            await ctx.send("Fetching jobs for you from " + i.name)
            await retrieve_message(i.id, ctx.channel)

@bot.command(name='job')
async def find_job(ctx):
    await ctx.send("Fetching servers...")
    await scrape_website(discord_url,ctx.channel)

    tabs = []
    for i in range(5,6):
        guild_id = list(guild_ids[i].keys())[0]  
        driver.execute_script("window.open('');")
        tabs.append(driver.window_handles[-1]) 
        driver.switch_to.window(driver.window_handles[-1])
        await extract_all_channel_ids(guild_id,ctx.channel)
    driver.switch_to.window(driver.window_handles[0])

    for tab in tabs:
        driver.switch_to.window(tab)
        driver.close()
    driver.quit()

    channel_count = 0
    for i in range(5,6):
        guild_id = list(guild_ids[i].keys())[0]  
        channel_with_name = all_channel_ids.get(guild_id, {})
        for channel_id, channel_name in channel_with_name.items():
            if any(keyword in channel_name.lower() for keyword in ["job", "jobs", "job-board","internship","opportunities"]):
                channel_count += 1
                await ctx.send("Fetching jobs for you from " + channel_name)
                print("ChannelName - ",channel_name)
                await retrieve_message(channel_id, ctx.channel)
    if channel_count == 0 :
        await ctx.send("No job channels found")
    print(channel_count)

bot.run(token)

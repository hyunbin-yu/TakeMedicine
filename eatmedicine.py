import discord
from discord import Message, File, Embed
from datetime import datetime
import asyncio
import time
from discord.ext import tasks
from discord.ext import commands
import load_json_variable as variable

with open("timelist.txt", 'r', encoding="UTF-8") as f:
    timelist = eval(f.read())

prefix = "약"
bot = commands.Bot(command_prefix=prefix)

@bot.event
async def on_ready():
    print("start")
    now = datetime.now()
    lastclock = int(now.strftime("%H")) - 1

    while 1:
        nowtime = datetime.now()
        clock = int(nowtime.strftime("%H"))
        
        if clock != lastclock:
            admin = await bot.fetch_user(739698524115173387)
            await admin.send("이번 시간 약 알림자 : " + str(timelist[int(clock)]))

            for i in timelist[int(clock)]:                
                temp = await bot.fetch_user(i)
                try:
                    await temp.send("약 먹을 시간이에요.")
                except:
                    await admin.send("전송 오류!" + str(temp))
            
            lastclock = clock
            await asyncio.sleep(60)
        
                     

@bot.event
async def on_message(message):
    if message.author.bot:
        return None
    await bot.process_commands(message)


@bot.command("먹을래")
async def react_test(ctx):
    def check(mes: Message):
        return mes.author == ctx.author and mes.channel == ctx.channel

    try:
        await ctx.send("몇시에 먹을래요? 0부터 23 사이의 정수를 입력해주세요.")
        mes: Message = await ctx.bot.wait_for('message', check=check, timeout=30)

    except asyncio.TimeoutError:
        await ctx.send("제한 시간을 초과했어요. 처음부터 다시 해주세요. 죄송해요.")  
    if not 0 <= int(mes.content) <= 23:
        await ctx.send("아니요. 그렇게 입력하면 안돼요. 처음부터 다시 해주세요.")
    else:
        await ctx.send("오늘부터 매일 " + mes.content + "시 정각에 DM으로 알려줄게요.")
        #print(type(ctx.author))
        timelist[int(mes.content)].append(ctx.author.id)
        with open("timelist.txt", "w", encoding="UTF-8") as f:
            f.write(str(timelist))

        print(timelist)    

    return None

@bot.command("안먹을래")
async def anmuke(ctx):
    def check(mes: Message):
        return mes.author == ctx.author and mes.channel == ctx.channel

    try:
        await ctx.send(str(ctx.author) + "님, 몇 시에 안 드실래요?")
        mes: Message = await ctx.bot.wait_for('message', check=check, timeout=30)

    except asyncio.TimeoutError:
        await ctx.send("제한 시간을 초과했어요. 처음부터 다시 해주세요. 죄송해요.")  
    if not 0 <= int(mes.content) <= 23:
        await ctx.send("아니요. 그렇게 입력하면 안돼요. 처음부터 다시 해주세요.")
    else:
        await ctx.send(mes.content + "시에 더 이상 약을 먹으라고 하지 않을게요.")
        timelist[int(mes.content)].remove(ctx.author.id)
        with open("timelist.txt", "w", encoding="UTF-8") as f:
            f.write(str(timelist))
        print(timelist)

@bot.command("도움")
async def help(ctx):
    await ctx.send("**약을 제때제때 먹을 수 있도록 도와줍니다.**\n- 약언제먹어 : 알림을 받을 시간을 알려줘요.\n- 약먹을래 : 약 먹을 시간을 새로 등록해요.\n- 약안먹을래 : 등록한 시간을 지워요.")

@bot.command("언제먹어")
async def when(ctx):
    wheneat = []
    for i in range(23):
        if ctx.author.id in timelist[i]:
            wheneat.append(i)
    if not str(wheneat) == "[]":
        await ctx.send(str(ctx.author) + "님은 " + str(wheneat) + "시에 약을 먹어요.")
    else:
        await ctx.send(str(ctx.author) + "님은 아직 먹는 약이 없어요.")

bot.run(variable.get_token())

# MIT License
#
# Copyright (c) 2023 jvherck (on GitHub)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import discord, os, random, json, re
from discord.ext.commands import Bot, Context, max_concurrency, BucketType, cooldown
from discord.ext.commands.errors import CommandOnCooldown
from dotenv import load_dotenv
from time import sleep
from roastedbyai import Conversation

load_dotenv()

bot = Bot(command_prefix="roast ", intents=discord.Intents.all())

with open("database/roast.json", "r", encoding="UTF-8") as f:
    roasts = json.load(f)
f.close()


@bot.event
async def on_ready():
    print("Bot logged in as {}".format(bot.user))


@bot.command(name="roast", aliases=["me"])
@max_concurrency(1, BucketType.user)
@max_concurrency(4, BucketType.channel)
@cooldown(1, 60, BucketType.user)
async def _roast(ctx: Context):
    """
    Start an AI roast session. Take turns in roasting the AI and the AI roasting you.
    If you want to stop, simply say "stop" or "quit".

    Cooldown:
    > Once every minute per user

    Concurrency:
    > Maximum of 1 session per user at the same time
    > Maximum of 4 sessions per channel at the same time
    """
    convo = Conversation()
    await ctx.reply(
        "Alright, give me your best roast and we'll take turns.\nIf you want to stop, simply say \"stop\" or \"quit\".")

    def check(m: discord.Message):
        return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

    while convo.alive is True:
        try:
            msg: discord.Message = await bot.wait_for("message", check=check, timeout=300)

            response = None
            while response is None:
                try:
                    await ctx.typing()
                    if msg.content.lower() in ["stop", "quit"]:
                        await ctx.channel.send(
                            f"{ctx.author.mention} you're so lame bro, chickening out like this. "
                            f"But I wouldn't want to hurt your few little braincells much more, buh-bye."
                        )
                        convo.kill()
                        return
                    else:
                        response = convo.send(msg.content)

                except TimeoutError:
                    sleep(1)
                    await ctx.send(f"{ctx.author.mention} I'm too tired to continue talking right now, buh-bye.")
                    convo.kill()
                    return

                else:
                    await msg.reply(response)

        except TimeoutError:
            convo.kill()

    if convo.alive:
        convo.kill()


@bot.event
async def on_message(message: discord.Message):
    if re.fullmatch(r"roast <@[0-9]{18,20}>", message.content.lower()):
        try:
            member = message.guild.get_member(int(re.search(r"<@([0-9]{18,20})>", message.content).group(1)))
            await _roast_someone(await bot.get_context(message), member)
        except Exception as e:
            raise e
    else:
        await bot.process_commands(message)


async def _roast_someone(ctx: Context, target: discord.Member = None):
    """Roast someone :smiling_imp:"""
    if target is None:
        dumb = [
            "Look in the mirror, there's my roast. Now next time give me someone else to roast",
            "Why do you even wanna roast yourself?",
            "https://tenor.com/view/roast-turkey-turkey-thanksgiving-gif-18067752",
            "You get no bitches, so lonely you're even trying to roast yourself...",
            "Stop roasting yourself, there's so many roasts ready to use on others",
            "Don't tell me there's {} other people to roast, and from all those people you want to roast yourself??".format(
                ctx.guild.member_count - 1)
        ]
        await ctx.reply(random.choice(dumb))
        return
    # await ctx.message.delete()
    initroast = random.choice(roasts)
    # initroast = roasts[len(roasts) - 1]
    roast_expl = None
    if type(initroast) is list:
        _roast = initroast[0].replace("{mention}", f"**{target.display_name}**").replace("{author}",
                                                                                         f"**{ctx.author.display_name}**")
        roast_expl = initroast[1].replace("{mention}", f"**{target.display_name}**").replace("{author}",
                                                                                             f"**{ctx.author.display_name}**")
    else:
        _roast = initroast
    roast = f"{target.mention}, " + _roast
    y = -1
    await ctx.channel.send(roast)
    if roast_expl:
        try:
            msg: discord.Message = await bot.wait_for("message",
                                                           check=lambda x:
                                                           x.channel.id == ctx.channel.id and
                                                           x.content.lower().startswith(("what", "what?",
                                                                                         "i dont get it",
                                                                                         "i don't get it")),
                                                           timeout=10)
            await ctx.typing()
            sleep(1.5)
            await msg.reply(roast_expl)
        except Exception as e:
            raise e

@bot.event
async def on_command_error(ctx, ex):
    if isinstance(ex, CommandOnCooldown):
        await ctx.reply(f"You're on cooldown, try again in **`{round(ex.retry_after, 1)}s`**")


if __name__ == "__main__":
    bot.run(os.environ.get("TOKEN"), reconnect=True)

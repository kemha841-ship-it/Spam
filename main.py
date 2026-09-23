import os
import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.command(name="spam")
async def spam(ctx, target_name: str, count: int, delay: int, *, content: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Sếp không có quyền dùng lệnh này!", delete_after=5)
        return

    if count > 500:
        await ctx.send("❌ Tối đa chỉ gửi được 500 tin nhắn thôi sếp ơi!")
        return

    if delay < 1:
        await ctx.send("❌ Thời gian nghỉ tối thiểu phải từ 1 giây!")
        return

    await ctx.send(f"🚀 Đang tìm kiếm tài khoản **{target_name}** để hối thúc...", delete_after=5)

    target_user = None
    target_clean = target_name.strip()

    # 1. Thử tìm bằng ID nếu sếp gõ số
    if target_clean.isdigit():
        try:
            target_user = await bot.fetch_user(int(target_clean))
        except Exception:
            pass

    # 2. Nếu không phải số hoặc không tìm thấy bằng ID, quét toàn bộ người dùng trong server
    if not target_user:
        for member in ctx.guild.members:
            # So khớp với tên hiển thị (Display Name) hoặc Tên tài khoản (Username)
            if (target_clean.lower() in member.name.lower() or 
                target_clean.lower() in member.display_name.lower() or 
                (member.nick and target_clean.lower() in member.nick.lower())):
                target_user = member
                break

    if not target_user:
        await ctx.send(f"❌ Không tìm thấy user nào có tên là `{target_name}` trong server này! Hãy chắc chắn nó có trong server hoặc dùng ID chuẩn.")
        return

    success = 0
    for i in range(1, count + 1):
        try:
            await target_user.send(f"🔔 **[HỐI THÚC HỌC BÀI]** {content} *(Tin {i}/{count})*")
            success += 1
        except Exception as e:
            await ctx.send(f"⚠️ Dừng lại do lỗi (có thể do nó chặn tin nhắn riêng): `{e}`")
            break
        
        if i < count:
            await asyncio.sleep(delay)

    await ctx.send(f"✅ Đã gửi thành công **{success}/{count}** tin nhắn riêng cho **{target_user.name}**!")

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} đã sẵn sàng!")

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)

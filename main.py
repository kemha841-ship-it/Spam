import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="spam", description="Gửi tin nhắn riêng hối thúc học bài bằng ID hoặc Tên")
@app_commands.describe(
    target="Nhập ID Discord hoặc Tên của người cần spam",
    noidung="Nội dung muốn gửi",
    solan="Số lượng tin nhắn (tối đa 500)",
    delay="Số giây nghỉ giữa các tin (tối thiểu 1)"
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def spam(interaction: discord.Interaction, target: str, noidung: str, solan: int, delay: int):
    if solan > 500:
        await interaction.response.send_message("❌ Tối đa chỉ gửi được 500 lần thôi sếp ơi!", ephemeral=True)
        return
    
    if delay < 1:
        await interaction.response.send_message("❌ Thời gian nghỉ tối thiểu phải từ 1 giây!", ephemeral=True)
        return

    # Phản hồi ẩn xác nhận đang xử lý
    await interaction.response.send_message(f"🚀 Đang tìm kiếm tài khoản **{target}** để hối thúc...", ephemeral=True)

    target_user = None
    target_clean = target.strip()

    # Nếu sếp nhập ID (toàn số)
    if target_clean.isdigit():
        try:
            target_user = await bot.fetch_user(int(target_clean))
        except Exception:
            pass

    # Nếu không tìm thấy bằng ID, thử tìm trong danh sách thành viên của server theo tên
    if not target_user:
        for member in interaction.guild.members:
            if target_clean.lower() in member.name.lower() or (member.nick and target_clean.lower() in member.nick.lower()):
                target_user = member
                break

    if not target_user:
        await interaction.followup.send(f"❌ Không tìm thấy user nào có ID hoặc tên là **{target}**!", ephemeral=True)
        return

    # Tiến hành oanh tạc tin nhắn riêng (DM)
    success_count = 0
    for i in range(1, solan + 1):
        try:
            await target_user.send(f"🔔 **[HỐI THÚC HỌC BÀI]** {noidung} *(Tin {i}/{solan})*")
            success_count += 1
        except Exception as e:
            await interaction.followup.send(f"⚠️ Dừng lại do vướng lỗi (có thể do nó chặn tin nhắn người lạ): `{e}`", ephemeral=True)
            break
        
        if i < solan:
            await asyncio.sleep(delay)

    await interaction.followup.send(f"✅ Đã gửi thành công **{success_count}/{solan}** tin nhắn riêng cho **{target_user.name}**!", ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} lệnh.")
    except Exception as e:
        print(f"Lỗi: {e}")
    print(f"Bot {bot.user.name} đã sẵn sàng!")
    await bot.change_presence(activity=discord.Game(name="/spam | Hối học bài riêng"))

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)

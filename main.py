import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.tree.command(
    name="spam", description="Gửi tin nhắn riêng hối thúc học bài chuyên nghiệp"
)
@app_commands.describe(
    target="Nhập ID Discord hoặc Tên tài khoản cần gửi",
    noidung="Nội dung muốn hối thúc",
    solan="Số lượng tin nhắn (tối đa 500)",
    delay="Số giây nghỉ giữa các tin (tối thiểu 1)",
)
@discord.app_commands.checks.has_permissions(administrator=True)
async def spam(
    interaction: discord.Interaction,
    target: str,
    noidung: str,
    solan: int,
    delay: int,
):
  if solan > 500:
    await interaction.response.send_message(
        "❌ Tối đa chỉ gửi được 500 tin nhắn thôi sếp ơi!", ephemeral=True
    )
    return

  if delay < 1:
    await interaction.response.send_message(
        "❌ Thời gian nghỉ tối thiểu phải từ 1 giây!", ephemeral=True
    )
    return

  # Phản hồi ngay lập tức để Discord không báo lỗi
  await interaction.response.defer(ephemeral=True)

  target_user = None
  target_clean = target.strip()

  # 1. Tìm bằng ID nếu sếp gõ số
  if target_clean.isdigit():
    try:
      target_user = await bot.fetch_user(int(target_clean))
    except Exception:
      pass

  # 2. Nếu không phải ID, quét trong danh sách thành viên server
  if not target_user and interaction.guild:
    for member in interaction.guild.members:
      if (
          target_clean.lower() in member.name.lower()
          or target_clean.lower() in member.display_name.lower()
          or (member.nick and target_clean.lower() in member.nick.lower())
      ):
        target_user = member
        break

  if not target_user:
    await interaction.followup.send(
        f"❌ Không tìm thấy user nào có tên hoặc ID là `{target}`!",
        ephemeral=True,
    )
    return

  # Thông báo bắt đầu chiến dịch
  await interaction.followup.send(
      f"🚀 Đã bắt đầu oanh tạc hòm thư riêng của **{target_user.name}** ({solan}"
      " tin)...",
      ephemeral=True,
  )

  success = 0
  for i in range(1, solan + 1):
    try:
      await target_user.send(
          f"🔔 **[HỐI THÚC HỌC BÀI]** {noidung} *(Tin {i}/{solan})*"
      )
      success += 1
    except Exception as e:
      await interaction.followup.send(
          f"⚠️ Dừng lại do lỗi (có thể do nó chặn tin nhắn người lạ): `{e}`",
          ephemeral=True,
      )
      break

    if i < solan:
      await asyncio.sleep(delay)

  await interaction.followup.send(
      f"✅ Đã gửi thành công **{success}/{solan}** tin nhắn riêng cho"
      f" **{target_user.name}**!",
      ephemeral=True,
  )


@bot.event
async def on_ready():
  try:
    synced = await bot.tree.sync()
    print(f"Đã đồng bộ thành công {len(synced)} lệnh slash.")
  except Exception as e:
    print(f"Lỗi đồng bộ lệnh: {e}")
  print(f"Bot {bot.user.name} đã sẵn sàng hoạt động chuyên nghiệp!")


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("❌ Không tìm thấy biến môi trường DISCORD_TOKEN!")

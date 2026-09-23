import discord
from discord import app_commands
from discord.ext import commands

# --- CẤU HÌNH BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- ID ADMIN ĐÃ ĐƯỢC THIẾT LẬP CHO SẾP ---
ADMIN_ID = 1492784020193415271


@bot.event
async def on_ready():
  print(f"Bot đã online: {bot.user}")
  try:
    synced = await bot.tree.sync()
    print(f"Đã đồng bộ {len(synced)} lệnh slash (/).")
  except Exception as e:
    print(f"Lỗi đồng bộ lệnh: {e}")


# --- LỆNH SPAM 2 CHẾ ĐỘ + BẢO MẬT ADMIN ---
@bot.tree.command(
    name="spam",
    description="Công cụ spam siêu tốc (Chỉ Admin mới có quyền sử dụng)",
)
@app_commands.describe(
    mode="Chọn chế độ: 1 = Spam kênh nhóm, 2 = Spam tin nhắn riêng (DM)",
    target="Người nhận (nếu mode=2) hoặc để trống (nếu mode=1)",
    amount="Số lượng tin nhắn cần gửi (tốc độ nhanh)",
    content="Nội dung tin nhắn spam",
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="1. Spam Kênh Nhóm (Channel)", value=1),
        app_commands.Choice(name="2. Spam Tin Nhắn Riêng (DM)", value=2),
    ]
)
async def spam(
    interaction: discord.Interaction,
    mode: int,
    amount: int,
    content: str,
    target: discord.Member = None,
):
  # 1. KIỂM TRA BẢO MẬT ADMIN (Chỉ sếp mới dùng được)
  if interaction.user.id != ADMIN_ID:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân (Admin) của tao, đừng có hòng dùng lệnh"
        " này!",
        ephemeral=True,
    )
    return

  # Giới hạn số lượng để tránh sập bot/Discord rate limit
  if amount > 50:
    amount = 50

  # Phản hồi trước để Discord không bị timeout
  await interaction.response.send_message(
      f"🚀 Bắt đầu chiến dịch spam (Chế độ {mode}), chuẩn bị xả {amount} tin"
      " nhắn...",
      ephemeral=True,
  )

  # --- CHẾ ĐỘ 1: SPAM KÊNH NHÓM (CHANNEL) ---
  if mode == 1:
    channel = interaction.channel
    for i in range(amount):
      try:
        await channel.send(f"{content} ({i+1}/{amount})")
      except Exception as e:
        print(f"Lỗi gửi tin nhắn kênh: {e}")
        break

  # --- CHẾ ĐỘ 2: SPAM TIN NHẮN RIÊNG (DM) ---
  elif mode == 2:
    if not target:
      await interaction.followup.send(
          "❌ Vui lòng chọn `target` (người nhận) khi dùng chế độ Spam DM!",
          ephemeral=True,
      )
      return

    try:
      # Mở hoặc lấy sẵn hòm thư DM với mục tiêu
      dm_channel = target.dm_channel
      if dm_channel is None:
        dm_channel = await target.create_dm()

      for i in range(amount):
        try:
          await dm_channel.send(f"{content} ({i+1}/{amount})")
        except Exception as e:
          print(f"Lỗi gửi DM: {e}")
          break
    except Exception as e:
      await interaction.followup.send(
          f"❌ Không thể gửi tin nhắn riêng cho người này: {e}", ephemeral=True
      )


# Thay token hoặc giữ nguyên cấu hình biến môi trường trên Railway của sếp
bot.run("TOKEN_CUA_BOT")

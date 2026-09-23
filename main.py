import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID TỐI CAO CỦA SẾP - CẤM TUYỆT ĐỐI NGƯỜI KHÁC DÙNG
ADMIN_ID = 1492784020193415271


@bot.tree.command(
    name="spam",
    description="Hệ thống hủy diệt & Treo máy toàn năng (Chỉ dành cho Chủ nhân)",
)
@app_commands.describe(
    mode="Chọn chế độ: 1 = Spam Kênh, 2 = Spam DM, 3 = Treo dài hạn (1-2 tiếng)",
    content="Nội dung tin nhắn muốn gửi hoặc treo",
    amount="Số lượng (dành cho mode 1 & 2)",
    target="Người nhận (Bắt buộc nếu chọn chế độ 2 hoặc 3 để DM)",
    hours="Số giờ muốn treo (Chỉ dùng cho chế độ 3, tối đa 3 giờ)",
    interval="Số giây nghỉ giữa mỗi tin khi treo (Chế độ 3, khuyên dùng từ 30s trở lên)",
)
@app_commands.choices(
    mode=[
        app_commands.Choice(name="1. Spam Kênh Server (Nhanh)", value=1),
        app_commands.Choice(name="2. Spam Tin Nhắn Riêng DM (Nhanh)", value=2),
        app_commands.Choice(name="3. Treo Máy Dài Hạn (1-2 Tiếng Chạy Ngầm)", value=3),
    ]
)
async def spam(
    interaction: discord.Interaction,
    mode: int,
    content: str,
    amount: int = 10,
    target: discord.Member = None,
    hours: float = 1.0,
    interval: int = 30,
):
  # 1. BẢO MẬT TUYỆT ĐỐI - CHỈ ADMIN MỚI ĐƯỢC XÀI
  if interaction.user.id != ADMIN_ID:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân tối cao của tao, tuổi gì đòi dùng"
        " lệnh này!",
        ephemeral=True,
    )
    return

  await interaction.response.defer(ephemeral=True)

  # --- CHẾ ĐỘ 1: SPAM KÊNH SERVER ---
  if mode == 1:
    if amount > 200:
      amount = 200
    channel = interaction.channel
    await interaction.followup.send(
        f"⚡ Bắt đầu oanh tạc kênh **{channel.name}** với {amount} tin nhắn!",
        ephemeral=True,
    )
    for i in range(1, amount + 1):
      try:
        await channel.send(f"🔥 **[SYSTEM ATTACK]** {content} *({i}/{amount})*")
        await asyncio.sleep(0.4)
      except Exception:
        break

  # --- CHẾ ĐỘ 2: SPAM DM NHANH ---
  elif mode == 2:
    if not target:
      await interaction.followup.send(
          "❌ Chế độ 2 bắt buộc phải chọn `target` (người nhận) sếp ơi!",
          ephemeral=True,
      )
      return
    if amount > 200:
      amount = 200

    await interaction.followup.send(
        f"🎯 Đang rót mưa bom vào hòm thư riêng của **{target.name}** ({amount}"
        " tin)...",
        ephemeral=True,
    )
    success = 0
    for i in range(1, amount + 1):
      try:
        await target.send(
            f"💀 **[DARK SYSTEM]** {content} ❄️ *({i}/{amount})*"
        )
        success += 1
        await asyncio.sleep(0.4)
      except Exception:
        break

    await interaction.followup.send(
        f"✅ Hoàn tất! Đã tống thành công {success}/{amount} tin vào DM của"
        f" **{target.name}**.",
        ephemeral=True,
    )

  # --- CHẾ ĐỘ 3: TREO MÁY DÀI HẠN (1-2 TIẾNG CHẠY NGẦM) ---
  elif mode == 3:
    if not target:
      await interaction.followup.send(
          "❌ Chế độ Treo (Mode 3) bắt buộc phải chọn `target` (người nhận DM)"
          " để treo máy!",
          ephemeral=True,
      )
      return

    if hours > 3.0:
      hours = 3.0  # Giới hạn tối đa 3 tiếng để bảo vệ bot

    total_seconds = int(hours * 3600)
    await interaction.followup.send(
        f"🛡️ **Đã kích hoạt chế độ Treo Dài Hạn!**\n- Mục tiêu:"
        f" **{target.name}**\n- Thời gian treo: **{hours} tiếng**\n- Tần suất:"
        f" Cứ **{interval} giây** gửi 1 tin.\nBot sẽ tự động chạy ngầm bền"
        " bỉ!",
        ephemeral=True,
    )

    # Hàm chạy ngầm không làm nghẽn bot
    async def background_hanging():
      elapsed = 0
      count = 0
      while elapsed < total_seconds:
        try:
          count += 1
          await target.send(
              f"⏳ **[AFK SYSTEM TREO MÁY]** {content} *(Lần {count})*"
          )
        except Exception as e:
          print(f"Lỗi treo máy DM: {e}")
          break
        await asyncio.sleep(interval)
        elapsed += interval

    # Đẩy tác vụ chạy ngầm độc lập
    asyncio.create_task(background_hanging())


@bot.event
async def on_ready():
  try:
    synced = await bot.tree.sync()
    print(f"Đã đồng bộ {len(synced)} lệnh slash.")
  except Exception as e:
    print(f"Lỗi đồng bộ: {e}")
  print(f"Bot {bot.user.name} đã online và sẵn sàng hủy diệt!")


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("❌ Không tìm thấy biến môi trường DISCORD_TOKEN!")

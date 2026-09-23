import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# UID CHÍNH CHỦ CỦA SẾP
ADMIN_ID = 1492784020193415271


# --- MENU CHỌN CHẾ ĐỘ ĐẲNG CẤP ---
class ChonCheDoView(discord.ui.View):

  def __init__(self, author_id: int, content: str, amount: int, target, hours, interval):
    super().__init__(timeout=60)
    self.author_id = author_id
    self.content = content
    self.amount = amount
    self.target = target
    self.hours = hours
    self.interval = interval

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN CHẾ ĐỘ HỦY DIỆT TỐI THƯỢNG...",
      min_values=1,
      max_values=1,
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server",
              description="Xả đạn trực tiếp vào kênh chat hiện tại",
              emoji="⚡",
              value="1",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng (DM)",
              description="Oanh tạc hòm thư cá nhân mục tiêu",
              emoji="🎯",
              value="2",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (1-2 Tiếng)",
              description="Chạy ngầm liên tục bền bỉ theo thời gian",
              emoji="🛡️",
              value="3",
          ),
      ],
  )
  async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
    # Kiểm tra bảo mật ngay trên menu
    if interaction.user.id != self.author_id:
      await interaction.response.send_message(
          "❌ **Cút!** Menu này không dành cho mày!", ephemeral=True
      )
      return

    mode = int(select.values[0])
    await interaction.response.defer(ephemeral=True)

    # --- CHẾ ĐỘ 1: SPAM KÊNH ---
    if mode == 1:
      amt = self.amount if self.amount <= 200 else 200
      channel = interaction.channel
      await interaction.followup.send(
          f"⚡ Đã nạp đạn! Oanh tạc kênh **{channel.name}** với {amt} tin nhắn!",
          ephemeral=True,
      )
      for i in range(1, amt + 1):
        try:
          await channel.send(f"🔥 **[SYSTEM ATTACK]** {self.content} *({i}/{amt})*")
          await asyncio.sleep(0.4)
        except Exception:
          break

    # --- CHẾ ĐỘ 2: SPAM DM ---
    elif mode == 2:
      if not self.target:
        await interaction.followup.send(
            "❌ Sếp chưa chọn người nhận (`nguoi_nhan`) kìa!", ephemeral=True
        )
        return
      amt = self.amount if self.amount <= 200 else 200
      await interaction.followup.send(
          f"🎯 Đang rót mưa bom vào hòm thư của **{self.target.name}** ({amt} tin)...",
          ephemeral=True,
      )
      success = 0
      for i in range(1, amt + 1):
        try:
          await self.target.send(
              f"💀 **[DARK SYSTEM]** {self.content} ❄️ *({i}/{amt})*"
          )
          success += 1
          await asyncio.sleep(0.4)
        except Exception:
          break
      await interaction.followup.send(
          f"✅ Hoàn tất! Đã tống {success}/{amt} tin vào DM của **{self.target.name}**.",
          ephemeral=True,
      )

    # --- CHẾ ĐỘ 3: TREO MÁY ---
    elif mode == 3:
      if not self.target:
        await interaction.followup.send(
            "❌ Chế độ treo máy bắt buộc phải chọn `nguoi_nhan`!", ephemeral=True
        )
        return
      hrs = self.hours if self.hours <= 3.0 else 3.0
      total_seconds = int(hrs * 3600)
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt hệ thống Treo Ngầm!**\n- Mục tiêu: **{self.target.name}**\n- Thời gian: **{hrs} tiếng**\n- Tần suất: Cứ **{self.interval} giây** gửi 1 tin.",
          ephemeral=True,
      )

      async def background_hanging():
        elapsed = 0
        count = 0
        while elapsed < total_seconds:
          try:
            count += 1
            await self.target.send(
                f"⏳ **[AFK SYSTEM TREO MÁY]** {self.content} *(Lần {count})*"
            )
          except Exception:
            break
          await asyncio.sleep(self.interval)
          elapsed += self.interval

      asyncio.create_task(background_hanging())


@bot.tree.command(
    name="spam",
    description="Hệ thống hủy diệt tối thượng (Giao diện Menu tiếng Việt)",
)
@app_commands.describe(
    noi_dung="Nhập nội dung tin nhắn muốn bắn hoặc treo",
    so_luong="Số lượng tin nhắn (Dùng cho mode 1 & 2, mặc định 10)",
    nguoi_nhan="Chọn người nhận (Bắt buộc nếu dùng chế độ DM hoặc Treo)",
    so_gio="Số giờ muốn treo máy (Dùng cho chế độ 3, tối đa 3 giờ)",
    nghi_giay="Số giây nghỉ giữa mỗi tin khi treo (Mặc định 30 giây)",
)
async def spam(
    interaction: discord.Interaction,
    noi_dung: str,
    so_luong: int = 10,
    nguoi_nhan: discord.Member = None,
    so_gio: float = 1.0,
    nghi_giay: int = 30,
):
  # Kiểm tra bảo mật tối cao
  if interaction.user.id != ADMIN_ID:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân tối cao của tao, tuổi gì đòi dùng"
        " lệnh này!",
        ephemeral=True,
    )
    return

  # Gửi bảng Menu chọn chế độ cực đẹp mắt bằng tiếng Việt
  view = ChonCheDoView(
      interaction.user.id, noi_dung, so_luong, nguoi_nhan, so_gio, nghi_giay
  )
  await interaction.response.send_message(
      "💻 **[HỆ THỐNG ĐIỀU KHIỂN TỐI CAO]**\nSếp vui lòng chọn phương thức tấn"
      " công bên dưới:",
      view=view,
      ephemeral=True,
  )


@bot.event
async def on_ready():
  try:
    synced = await bot.tree.sync()
    print(f"Đã đồng bộ {len(synced)} lệnh.")
  except Exception as e:
    print(f"Lỗi: {e}")
  print(f"Bot {bot.user.name} đã sẵn sàng phục vụ Chủ nhân!")


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("❌ Thiếu DISCORD_TOKEN!")

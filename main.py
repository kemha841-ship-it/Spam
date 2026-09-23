import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ADMIN_USERNAME = "huy09153"

# Từ điển quản lý các task đang chạy
active_tasks = {}


# --- LỆNH CHAT !STOP ĐỂ HỦY NGAY LẬP TỨC ---
@bot.command(name="stop")
async def stop_command(ctx):
  if ctx.author.name != ADMIN_USERNAME:
    await ctx.send("❌ Mày không phải chủ nhân, tuổi gì dừng lệnh!")
    return

  if active_tasks:
    # Đổi toàn bộ trạng thái thành False để dừng các vòng lặp
    for task_id in list(active_tasks.keys()):
      active_tasks[task_id] = False
    active_tasks.clear()
    await ctx.send(
        "🛑 **[HỆ THỐNG]** Đã phát lệnh `!stop`! Tất cả các chiến dịch treo"
        " ngầm đã bị hủy khẩn cấp!"
    )
  else:
    await ctx.send(
        "⚠️ Hiện tại không có chiến dịch treo ngầm nào đang hoạt động cả!"
    )


# --- BẢNG NHẬP LIỆU CHO SPAM NHANH ---
class ModalSpamNhanh(discord.ui.Modal, title="⚡ CẤU HÌNH CHIẾN DỊCH SPAM"):

  noi_dung = discord.ui.TextInput(
      label="Nội dung muốn spam",
      placeholder="Nhập nội dung vào đây...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="Ví dụ: 20",
      default="10",
      max_length=3,
      required=True,
  )

  def __init__(self, mode_type: str, target_member=None):
    super().__init__()
    self.mode_type = mode_type
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    if self.mode_type == "server":
      channel = interaction.channel
      await interaction.followup.send(
          f"⚡ Đã nạp đạn! Oanh tạc kênh **{channel.name}** với {amount} tin!",
          ephemeral=True,
      )
      for i in range(1, amount + 1):
        try:
          await channel.send(f"🔥 **[SYSTEM ATTACK]** {content} *({i}/{amount})*")
          await asyncio.sleep(0.2)  # Tăng tốc độ xả đạn
        except Exception:
          break

    elif self.mode_type == "dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Chưa chọn người nhận DM!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🎯 Đang rót mưa bom vào hòm thư của **{self.target_member.name}**"
          f" ({amount} tin)...",
          ephemeral=True,
      )
      success = 0
      for i in range(1, amount + 1):
        try:
          await self.target_member.send(
              f"💀 **[DARK SYSTEM]** {content} ❄️ *({i}/{amount})*"
          )
          success += 1
          await asyncio.sleep(0.2)  # Tăng tốc độ xả đạn DM
        except Exception:
          break
      await interaction.followup.send(
          f"✅ Hoàn tất! Đã tống {success}/{amount} tin vào DM của"
          f" **{self.target_member.name}**.",
          ephemeral=True,
      )


# --- BẢNG NHẬP LIỆU CHO TREO GIỜ (SIÊU TỐC) ---
class ModalTreoGio(discord.ui.Modal, title="🛡️ CẤU HÌNH HỆ THỐNG TREO NGẦM"):

  noi_dung = discord.ui.TextInput(
      label="Nội dung muốn treo",
      placeholder="Nhập nội dung treo máy...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_gio = discord.ui.TextInput(
      label="Số giờ treo (Tối đa 3 tiếng)",
      placeholder="Ví dụ: 1 hoặc 2",
      default="1",
      max_length=3,
      required=True,
  )
  nghi_giay = discord.ui.TextInput(
      label="Số giây nghỉ giữa mỗi tin (Ví dụ: 1 hoặc 2 giây)",
      placeholder="Mặc định: 2 giây",
      default="2",
      max_length=4,
      required=True,
  )

  def __init__(self, treo_type: str, target_member=None):
    super().__init__()
    self.treo_type = treo_type
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      hours = float(self.so_gio.value)
      if hours > 3.0:
        hours = 3.0
    except ValueError:
      hours = 1.0

    try:
      interval = float(self.nghi_giay.value)
      if interval < 0.5:
        interval = 0.5  # Cho phép siêu tốc độ
    except ValueError:
      interval = 2.0

    total_seconds = int(hours * 3600)
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True

    # Treo Server siêu tốc
    if self.treo_type == "treo_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo Kênh Siêu Tốc!**\n- Kênh:"
          f" **{channel.name}**\n- Tần suất: Cứ **{interval} giây** 1 tin."
          f"\n- Muốn dừng lúc nào chỉ cần gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(
                f"⏳ **[AFK SERVER TREO]** {content} *(Lần {count})*"
            )
          except Exception:
            break
          await asyncio.sleep(interval)
          elapsed += interval
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    # Treo DM siêu tốc
    elif self.treo_type == "treo_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Chưa chọn mục tiêu để treo DM!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo DM Siêu Tốc!**\n- Mục tiêu:"
          f" **{self.target_member.name}**\n- Tần suất: Cứ **{interval} giây** 1"
          f" tin.\n- Muốn dừng lúc nào chỉ cần gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(
                f"⏳ **[AFK DM TREO]** {content} *(Lần {count})*"
            )
          except Exception:
            break
          await asyncio.sleep(interval)
          elapsed += interval
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_dm())


# --- MENU CHỌN KIỂU TREO ---
class ViewChonKieuTreo(discord.ui.View):

  def __init__(self, target_member=None):
    super().__init__(timeout=60)
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🛡️ CHỌN HÌNH THỨC TREO MÁY...",
      options=[
          discord.SelectOption(
              label="Treo Kênh Server",
              description="Treo tự động gửi vào kênh chat hiện tại",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tin Nhắn Riêng (DM)",
              description="Treo tự động bắn vào hòm thư mục tiêu",
              emoji="🎯",
              value="treo_dm",
          ),
      ],
  )
  async def select_treo(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    kieu = select.values[0]
    if kieu == "treo_dm" and not self.target_member:
      await interaction.response.send_message(
          "❌ Sếp cần chọn mục tiêu (`nguoi_nhan`) từ lệnh ban đầu để treo DM"
          " nhé!",
          ephemeral=True,
      )
      return
    await interaction.response.send_modal(
        ModalTreoGio(treo_type=kieu, target_member=self.target_member)
    )


# --- MENU CHÍNH BƯỚC 1 ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN CHẾ ĐỘ TẤN CÔNG...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server",
              description="Hiện bảng nhập nội dung & số lượng để xả đạn",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng (DM)",
              description="Hiện bảng nhập oanh tạc hòm thư mục tiêu",
              emoji="🎯",
              value="spam_dm",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (Siêu Tốc)",
              description="Chọn hình thức treo giờ chạy ngầm tốc độ cao",
              emoji="🛡️",
              value="treo_gio",
          ),
      ],
  )
  async def select_main(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    if interaction.user.name != self.author_name:
      await interaction.response.send_message(
          "❌ **Cút!** Menu này không dành cho mày!", ephemeral=True
      )
      return

    choice = select.values[0]

    if choice == "spam_server":
      await interaction.response.send_modal(
          ModalSpamNhanh(mode_type="server")
      )
    elif choice == "spam_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp ơi, chế độ Spam DM bắt buộc phải chọn `nguoi_nhan` ngay ở"
            " bảng lệnh đầu tiên nhé!",
            ephemeral=True,
        )
        return
      await interaction.response.send_modal(
          ModalSpamNhanh(mode_type="dm", target_member=self.target_member)
      )
    elif choice == "treo_gio":
      view_treo = ViewChonKieuTreo(target_member=self.target_member)
      await interaction.response.send_message(
          "🛡️ **[HỆ THỐNG TREO GIỜ]**\nSếp muốn treo theo hình thức nào?",
          view=view_treo,
          ephemeral=True,
      )


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt tối thượng (Menu & Khung nhập)"
)
@app_commands.describe(
    nguoi_nhan="Chọn người nhận (Bắt buộc nếu muốn dùng chức năng Spam DM hoặc Treo DM)"
)
async def spam(
    interaction: discord.Interaction, nguoi_nhan: discord.Member = None
):
  if interaction.user.name != ADMIN_USERNAME:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân tối cao của tao, tuổi gì đòi dùng"
        " lệnh này!",
        ephemeral=True,
    )
    return

  view = ViewMenuChinh(
      author_name=interaction.user.name, target_member=nguoi_nhan
  )
  await interaction.response.send_message(
      "💻 **[HỆ THỐNG ĐIỀU KHIỂN TỐI CAO]**\nSếp vui lòng chọn phương thức bên"
      " dưới:",
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

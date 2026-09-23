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
active_tasks = {}


# --- LỆNH CHAT !STOP ---
@bot.command(name="stop")
async def stop_command(ctx):
  if ctx.author.name != ADMIN_USERNAME:
    await ctx.send("❌ Mày không phải chủ nhân, tuổi gì dừng lệnh!")
    return

  if active_tasks:
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


# --- MODAL SPAM NHANH (CỰC TỐC 0.01S) ---
class ModalSpamNhanh(discord.ui.Modal, title="⚡ CHIẾN DỊCH HỦY DIỆT (0.01S)"):

  noi_dung = discord.ui.TextInput(
      label="Nội dung muốn spam",
      placeholder="Nhập nội dung vào đây...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="Ví dụ: 50",
      default="30",
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
          f"⚡ Khai hỏa liên thanh kênh **{channel.name}** với {amount} tin!",
          ephemeral=True,
      )
      for i in range(1, amount + 1):
        try:
          await channel.send(f"🔥 **[SPEED ATTACK]** {content} *({i}/{amount})*")
          await asyncio.sleep(0.01)  # Tốc độ 0.01 giây cực bốc
        except Exception:
          break

    elif self.mode_type == "dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp chưa chọn người nhận ở lệnh ban đầu!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🎯 Oanh tạc hòm thư **{self.target_member.name}** ({amount}"
          " tin)...",
          ephemeral=True,
      )
      success = 0
      for i in range(1, amount + 1):
        try:
          await self.target_member.send(
              f"💀 **[DARK SYSTEM]** {content} ❄️ *({i}/{amount})*"
          )
          success += 1
          await asyncio.sleep(0.01)  # Tốc độ 0.01 giây cực bốc
        except Exception:
          break
      await interaction.followup.send(
          f"✅ Hoàn tất! Đã tống {success}/{amount} tin vào DM của"
          f" **{self.target_member.name}**.",
          ephemeral=True,
      )


# --- MODAL TREO GIỜ (CỰC TỐC 0.01S) ---
class ModalTreoGio(discord.ui.Modal, title="🛡️ CẤU HÌNH TREO NGẦM TỐC ĐỘ CAO"):

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
      label="Số giây nghỉ giữa mỗi tin (Ví dụ: 0.01)",
      placeholder="Mặc định: 0.01",
      default="0.01",
      max_length=6,
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
      if interval < 0.01:
        interval = 0.01
    except ValueError:
      interval = 0.01

    total_seconds = int(hours * 3600)
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True

    # Treo Server
    if self.treo_type == "treo_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo Kênh 0.01s!**\n- Kênh: **{channel.name}**\n-"
          f" Tần suất: **{interval}s**/tin.\n- Muốn dừng gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(
                f"⏳ **[AFK SERVER]** {content} *(Lần {count})*"
            )
          except Exception:
            break
          await asyncio.sleep(interval)
          elapsed += interval
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    # Treo DM
    elif self.treo_type == "treo_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp chưa chọn `nguoi_nhan` ở bảng lệnh đầu tiên để treo DM!",
            ephemeral=True,
        )
        return
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo DM 0.01s!**\n- Mục tiêu:"
          f" **{self.target_member.name}**\n- Tần suất: **{interval}s**/tin.\n-"
          " Muốn dừng gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(
                f"⏳ **[AFK DM]** {content} *(Lần {count})*"
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
              description="Treo tốc độ cao vào kênh hiện tại",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tin Nhắn Riêng (DM)",
              description="Treo tốc độ cao vào hòm thư mục tiêu",
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
          "❌ Sếp chưa chọn mục tiêu (`nguoi_nhan`) ở lệnh ban đầu!",
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
              description="Xả đạn nhanh kênh server",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng (DM)",
              description="Xả đạn nhanh hòm thư mục tiêu",
              emoji="🎯",
              value="spam_dm",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (0.01s)",
              description="Treo ngầm tốc độ cao liên thanh",
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
        await interaction.response.send_message(
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


TOKEN = os.getenv("DISNCORD_TOKEN")  # noqa: F841
TOKEN_ENV = os.getenv("DISCORD_TOKEN")
if TOKEN_ENV:
  bot.run(TOKEN_ENV)
else:
  print("❌ Thiếu DISCORD_TOKEN!")

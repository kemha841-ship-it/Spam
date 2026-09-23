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


def chunks(lst, n):
  for i in range(0, len(lst), n):
    yield lst[i : i + n]


# --- MODAL 1: SPAM KÊNH SERVER (HỖ TRỢ ĐOẠN VĂN DÀI TỚI 500+ CHỮ) ---
class ModalSpamServer(discord.ui.Modal, title="⚡ SPAM KÊNH SERVER (FULL TEXT)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung văn bản dài (tới 500+ chữ)",
      placeholder=(
          "Dán đoạn văn dài tùy ý vào đây, bao nhiêu chữ cũng nhận hết..."
      ),
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="30",
      default="30",
      max_length=3,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    channel = interaction.channel
    await interaction.followup.send(
        f"⚡ Đang xả {amount} tin nhắn dài vào kênh **{channel.name}**...",
        ephemeral=True,
    )

    # Gửi nguyên văn bản sếp nhập mà không bị cắt xén ngắn gọn
    tasks = [
        channel.send(content=f"{content}\n🔥 *({i}/{amount})*")
        for i in range(1, amount + 1)
    ]
    for batch in chunks(tasks, 10):
      await asyncio.gather(
          *(asyncio.gather(t, return_exceptions=True) for t in batch)
      )
      await asyncio.sleep(0.001)


# --- MODAL 2: SPAM VĂN BẢN TỰ DO TRÀN SERVER (THAY THẾ CHO DM CŨ) ---
class ModalSpamTrangServer(discord.ui.Modal, title="🌊 SPAM VĂN BẢN TRÀN SERVER"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung văn bản spam tràn server",
      placeholder="Nhập nội dung văn bản tự do dài tùy ý...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="30",
      default="30",
      max_length=3,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    channel = interaction.channel
    await interaction.followup.send(
        f"🌊 Đang oanh tạc tràn server tại kênh **{channel.name}** ({amount}"
        " tin)...",
        ephemeral=True,
    )

    # Gửi liên tục text tự do tràn ngập thẳng vào kênh server
    for i in range(1, amount + 1):
      try:
        await channel.send(content=f"{content}\n🌊 *({i}/{amount})*")
        await asyncio.sleep(0.01)
      except Exception:
        break
    await interaction.followup.send(
        f"✅ Hoàn tất oanh tạc tràn server tại **{channel.name}**!", ephemeral=True
    )


# --- MODAL 3: TREO MÁY DÀI HẠN (1 ĐẾN 5 TIẾNG - HỖ TRỢ FULL VĂN BẢN) ---
class ModalTreoMay(discord.ui.Modal, title="🛡️ TREO MÁY DÀI HẠN (1 - 5 TIẾNG)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung văn bản treo ngầm",
      placeholder="Nhập nội dung văn bản dài tùy ý...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_gio = discord.ui.TextInput(
      label="Số giờ treo (Từ 1 đến 5 tiếng)",
      placeholder="Ví dụ: 1 hoặc 3",
      default="1",
      max_length=1,
      required=True,
  )

  def __init__(self, treo_type: str):
    super().__init__()
    self.treo_type = treo_type

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      hours = int(self.so_gio.value)
      if hours < 1:
        hours = 1
      if hours > 5:
        hours = 5
    except ValueError:
      hours = 1

    total_seconds = hours * 3600
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True

    # 1. Treo Server
    if self.treo_type == "treo_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã bật Treo Kênh Server trong {hours} tiếng!**\n- Kênh:"
          f" **{channel.name}**\n- Gõ `!stop` để dừng bất cứ lúc nào.",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(content=f"{content}\n⏳ *(Lần {count})*")
          except Exception:
            break
          await asyncio.sleep(0.5)
          elapsed += 0.5
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    # 2. Treo Tràn Server (Thay thế Treo DM cũ)
    elif self.treo_type == "treo_trang_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã bật Treo Tràn Server liên tục trong {hours} tiếng!**\n- Gõ"
          " `!stop` để dừng bất cứ lúc nào.",
          ephemeral=True,
      )

      async def bg_trang_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(content=f"{content}\n🌊 *(AFK Tràn Lần {count})*")
          except Exception:
            break
          await asyncio.sleep(0.5)
          elapsed += 0.5
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_trang_server())


# --- VIEW CHỌN HÌNH THỨC TREO MÁY ---
class ViewChonKieuTreo(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=60)

  @discord.ui.select(
      placeholder="🛡️ CHỌN HÌNH THỨC TREO MÁY...",
      options=[
          discord.SelectOption(
              label="Treo Kênh Server (1 - 5 tiếng)",
              description="Treo gửi ngầm văn bản liên tục vào kênh",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tràn Server (1 - 5 tiếng)",
              description="Treo văn bản tự do oanh tạc liên tục",
              emoji="🌊",
              value="treo_trang_server",
          ),
      ],
  )
  async def select_treo(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    kieu = select.values[0]
    await interaction.response.send_modal(ModalTreoMay(treo_type=kieu))


# --- MENU CHÍNH 3 LỰA CHỌN ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str):
    super().__init__(timeout=60)
    self.author_name = author_name

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN 1 TRONG 3 CHẾ ĐỘ SPAM...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server (Full Văn Bản)",
              description="Xả đoạn văn bản dài tùy ý vào kênh",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tràn Server (Văn Bản Tự Do)",
              description="Oanh tạc tự do văn bản tràn ngập kênh",
              emoji="🌊",
              value="spam_trang_server",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (1 - 5 tiếng)",
              description="Treo ngầm văn bản liên thanh, gõ !stop",
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
      await interaction.response.send_modal(ModalSpamServer())
    elif choice == "spam_trang_server":
      await interaction.response.send_modal(ModalSpamTrangServer())
    elif choice == "treo_gio":
      view_treo = ViewChonKieuTreo()
      await interaction.response.send_message(
          "🛡️ **[HỆ THỐNG TREO MÁY]**\nSếp muốn treo văn bản theo hình thức nào?",
          view=view_treo,
          ephemeral=True,
      )


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt văn bản dài & tràn server"
)
async def spam(interaction: discord.Interaction):
  if interaction.user.name != ADMIN_USERNAME:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân tối cao của tao, tuổi gì đòi dùng"
        " lệnh này!",
        ephemeral=True,
    )
    return

  view = ViewMenuChinh(author_name=interaction.user.name)
  await interaction.response.send_message(
      "💻 **[HỆ THỐNG ĐIỀU KHIỂN TỐI CAO]**\nSếp vui lòng chọn phương thức"
      " bên dưới:",
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


TOKEN_ENV = os.getenv("DISCORD_TOKEN")
if TOKEN_ENV:
  bot.run(TOKEN_ENV)
else:
  print("❌ Thiếu DISCORD_TOKEN!")

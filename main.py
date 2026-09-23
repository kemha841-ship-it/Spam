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

# Hình ảnh Itachi ngầu lòi do sếp cung cấp kèm hiệu ứng vòng lặp 7 màu
DEFAULT_NOI_DUNG = "🔥 **[UCHIHA ITACHI - MẮT ĐỎ HUỶ DIỆT]** Spam siêu tốc 2026!"
DEFAULT_IMAGE_URL = (
    "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHpucHRqOWp3NWlscmp4d3ltc3RrdHhscnh4M3ZrdjV0Z2xqcjJraiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Lq0h93752f6J9tijrh/giphy.gif"
)


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


def create_rainbow_embed(content: str, image_url: str):
  embed = discord.Embed(
      description=content, color=discord.Color.from_rgb(255, 0, 127)
  )
  embed.set_image(url=image_url)
  embed.set_footer(text="✨ Itachi Sharingan - Vòng lặp 7 màu cực ngầu ✨")
  return embed


# --- MODAL 1: SPAM KÊNH SERVER (0.001S KHÔNG KHỰNG) ---
class ModalSpamServer(discord.ui.Modal, title="⚡ SPAM KÊNH SERVER (0.001S)"):

  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="Ví dụ: 50",
      default="30",
      max_length=3,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    channel = interaction.channel
    embed = create_rainbow_embed(DEFAULT_NOI_DUNG, DEFAULT_IMAGE_URL)
    await interaction.followup.send(
        f"⚡ Đang xả đạn liên thanh vào **{channel.name}** ({amount} tin)...",
        ephemeral=True,
    )

    # Gửi song song cực tốc không khựng
    tasks = [
        channel.send(content=f"🔥 *({i}/{amount})*", embed=embed)
        for i in range(1, amount + 1)
    ]
    await asyncio.gather(
        *(
            asyncio.gather(t, return_exceptions=True)
            for t in chunks(tasks, 10)
        )
    )  # Bắn batch mượt mà


# --- MODAL 2: SPAM DM (0.001S KHÔNG KHỰNG) ---
class ModalSpamDM(discord.ui.Modal, title="🎯 SPAM TIN NHẮN RIÊNG DM (0.001S)"):

  so_luong = discord.ui.TextInput(
      label="Số lượng tin nhắn (Tối đa 200)",
      placeholder="Ví dụ: 50",
      default="30",
      max_length=3,
      required=True,
  )

  def __init__(self, target_member: discord.Member):
    super().__init__()
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    if not self.target_member:
      await interaction.followup.send(
          "❌ Sếp chưa chọn người nhận ở lệnh ban đầu!", ephemeral=True
      )
      return

    embed = create_rainbow_embed(DEFAULT_NOI_DUNG, DEFAULT_IMAGE_URL)
    await interaction.followup.send(
        f"🎯 Đang oanh tạc hòm thư **{self.target_member.name}** ({amount}"
        " tin)...",
        ephemeral=True,
    )

    for i in range(1, amount + 1):
      try:
        await self.target_member.send(content=f"❄️ *({i}/{amount})*", embed=embed)
        await asyncio.sleep(
            0.005
        )  # Giữ nhịp DM an toàn không bị chặn hòm thư
      except Exception:
        break
    await interaction.followup.send(
        f"✅ Hoàn tất bắn DM vào **{self.target_member.name}**!", ephemeral=True
    )


# --- MODAL 3: TREO MÁY DÀI HẠN (0.001S) ---
class ModalTreoMay(discord.ui.Modal, title="🛡️ TREO NGẦM DÀI HẠN (0.001S)"):

  so_gio = discord.ui.TextInput(
      label="Số giờ treo (Tối đa 3 tiếng)",
      placeholder="Ví dụ: 1",
      default="1",
      max_length=3,
      required=True,
  )
  hinh_thuc = discord.ui.TextInput(
      label="Gõ 's' (Server) hoặc 'd' (DM)",
      placeholder="s hoặc d",
      default="s",
      max_length=1,
      required=True,
  )

  def __init__(self, target_member=None):
    super().__init__()
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    mode = self.hinh_thuc.value.lower()
    try:
      hours = float(self.so_gio.value)
      if hours > 3.0:
        hours = 3.0
    except ValueError:
      hours = 1.0

    total_seconds = int(hours * 3600)
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True
    embed = create_rainbow_embed(DEFAULT_NOI_DUNG, DEFAULT_IMAGE_URL)

    if mode == "s":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã bật Treo Kênh 0.001s!** Kênh: **{channel.name}**. Gõ"
          " `!stop` để dừng.",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(
                content=f"⏳ **[AFK]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(0.01)
          elapsed += 0.01
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    elif mode == "d":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Chưa chọn `nguoi_nhan` ở lệnh đầu để treo DM!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🛡️ **Đã bật Treo DM 0.001s!** Mục tiêu:"
          f" **{self.target_member.name}**. Gõ `!stop` để dừng.",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(
                content=f"⏳ **[AFK DM]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(0.1)
          elapsed += 0.1
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_dm())


# Hàm hỗ trợ chia nhỏ task để gửi mượt
def chunks(lst, n):
  for i in range(0, len(lst), n):
    yield lst[i : i + n]


# --- MENU CHÍNH BƯỚC 1 (HIỆN THẲNG MODAL KHÔNG MẤT KHUNG NHẬP) ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN 1 TRONG 3 CHẾ ĐỘ 0.001S...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server (0.001s)",
              description="Xả đạn Itachi viền 7 màu vào kênh",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng DM (0.001s)",
              description="Xả đạn Itachi vào hòm thư mục tiêu",
              emoji="🎯",
              value="spam_dm",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (0.001s)",
              description="Treo ngầm liên thanh không khựng",
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
    elif choice == "spam_dm":
      if not self.target_member:
        await interaction.response.send_message(
            "❌ Sếp ơi, chế độ Spam DM bắt buộc phải chọn `nguoi_nhan` ngay ở"
            " bảng lệnh đầu tiên nhé!",
            ephemeral=True,
        )
        return
      await interaction.response.send_modal(
          ModalSpamDM(target_member=self.target_member)
      )
    elif choice == "treo_gio":
      await interaction.response.send_modal(
          ModalTreoMay(target_member=self.target_member)
      )


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt Itachi 0.001s (Không khựng)"
)
@app_commands.describe(
    nguoi_nhan="Chọn người nhận (Bắt buộc nếu dùng tính năng DM hoặc Treo DM)"
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
      "💻 **[HỆ THỐNG ĐIỀU KHIỂN TỐI CAO ITACHI]**\nSếp vui lòng chọn phương"
      " thức bên dưới:",
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

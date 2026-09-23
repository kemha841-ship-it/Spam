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

# Đã thay chuẩn ảnh GIF/Video Itachi Sharingan ngầu lòi theo ý sếp
ITACHI_IMAGE_URL = (
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3BlbDZ4aXJ6bHRwMXMyZmd2NDlnbTNlYW9xZ3VpcGNqcWNqOWk5OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VChsIl9WnreDJdIOyA/giphy.gif"
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


def create_itachi_embed(content: str):
  embed = discord.Embed(
      description=content, color=discord.Color.from_rgb(180, 0, 0)
  )
  embed.set_image(url=ITACHI_IMAGE_URL)
  embed.set_footer(text="✨ Uchiha Itachi - Sharingan Độc Quyền ✨")
  return embed


def chunks(lst, n):
  for i in range(0, len(lst), n):
    yield lst[i : i + n]


# --- MODAL 1: SPAM SERVER ---
class ModalSpamServer(discord.ui.Modal, title="⚡ SPAM KÊNH SERVER (ITACHI)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung chữ muốn spam",
      placeholder="Nhập nội dung vào đây...",
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
    embed = create_itachi_embed(content)
    await interaction.followup.send(
        f"⚡ Đang xả {amount} tin Itachi vào kênh **{channel.name}**...",
        ephemeral=True,
    )

    tasks = [
        channel.send(content=f"🔥 *({i}/{amount})*", embed=embed)
        for i in range(1, amount + 1)
    ]
    for batch in chunks(tasks, 10):
      await asyncio.gather(*(asyncio.gather(t, return_exceptions=True) for t in batch))
      await asyncio.sleep(0.001)


# --- MODAL 2: SPAM DM ---
class ModalSpamDM(discord.ui.Modal, title="🎯 SPAM DM (ITACHI)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung chữ gửi vào hòm thư",
      placeholder="Nhập nội dung vào đây...",
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

  def __init__(self, target_member: discord.Member):
    super().__init__()
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

    if not self.target_member:
      await interaction.followup.send(
          "❌ Sếp chưa chọn `nguoi_nhan` ở lệnh ban đầu!", ephemeral=True
      )
      return

    embed = create_itachi_embed(content)
    await interaction.followup.send(
        f"🎯 Đang oanh tạc hòm thư **{self.target_member.name}** ({amount}"
        " tin)...",
        ephemeral=True,
    )

    for i in range(1, amount + 1):
      try:
        await self.target_member.send(content=f"❄️ *({i}/{amount})*", embed=embed)
        await asyncio.sleep(0.01)
      except Exception:
        break
    await interaction.followup.send(
        f"✅ Hoàn tất gửi DM vào **{self.target_member.name}**!", ephemeral=True
    )


# --- MODAL 3: TREO MÁY DÀI HẠN (1 ĐẾN 5 TIẾNG) ---
class ModalTreoMay(discord.ui.Modal, title="🛡️ TREO MÁY DÀI HẠN (1 - 5 TIẾNG)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung chữ treo ngầm",
      placeholder="Nhập nội dung treo...",
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

  def __init__(self, treo_type: str, target_member=None):
    super().__init__()
    self.treo_type = treo_type
    self.target_member = target_member

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
    embed = create_itachi_embed(content)
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
            await channel.send(
                content=f"⏳ **[AFK ITACHI]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(0.5)
          elapsed += 0.5
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    # 2. Treo DM
    elif self.treo_type == "treo_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp chưa chọn `nguoi_nhan` ở bảng lệnh đầu tiên để treo DM!",
            ephemeral=True,
        )
        return
      await interaction.followup.send(
          f"🛡️ **Đã bật Treo DM mục tiêu {self.target_member.name} trong"
          f" {hours} tiếng!**\n- Gõ `!stop` để dừng bất cứ lúc nào.",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(
                content=f"⏳ **[AFK DM ITACHI]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(0.5)
          elapsed += 0.5
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_dm())


# --- VIEW CHỌN HÌNH THỨC TREO MÁY ---
class ViewChonKieuTreo(discord.ui.View):

  def __init__(self, target_member=None):
    super().__init__(timeout=60)
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🛡️ CHỌN HÌNH THỨC TREO MÁY...",
      options=[
          discord.SelectOption(
              label="Treo Kênh Server (1 - 5 tiếng)",
              description="Treo gửi ngầm liên tục vào kênh",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tin Nhắn Riêng DM (1 - 5 tiếng)",
              description="Treo gửi ngầm liên tục vào DM",
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
        ModalTreoMay(treo_type=kieu, target_member=self.target_member)
    )


# --- MENU CHÍNH 3 LỰA CHỌN ĐẦY ĐỦ ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN 1 TRONG 3 CHẾ ĐỘ...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server",
              description="Xả đạn Itachi viền đỏ vào kênh",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng DM",
              description="Xả đạn Itachi vào hòm thư mục tiêu",
              emoji="🎯",
              value="spam_dm",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (1 - 5 tiếng)",
              description="Treo ngầm liên thanh, gõ !stop để dừng",
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
      view_treo = ViewChonKieuTreo(target_member=self.target_member)
      await interaction.response.send_message(
          "🛡️ **[HỆ THỐNG TREO MÁY]**\nSếp muốn treo theo hình thức nào?",
          view=view_treo,
          ephemeral=True,
      )


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt Itachi (Menu thả xuống)"
)
@app_commands.describe(
    nguoi_nhan="Chọn người nhận (Bắt buộc nếu dùng tính năng Spam DM hoặc Treo DM)"
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

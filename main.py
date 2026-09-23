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

# Mặc định ảnh Itachi ngầu lòi
DEFAULT_IMAGE_URL = (
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHpucHRqOWp3NWlscmp4d3ltc3RrdHhscnh4M3ZrdjV0Z2xqcjJraiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Lq0h93752f6J9tijrh/giphy.gif"
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


def create_rainbow_embed(content: str):
  embed = discord.Embed(
      description=content, color=discord.Color.from_rgb(255, 0, 127)
  )
  embed.set_image(url=DEFAULT_IMAGE_URL)
  embed.set_footer(text="✨ Itachi Sharingan - Vòng lặp 7 màu độc quyền ✨")
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
    embed = create_rainbow_embed(content)
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

    embed = create_rainbow_embed(content)
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


# --- MODAL 3: TREO MÁY NGẦM ---
class ModalTreoMay(discord.ui.Modal, title="🛡️ TREO NGẦM DÀI HẠN (ITACHI)"):

  noi_dung = discord.ui.TextInput(
      label="Nhập nội dung chữ treo ngầm",
      placeholder="Nhập nội dung treo...",
      style=discord.TextStyle.paragraph,
      required=True,
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    channel = interaction.channel
    embed = create_rainbow_embed(content)
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True

    await interaction.followup.send(
        f"🛡️ **Đã bật Treo Ngầm 0.001s** tại kênh **{channel.name}**!\nGõ"
        " `!stop` để dừng.",
        ephemeral=True,
    )

    async def bg_treo():
      count = 0
      while active_tasks.get(task_id, False):
        try:
          count += 1
          await channel.send(
              content=f"⏳ **[AFK ITACHI]** *(Lần {count})*", embed=embed
          )
        except Exception:
          break
        await asyncio.sleep(0.05)

    asyncio.create_task(bg_treo())


# --- SELECT MENU GIAO DIỆN CŨ ĐẦY ĐỦ 3 CHẾ ĐỘ ---
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
      await interaction.response.send_modal(ModalTreoMay())


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt Itachi 0.001s (Menu thả xuống)"
)
@app_commands.describe(
    nguoi_nhan="Chọn người nhận (Bắt buộc nếu dùng tính năng Spam DM)"
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

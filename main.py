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

ITACHI_IMAGE_URL = (
    "https://media1.giphy.com/media/VChsIl9WnreDJdIOyA/giphy.gif"
)


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
        "🛑 **[HỆ THỐNG]** Đã hủy khẩn cấp toàn bộ các tiến trình treo ngầm!"
    )
  else:
    await ctx.send("⚠️ Không có tiến trình treo ngầm nào đang chạy cả!")


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


class ModalSpamServer(discord.ui.Modal, title="⚡ SPAM KÊNH SERVER"):
  noi_dung = discord.ui.TextInput(
      label="Nội dung spam",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng (Tối đa 200)", default="30", max_length=3, required=True
  )

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      amount = min(int(self.so_luong.value), 200)
    except ValueError:
      amount = 10

    channel = interaction.channel
    embed = create_itachi_embed(content)
    await interaction.followup.send(
        f"⚡ Đang xả {amount} tin vào kênh **{channel.name}**...", ephemeral=True
    )

    tasks = [
        channel.send(content=f"{content}\n🔥 *({i}/{amount})*", embed=embed)
        for i in range(1, amount + 1)
    ]
    for batch in chunks(tasks, 10):
      await asyncio.gather(
          *(asyncio.gather(t, return_exceptions=True) for t in batch)
      )
      await asyncio.sleep(0.001)


class ModalSpamDM(discord.ui.Modal, title="🎯 SPAM TIN NHẮN RIÊNG DM"):
  noi_dung = discord.ui.TextInput(
      label="Nội dung gửi DM",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng (Tối đa 200)", default="30", max_length=3, required=True
  )

  def __init__(self, target_member: discord.Member):
    super().__init__()
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      amount = min(int(self.so_luong.value), 200)
    except ValueError:
      amount = 10

    if not self.target_member:
      await interaction.followup.send(
          "❌ Sếp chưa chọn người nhận ở lệnh ban đầu!", ephemeral=True
      )
      return

    embed = create_itachi_embed(content)
    await interaction.followup.send(
        f"🎯 Đang oanh tạc hòm thư **{self.target_member.name}**...",
        ephemeral=True,
    )

    success_count = 0
    for i in range(1, amount + 1):
      try:
        await self.target_member.send(
            content=f"{content}\n❄️ *({i}/{amount})*", embed=embed
        )
        success_count += 1
        await asyncio.sleep(0.05)
      except Exception:
        # Nếu lỗi DM (do người nhận tắt nguồn tin nhắn riêng), thông báo ngay lập tức cho sếp biết
        await interaction.followup.send(
            f"❌ **Thất bại!** Không thể gửi DM cho **{self.target_member.name}**"
            " vì họ đã chặn tin nhắn từ thành viên trong server hoặc tắt DM.",
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        f"✅ Đã gửi thành công {success_count}/{amount} tin vào hòm thư"
        f" **{self.target_member.name}**!",
        ephemeral=True,
    )


class ModalTreoMay(discord.ui.Modal, title="🛡️ TREO MÁY DÀI HẠN"):
  noi_dung = discord.ui.TextInput(
      label="Nội dung treo ngầm",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  so_gio = discord.ui.TextInput(
      label="Số giờ (1 đến 5 tiếng)", default="1", max_length=1, required=True
  )

  def __init__(self, treo_type: str, target_member=None):
    super().__init__()
    self.treo_type = treo_type
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    content = self.noi_dung.value
    try:
      hours = max(1, min(int(self.so_gio.value), 5))
    except ValueError:
      hours = 1

    total_seconds = hours * 3600
    embed = create_itachi_embed(content)
    task_id = f"task_{interaction.user.id}_{asyncio.get_event_loop().time()}"
    active_tasks[task_id] = True

    if self.treo_type == "treo_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ Đã bật treo Kênh Server **{channel.name}** trong {hours}"
          " tiếng!\n- Gõ `!stop` để dừng.",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(
                content=f"{content}\n⏳ **[AFK]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(1)
          elapsed += 1
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    elif self.treo_type == "treo_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Chưa chọn mục tiêu để treo DM!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🛡️ Đã bật treo DM mục tiêu **{self.target_member.name}** trong"
          f" {hours} tiếng!\n- Gõ `!stop` để dừng.",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(
                content=f"{content}\n⏳ **[AFK DM]** *(Lần {count})*", embed=embed
            )
          except Exception:
            break
          await asyncio.sleep(1)
          elapsed += 1
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_dm())


class ViewChonKieuTreo(discord.ui.View):

  def __init__(self, target_member=None):
    super().__init__(timeout=60)
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🛡️ CHỌN HÌNH THỨC TREO MÁY...",
      options=[
          discord.SelectOption(
              label="Treo Kênh Server (1 - 5 tiếng)",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tin Nhắn Riêng DM (1 - 5 tiếng)",
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
          "❌ Sếp chưa chọn `nguoi_nhan` ở lệnh ban đầu!", ephemeral=True
      )
      return
    await interaction.response.send_modal(
        ModalTreoMay(treo_type=kieu, target_member=self.target_member)
    )


class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN 1 TRONG 3 CHẾ ĐỘ...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server", emoji="⚡", value="spam_server"
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng DM", emoji="🎯", value="spam_dm"
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (1 - 5 tiếng)",
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
            "❌ Sếp phải chọn `nguoi_nhan` ngay từ bảng lệnh `/spam` ban đầu!",
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


@bot.tree.command(name="spam", description="Hệ thống hủy diệt Itachi")
@app_commands.describe(nguoi_nhan="Chọn người nhận để Spam DM hoặc Treo DM")
async def spam(
    interaction: discord.Interaction, nguoi_nhan: discord.Member = None
):
  if interaction.user.name != ADMIN_USERNAME:
    await interaction.response.send_message(
        "❌ **Cút!** Mày không phải chủ nhân!", ephemeral=True
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
  print(f"Bot {bot.user.name} đã sẵn sàng!")


TOKEN_ENV = os.getenv("DISCORD_TOKEN")
if TOKEN_ENV:
  bot.run(TOKEN_ENV)
else:
  print("❌ Thiếu DISCORD_TOKEN!")

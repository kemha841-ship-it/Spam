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


# --- MODAL SPAM KÉP (VỪA TEXT VỪA ẢNH - 0.01S) ---
class ModalSpamKep(discord.ui.Modal, title="⚡ ĐẠI PHÁO KÉP (TEXT + ẢNH)"):

  noi_dung = discord.ui.TextInput(
      label="Nội dung chữ muốn spam",
      placeholder="Nhập nội dung vào đây...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  link_anh = discord.ui.TextInput(
      label="Đường dẫn ảnh/GIF (Link hình ảnh)",
      placeholder="Dán link ảnh https://... vào đây",
      style=discord.TextStyle.short,
      required=True,
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng lượt gửi (Tối đa 200)",
      placeholder="Ví dụ: 30",
      default="20",
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
    image_url = self.link_anh.value
    try:
      amount = int(self.so_luong.value)
      if amount > 200:
        amount = 200
    except ValueError:
      amount = 10

    # Ghép nội dung chữ kèm link ảnh để bot gửi chung 1 tin hoặc nối tiếp nhau
    full_payload = f"🔥 **[COMBO ATTACK]** {content}\n{image_url}"

    if self.mode_type == "server":
      channel = interaction.channel
      await interaction.followup.send(
          f"⚡ Khai hỏa Đại Pháo Kép vào kênh **{channel.name}** ({amount}"
          " lượt)...",
          ephemeral=True,
      )
      for i in range(1, amount + 1):
        try:
          await channel.send(f"{full_payload} *({i}/{amount})*")
          await asyncio.sleep(0.01)  # Tốc độ 0.01s liên thanh
        except Exception:
          break

    elif self.mode_type == "dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp chưa chọn người nhận ở lệnh ban đầu!", ephemeral=True
        )
        return
      await interaction.followup.send(
          f"🎯 Oanh tạc hòm thư **{self.target_member.name}** bằng Đại Pháo"
          f" Kép ({amount} lượt)...",
          ephemeral=True,
      )
      success = 0
      for i in range(1, amount + 1):
        try:
          await self.target_member.send(f"{full_payload} *({i}/{amount})*")
          success += 1
          await asyncio.sleep(0.01)  # Tốc độ 0.01s liên thanh
        except Exception:
          break
      await interaction.followup.send(
          f"✅ Hoàn tất! Đã tống {success}/{amount} combo tin vào DM của"
          f" **{self.target_member.name}**.",
          ephemeral=True,
      )


# --- MODAL TREO GIỜ KÉP (0.01S) ---
class ModalTreoKep(discord.ui.Modal, title="🛡️ TREO NGẦM ĐẠI PHÁO KÉP"):

  noi_dung = discord.ui.TextInput(
      label="Nội dung chữ muốn treo",
      placeholder="Nhập nội dung treo...",
      style=discord.TextStyle.paragraph,
      required=True,
  )
  link_anh = discord.ui.TextInput(
      label="Đường dẫn ảnh/GIF kèm theo",
      placeholder="Dán link ảnh https://...",
      style=discord.TextStyle.short,
      required=True,
  )
  so_gio = discord.ui.TextInput(
      label="Số giờ treo (Tối đa 3 tiếng)",
      placeholder="Ví dụ: 1",
      default="1",
      max_length=3,
      required=True,
  )
  nghi_giay = discord.ui.TextInput(
      label="Số giây nghỉ giữa mỗi lần (Ví dụ: 0.01)",
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
    image_url = self.link_anh.value
    full_payload = f"⏳ **[AFK COMBO]** {content}\n{image_url}"

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

    # Treo Server Kép
    if self.treo_type == "treo_server":
      channel = interaction.channel
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo Kênh Kép 0.01s!**\n- Kênh:"
          f" **{channel.name}**\n- Tần suất: **{interval}s**/lượt.\n- Muốn"
          " dừng gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_server():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await channel.send(f"{full_payload} *(Lần {count})*")
          except Exception:
            break
          await asyncio.sleep(interval)
          elapsed += interval
        if task_id in active_tasks:
          del active_tasks[task_id]

      asyncio.create_task(bg_server())

    # Treo DM Kép
    elif self.treo_type == "treo_dm":
      if not self.target_member:
        await interaction.followup.send(
            "❌ Sếp chưa chọn `nguoi_nhan` ở bảng lệnh đầu tiên để treo DM!",
            ephemeral=True,
        )
        return
      await interaction.followup.send(
          f"🛡️ **Đã kích hoạt Treo DM Kép 0.01s!**\n- Mục tiêu:"
          f" **{self.target_member.name}**\n- Tần suất:"
          f" **{interval}s**/lượt.\n- Muốn dừng gõ: `!stop`",
          ephemeral=True,
      )

      async def bg_dm():
        elapsed = 0
        count = 0
        while elapsed < total_seconds and active_tasks.get(task_id, False):
          try:
            count += 1
            await self.target_member.send(f"{full_payload} *(Lần {count})*")
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
      placeholder="🛡️ CHỌN HÌNH THỨC TREO KÉP...",
      options=[
          discord.SelectOption(
              label="Treo Kênh Server (Text + Ảnh)",
              description="Treo tốc độ cao gửi kèm ảnh vào kênh",
              emoji="💬",
              value="treo_server",
          ),
          discord.SelectOption(
              label="Treo Tin Nhắn Riêng DM (Text + Ảnh)",
              description="Treo tốc độ cao gửi kèm ảnh vào hòm thư",
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
        ModalTreoKep(treo_type=kieu, target_member=self.target_member)
    )


# --- MENU CHÍNH BƯỚC 1 ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN CHIẾN DỊCH ĐẠI PHÁO KÉP...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server (Text + Ảnh)",
              description="Xả đạn nhanh chữ và ảnh kênh server",
              emoji="⚡",
              value="spam_server",
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng DM (Text + Ảnh)",
              description="Xả đạn nhanh chữ và ảnh vào hòm thư",
              emoji="🎯",
              value="spam_dm",
          ),
          discord.SelectOption(
              label="3. Treo Máy Dài Hạn (Text + Ảnh 0.01s)",
              description="Treo ngầm liên thanh chữ và ảnh",
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
          ModalSpamKep(mode_type="server")
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
          ModalSpamKep(mode_type="dm", target_member=self.target_member)
      )
    elif choice == "treo_gio":
      view_treo = ViewChonKieuTreo(target_member=self.target_member)
      await interaction.response.send_message(
          "🛡️ **[HỆ THỐNG TREO KÉP]**\nSếp muốn treo theo hình thức nào?",
          view=view_treo,
          ephemeral=True,
      )


@bot.tree.command(
    name="spam", description="Hệ thống hủy diệt Đại Pháo Kép (Text + Ảnh)"
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


TOKEN_ENV = os.getenv("DISCORD_TOKEN")
if TOKEN_ENV:
  bot.run(TOKEN_ENV)
else:
  print("❌ Thiếu DISCORD_TOKEN!")

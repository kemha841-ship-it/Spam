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
    await ctx.send("❌ Mày không phải chủ nhân!")
    return

  if active_tasks:
    active_tasks.clear()
    await ctx.send("🛑 Đã dừng toàn bộ tiến trình treo ngầm!")
  else:
    await ctx.send("⚠️ Không có tiến trình nào đang chạy!")


def create_itachi_embed(content: str):
  embed = discord.Embed(
      description=content, color=discord.Color.from_rgb(180, 0, 0)
  )
  embed.set_image(url=ITACHI_IMAGE_URL)
  embed.set_footer(text="✨ Uchiha Itachi ✨")
  return embed


# --- MODAL SPAM SERVER ---
class ModalSpamServer(discord.ui.Modal, title="⚡ Spam Kênh Server"):
  noi_dung = discord.ui.TextInput(
      label="Nội dung", style=discord.TextStyle.paragraph, required=True
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng (Tối đa 50)", default="10", max_length=2, required=True
  )

  async def on_submit(self, interaction: discord.Interaction):
    # Phản hồi ngay lập tức để tránh lỗi quá 3 giây
    await interaction.response.send_message(
        "⚡ Đang tiến hành spam kênh...", ephemeral=True
    )
    content = self.noi_dung.value
    try:
      amount = min(int(self.so_luong.value), 50)
    except ValueError:
      amount = 5

    channel = interaction.channel
    embed = create_itachi_embed(content)

    for i in range(1, amount + 1):
      try:
        await channel.send(
            content=f"{content}\n🔥 *({i}/{amount})*", embed=embed
        )
        await asyncio.sleep(0.1)
      except Exception:
        break


# --- MODAL SPAM DM ---
class ModalSpamDM(discord.ui.Modal, title="🎯 Spam Tin Nhắn Riêng DM"):
  noi_dung = discord.ui.TextInput(
      label="Nội dung DM", style=discord.TextStyle.paragraph, required=True
  )
  so_luong = discord.ui.TextInput(
      label="Số lượng (Tối đa 50)", default="10", max_length=2, required=True
  )

  def __init__(self, target_member: discord.Member):
    super().__init__()
    self.target_member = target_member

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🎯 Đang gửi DM tới {self.target_member.name}...", ephemeral=True
    )
    content = self.noi_dung.value
    try:
      amount = min(int(self.so_luong.value), 50)
    except ValueError:
      amount = 5

    embed = create_itachi_embed(content)
    for i in range(1, amount + 1):
      try:
        await self.target_member.send(
            content=f"{content}\n❄️ *({i}/{amount})*", embed=embed
        )
        await asyncio.sleep(0.2)
      except Exception:
        await interaction.followup.send(
            f"❌ Không thể gửi DM cho {self.target_member.name} (Họ đã chặn"
            " DM hoặc không chung server).",
            ephemeral=True,
        )
        return


# --- MENU CHÍNH ---
class ViewMenuChinh(discord.ui.View):

  def __init__(self, author_name: str, target_member=None):
    super().__init__(timeout=60)
    self.author_name = author_name
    self.target_member = target_member

  @discord.ui.select(
      placeholder="🔥 HÃY CHỌN CHẾ ĐỘ SPAM...",
      options=[
          discord.SelectOption(
              label="1. Spam Kênh Server", emoji="⚡", value="spam_server"
          ),
          discord.SelectOption(
              label="2. Spam Tin Nhắn Riêng DM", emoji="🎯", value="spam_dm"
          ),
      ],
  )
  async def select_main(
      self, interaction: discord.Interaction, select: discord.ui.Select
  ):
    if interaction.user.name != self.author_name:
      await interaction.response.send_message(
          "❌ Menu này không dành cho mày!", ephemeral=True
      )
      return

    choice = select.values[0]
    if choice == "spam_server":
      await interaction.response.send_modal(ModalSpamServer())
    elif choice == "spam_dm":
      if not self.target_member:
        await interaction.response.send_message(
            "❌ Sếp chưa chọn `nguoi_nhan` ở lệnh `/spam` ban đầu!",
            ephemeral=True,
        )
        return
      await interaction.response.send_modal(
          ModalSpamDM(target_member=self.target_member)
      )


@bot.tree.command(name="spam", description="Bảng điều khiển Itachi")
@app_commands.describe(nguoi_nhan="Chọn người nhận nếu muốn Spam DM")
async def spam(
    interaction: discord.Interaction, nguoi_nhan: discord.Member = None
):
  if interaction.user.name != ADMIN_USERNAME:
    await interaction.response.send_message(
        "❌ Mày không phải chủ nhân!", ephemeral=True
    )
    return

  view = ViewMenuChinh(
      author_name=interaction.user.name, target_member=nguoi_nhan
  )
  # Phản hồi bằng send_message trực tiếp chuẩn xác 100% không bị timeout
  await interaction.response.send_message(
      "💻 **BẢNG ĐIỀU KHIỂN ITACHI:**", view=view, ephemeral=True
  )


@bot.event
async def on_ready():
  await bot.tree.sync()
  print(f"Bot {bot.user.name} đã sẵn sàng!")


TOKEN_ENV = os.getenv("DISCORD_TOKEN")
if TOKEN_ENV:
  bot.run(TOKEN_ENV)

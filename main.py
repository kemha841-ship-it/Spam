import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "provip👑")

ADMIN_USERNAME = "huy09153"

# Giới hạn an toàn để tránh Discord rate-limit
MAX_MESSAGES = 20
MESSAGE_DELAY = 1.0

ITACHI_IMAGE_URL = (
    "https://media1.giphy.com/media/VChsIl9WnreDJdIOyA/giphy.gif"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

active_tasks = {}


# =========================
# CHECK ADMIN
# =========================

def is_admin(user: discord.User) -> bool:
    return user.name == ADMIN_USERNAME


# =========================
# EMBED
# =========================

def create_itachi_embed(content: str):
    embed = discord.Embed(
        description=content,
        color=discord.Color.from_rgb(180, 0, 0)
    )

    embed.set_image(url=ITACHI_IMAGE_URL)
    embed.set_footer(
        text="✨ Uchiha Itachi - Sharingan ✨"
    )

    return embed


# =========================
# STOP ALL TASKS
# =========================

@bot.command(name="okistop")
async def okistop_command(ctx):

    if not is_admin(ctx.author):
        await ctx.send(
            "❌ Mày không phải chủ nhân!"
        )
        return

    if not active_tasks:
        await ctx.send(
            "⚠️ Hiện tại không có tiến trình nào đang chạy."
        )
        return

    for task_id in list(active_tasks.keys()):
        active_tasks[task_id] = False

    active_tasks.clear()

    await ctx.send(
        "🛑 **[HỆ THỐNG ITACHI]** "
        "Đã dừng toàn bộ tiến trình."
    )


# =========================
# PASSWORD MODAL
# =========================

class AdminPasswordModal(
    discord.ui.Modal,
    title="🔐 Xác thực quản trị"
):

    password = discord.ui.TextInput(
        label="Mật khẩu",
        placeholder="Nhập mật khẩu admin...",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=100,
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if self.password.value != ADMIN_PASSWORD:
            await interaction.response.send_message(
                "❌ Mật khẩu không đúng.",
                ephemeral=True
            )
            return

        view = SpamControlView(
            owner_id=interaction.user.id
        )

        await interaction.response.send_message(
            "✅ **Xác thực thành công.**\n\n"
            "Chọn chức năng bên dưới.\n"
            "⚠️ Chế độ gửi tin được giới hạn để tránh "
            "Discord rate-limit.",
            view=view,
            ephemeral=True
        )


# =========================
# SPAM SERVER MODAL
# =========================

class ModalSpamServer(
    discord.ui.Modal,
    title="⚡ Gửi tin kiểm thử"
):

    noi_dung = discord.ui.TextInput(
        label="Nội dung",
        placeholder="Nhập nội dung...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000,
    )

    so_luong = discord.ui.TextInput(
        label="Số lượng (tối đa 20)",
        placeholder="Ví dụ: 5",
        default="5",
        max_length=2,
        required=True,
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:
            amount = int(self.so_luong.value)
        except ValueError:
            amount = 5

        amount = max(1, min(amount, MAX_MESSAGES))

        content = self.noi_dung.value
        channel = interaction.channel

        if channel is None:
            await interaction.response.send_message(
                "❌ Không xác định được kênh.",
                ephemeral=True
            )
            return

        task_id = (
            f"{interaction.user.id}_"
            f"{asyncio.get_running_loop().time()}"
        )

        active_tasks[task_id] = True

        await interaction.response.send_message(
            f"⚡ Bắt đầu gửi **{amount} tin** trong "
            f"{channel.mention}.\n"
            f"🛑 Dùng `!okistop` để dừng.",
            ephemeral=True
        )

        async def worker():

            try:
                for i in range(1, amount + 1):

                    if not active_tasks.get(
                        task_id,
                        False
                    ):
                        break

                    embed = create_itachi_embed(
                        content
                    )

                    try:
                        await channel.send(
                            content=(
                                f"{content}\n"
                                f"🔥 *({i}/{amount})*"
                            ),
                            embed=embed
                        )

                    except discord.Forbidden:
                        break

                    except discord.HTTPException:
                        break

                    await asyncio.sleep(
                        MESSAGE_DELAY
                    )

            finally:
                active_tasks.pop(
                    task_id,
                    None
                )

        asyncio.create_task(worker())


# =========================
# MENU CONTROL
# =========================

class SpamControlView(
    discord.ui.View
):

    def __init__(self, owner_id: int):
        super().__init__(timeout=120)
        self.owner_id = owner_id

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Menu này không phải của m.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(
        label="⚡ Gửi tin kiểm thử",
        style=discord.ButtonStyle.primary
    )
    async def send_test(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            ModalSpamServer()
        )

    @discord.ui.button(
        label="🛑 Dừng tất cả",
        style=discord.ButtonStyle.danger
    )
    async def stop_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        for task_id in list(active_tasks.keys()):
            active_tasks[task_id] = False

        active_tasks.clear()

        await interaction.response.send_message(
            "🛑 Đã dừng toàn bộ tiến trình.",
            ephemeral=True
        )


# =========================
# /spam
# =========================

@bot.tree.command(
    name="spam",
    description="Mở bảng điều khiển quản trị"
)
async def spam(
    interaction: discord.Interaction
):

    if not is_admin(interaction.user):
        await interaction.response.send_message(
            "❌ Mày không phải chủ nhân!",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(
        AdminPasswordModal()
    )


# =========================
# /ping
# =========================

@bot.tree.command(
    name="ping",
    description="Kiểm tra bot"
)
async def ping(
    interaction: discord.Interaction
):

    latency = round(
        bot.latency * 1000
    )

    await interaction.response.send_message(
        f"🏓 Pong!\n"
        f"📡 Ping: `{latency}ms`"
    )


# =========================
# READY
# =========================

@bot.event
async def on_ready():

    try:
        await bot.tree.sync()
    except Exception as e:
        print(
            f"[SYNC ERROR] {e}"
        )

    print(
        f"✅ Bot {bot.user} đã online."
    )


# =========================
# RUN
# =========================

if not DISCORD_TOKEN:
    raise RuntimeError(
        "❌ Thiếu biến DISCORD_TOKEN trên Railway."
    )

bot.run(DISCORD_TOKEN)

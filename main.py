import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands

# =========================================================
#                  CẤU HÌNH
# =========================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

ADMIN_USERNAME = "huy09153"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "provip👑")

ITACHI_IMAGE_URL = (
    "https://media1.giphy.com/media/"
    "VChsIl9WnreDJdIOyA/giphy.gif"
)

# Giới hạn an toàn
MAX_SERVER_MESSAGES = 20
MAX_DM_MESSAGES = 10

# Tối thiểu 1 giây giữa các tin
MESSAGE_DELAY = 1.0

# Chế độ theo giờ: tối đa 1 giờ/lần chạy
MAX_HOURS = 1

# =========================================================
#                  INTENTS / BOT
# =========================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

tree = bot.tree

# task đang chạy
active_tasks = {}


# =========================================================
#                  EMBED
# =========================================================

def create_embed(
    title,
    description,
    color=discord.Color.dark_red()
):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_image(url=ITACHI_IMAGE_URL)

    embed.set_footer(
        text="Itachi System • Admin Control"
    )

    return embed


# =========================================================
#                  KIỂM TRA ADMIN
# =========================================================

def is_admin(user):
    return user.name == ADMIN_USERNAME


# =========================================================
#                  PASSWORD MODAL
# =========================================================

class AdminPasswordModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="🔐 Xác thực Admin"
        )

        self.password = discord.ui.TextInput(
            label="Mật khẩu Admin",
            placeholder="Nhập mật khẩu...",
            style=discord.TextStyle.short,
            required=True,
            min_length=1,
            max_length=100
        )

        self.add_item(self.password)

    async def on_submit(self, interaction: discord.Interaction):

        if self.password.value != ADMIN_PASSWORD:

            embed = create_embed(
                "❌ Sai mật khẩu",
                "Mật khẩu không chính xác.",
                discord.Color.red()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        embed = create_embed(
            "✅ Xác thực thành công",
            (
                "Chào Admin 👑\n\n"
                "Chọn chế độ bên dưới để tiếp tục."
            ),
            discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ViewMenuChinh(
                interaction.user
            ),
            ephemeral=True
        )


# =========================================================
#                  MODAL SPAM SERVER
# =========================================================

class ModalSpamServer(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="⚡ Spam Server"
        )

        self.message = discord.ui.TextInput(
            label="Nội dung tin nhắn",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.amount = discord.ui.TextInput(
            label=f"Số lần (1-{MAX_SERVER_MESSAGES})",
            placeholder="Ví dụ: 10",
            style=discord.TextStyle.short,
            required=True,
            max_length=3
        )

        self.add_item(self.message)
        self.add_item(self.amount)

    async def on_submit(self, interaction):

        try:
            amount = int(self.amount.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Số lượng phải là số.",
                ephemeral=True
            )

            return

        if amount < 1 or amount > MAX_SERVER_MESSAGES:

            await interaction.response.send_message(
                f"❌ Chỉ được từ 1 đến {MAX_SERVER_MESSAGES} tin.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        if channel is None:

            await interaction.response.send_message(
                "❌ Không xác định được kênh.",
                ephemeral=True
            )

            return

        task_key = (
            interaction.guild.id
            if interaction.guild
            else interaction.user.id
        )

        stop_event = asyncio.Event()

        active_tasks[task_key] = stop_event

        await interaction.response.send_message(
            embed=create_embed(
                "⚡ Đang chạy Spam Server",
                (
                    f"📨 Nội dung: `{self.message.value}`\n"
                    f"🔢 Số lượng: **{amount}**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "Dùng `!okistop` để dừng."
                ),
                discord.Color.orange()
            ),
            ephemeral=True
        )

        try:

            for i in range(amount):

                if stop_event.is_set():
                    break

                try:

                    await channel.send(
                        self.message.value
                    )

                except discord.Forbidden:
                    break

                except discord.HTTPException:
                    await asyncio.sleep(2)
                    continue

                await asyncio.sleep(
                    MESSAGE_DELAY
                )

        finally:

            active_tasks.pop(
                task_key,
                None
            )


# =========================================================
#                  MODAL SPAM DM
# =========================================================

class ModalSpamDM(discord.ui.Modal):

    def __init__(self, target_member):

        super().__init__(
            title="💬 Spam DM"
        )

        self.target_member = target_member

        self.message = discord.ui.TextInput(
            label="Nội dung DM",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.amount = discord.ui.TextInput(
            label=f"Số lần (1-{MAX_DM_MESSAGES})",
            placeholder="Ví dụ: 5",
            style=discord.TextStyle.short,
            required=True,
            max_length=2
        )

        self.add_item(self.message)
        self.add_item(self.amount)

    async def on_submit(self, interaction):

        try:
            amount = int(self.amount.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Số lượng phải là số.",
                ephemeral=True
            )

            return

        if amount < 1 or amount > MAX_DM_MESSAGES:

            await interaction.response.send_message(
                f"❌ Chỉ được từ 1 đến {MAX_DM_MESSAGES} tin.",
                ephemeral=True
            )

            return

        task_key = interaction.user.id

        stop_event = asyncio.Event()

        active_tasks[task_key] = stop_event

        await interaction.response.send_message(
            embed=create_embed(
                "💬 Đang chạy Spam DM",
                (
                    f"👤 Người nhận: **{self.target_member}**\n"
                    f"📨 Số lượng: **{amount}**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "Dùng `!okistop` để dừng."
                ),
                discord.Color.blurple()
            ),
            ephemeral=True
        )

        try:

            try:
                dm = await self.target_member.create_dm()

            except discord.HTTPException:

                return

            for i in range(amount):

                if stop_event.is_set():
                    break

                try:

                    await dm.send(
                        self.message.value
                    )

                except discord.Forbidden:

                    break

                except discord.HTTPException:

                    await asyncio.sleep(2)
                    continue

                await asyncio.sleep(
                    MESSAGE_DELAY
                )

        finally:

            active_tasks.pop(
                task_key,
                None
            )


# =========================================================
#                  CHỌN NGƯỜI NHẬN DM
# =========================================================

class ModalChooseDM(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="🎯 Chọn người nhận DM"
        )

        self.username = discord.ui.TextInput(
            label="Tên Discord người nhận",
            placeholder="Nhập username chính xác...",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )

        self.add_item(self.username)

    async def on_submit(self, interaction):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Chế độ DM này cần dùng trong server.",
                ephemeral=True
            )

            return

        name = self.username.value.strip()

        target = None

        # Tìm trong member cache
        for member in guild.members:

            if (
                member.name.lower() == name.lower()
                or member.display_name.lower() == name.lower()
            ):

                target = member
                break

        if target is None:

            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Không tìm thấy người dùng",
                    (
                        f"Không tìm thấy `{name}` trong server.\n\n"
                        "Hãy nhập đúng username hoặc display name."
                    ),
                    discord.Color.red()
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ModalSpamDM(target)
        )


# =========================================================
#                  CHỌN KIỂU THEO GIỜ
# =========================================================

class ViewChonKieuTreo(discord.ui.View):

    def __init__(self, owner):
        super().__init__(timeout=120)
        self.owner = owner

    async def interaction_check(self, interaction):

        if interaction.user.id != self.owner.id:

            await interaction.response.send_message(
                "❌ Đây không phải menu của bạn.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.select(
        placeholder="⏱️ Chọn kiểu chạy theo giờ...",
        options=[
            discord.SelectOption(
                label="Server theo giờ",
                description="Chạy test trong kênh hiện tại",
                emoji="🖥️",
                value="server"
            ),
            discord.SelectOption(
                label="DM theo giờ",
                description="Chạy test DM cho người được chọn",
                emoji="💬",
                value="dm"
            )
        ]
    )
    async def select_callback(
        self,
        interaction,
        select
    ):

        mode = select.values[0]

        if mode == "server":

            await interaction.response.send_modal(
                ModalTreoServer()
            )

        elif mode == "dm":

            await interaction.response.send_modal(
                ModalTreoDM()
            )


# =========================================================
#                  TREO SERVER THEO GIỜ
# =========================================================

class ModalTreoServer(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="🖥️ Server theo giờ"
        )

        self.message = discord.ui.TextInput(
            label="Nội dung",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.hours = discord.ui.TextInput(
            label=f"Số giờ (0.1-{MAX_HOURS})",
            placeholder="Ví dụ: 0.5",
            required=True,
            max_length=4
        )

        self.add_item(self.message)
        self.add_item(self.hours)

    async def on_submit(self, interaction):

        try:
            hours = float(self.hours.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Số giờ không hợp lệ.",
                ephemeral=True
            )

            return

        if hours <= 0 or hours > MAX_HOURS:

            await interaction.response.send_message(
                f"❌ Chỉ được tối đa {MAX_HOURS} giờ.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        if channel is None:

            await interaction.response.send_message(
                "❌ Không xác định được kênh.",
                ephemeral=True
            )

            return

        task_key = (
            interaction.guild.id
            if interaction.guild
            else interaction.user.id
        )

        stop_event = asyncio.Event()

        active_tasks[task_key] = stop_event

        total_seconds = hours * 3600

        await interaction.response.send_message(
            embed=create_embed(
                "⏱️ Treo Server đã bắt đầu",
                (
                    f"📨 Nội dung: `{self.message.value}`\n"
                    f"⏰ Thời gian: **{hours} giờ**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dừng bằng `!okistop`."
                ),
                discord.Color.gold()
            ),
            ephemeral=True
        )

        async def worker():

            start = asyncio.get_running_loop().time()

            try:

                while (
                    asyncio.get_running_loop().time()
                    - start
                    < total_seconds
                ):

                    if stop_event.is_set():
                        break

                    try:

                        await channel.send(
                            self.message.value
                        )

                    except discord.Forbidden:
                        break

                    except discord.HTTPException:

                        await asyncio.sleep(2)
                        continue

                    await asyncio.sleep(
                        MESSAGE_DELAY
                    )

            finally:

                active_tasks.pop(
                    task_key,
                    None
                )

        asyncio.create_task(worker())


# =========================================================
#                  TREO DM THEO GIỜ
# =========================================================

class ModalTreoDM(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="💬 DM theo giờ"
        )

        self.username = discord.ui.TextInput(
            label="Username người nhận",
            placeholder="Nhập username chính xác...",
            required=True,
            max_length=100
        )

        self.message = discord.ui.TextInput(
            label="Nội dung DM",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.hours = discord.ui.TextInput(
            label=f"Số giờ (0.1-{MAX_HOURS})",
            placeholder="Ví dụ: 0.5",
            required=True,
            max_length=4
        )

        self.add_item(self.username)
        self.add_item(self.message)
        self.add_item(self.hours)

    async def on_submit(self, interaction):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Phải dùng trong server.",
                ephemeral=True
            )

            return

        try:
            hours = float(self.hours.value)

        except ValueError:

            await interaction.response.send_message(
                "❌ Số giờ không hợp lệ.",
                ephemeral=True
            )

            return

        if hours <= 0 or hours > MAX_HOURS:

            await interaction.response.send_message(
                f"❌ Chỉ được tối đa {MAX_HOURS} giờ.",
                ephemeral=True
            )

            return

        name = self.username.value.strip()

        target = None

        for member in guild.members:

            if (
                member.name.lower() == name.lower()
                or member.display_name.lower() == name.lower()
            ):

                target = member
                break

        if target is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy người nhận.",
                ephemeral=True
            )

            return

        task_key = interaction.user.id

        stop_event = asyncio.Event()

        active_tasks[task_key] = stop_event

        total_seconds = hours * 3600

        await interaction.response.send_message(
            embed=create_embed(
                "⏱️ Treo DM đã bắt đầu",
                (
                    f"👤 Người nhận: **{target}**\n"
                    f"⏰ Thời gian: **{hours} giờ**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dừng bằng `!okistop`."
                ),
                discord.Color.purple()
            ),
            ephemeral=True
        )

        async def worker():

            start = asyncio.get_running_loop().time()

            try:

                try:
                    dm = await target.create_dm()

                except discord.HTTPException:
                    return

                while (
                    asyncio.get_running_loop().time()
                    - start
                    < total_seconds
                ):

                    if stop_event.is_set():
                        break

                    try:

                        await dm.send(
                            self.message.value
                        )

                    except discord.Forbidden:
                        break

                    except discord.HTTPException:

                        await asyncio.sleep(2)
                        continue

                    await asyncio.sleep(
                        MESSAGE_DELAY
                    )

            finally:

                active_tasks.pop(
                    task_key,
                    None
                )

        asyncio.create_task(worker())


# =========================================================
#                  MENU CHÍNH
# =========================================================

class ViewMenuChinh(discord.ui.View):

    def __init__(self, owner):

        super().__init__(timeout=180)

        self.owner = owner

    async def interaction_check(self, interaction):

        if interaction.user.id != self.owner.id:

            await interaction.response.send_message(
                "❌ Menu này không dành cho bạn.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.select(
        placeholder="🎮 Chọn chế độ...",
        options=[

            discord.SelectOption(
                label="Spam Server",
                description="Gửi tin trong kênh hiện tại",
                emoji="⚡",
                value="server"
            ),

            discord.SelectOption(
                label="Spam DM",
                description="Chọn người nhận rồi gửi DM",
                emoji="💬",
                value="dm"
            ),

            discord.SelectOption(
                label="Spam theo giờ",
                description="Chọn Server hoặc DM và thời gian",
                emoji="⏱️",
                value="time"
            )
        ]
    )
    async def select_callback(
        self,
        interaction,
        select
    ):

        mode = select.values[0]

        if mode == "server":

            await interaction.response.send_modal(
                ModalSpamServer()
            )

        elif mode == "dm":

            await interaction.response.send_modal(
                ModalChooseDM()
            )

        elif mode == "time":

            embed = create_embed(
                "⏱️ Chế độ theo giờ",
                (
                    "Chọn nơi muốn chạy:\n\n"
                    "🖥️ **Server** — chạy trong kênh hiện tại\n"
                    "💬 **DM** — chạy cho người nhận được chọn"
                ),
                discord.Color.gold()
            )

            await interaction.response.send_message(
                embed=embed,
                view=ViewChonKieuTreo(
                    interaction.user
                ),
                ephemeral=True
            )


# =========================================================
#                  /SPAM
# =========================================================

@tree.command(
    name="spam",
    description="Mở bảng điều khiển Itachi"
)
async def spam_command(
    interaction: discord.Interaction
):

    if not is_admin(interaction.user):

        await interaction.response.send_message(
            embed=create_embed(
                "⛔ Không có quyền",
                "Chỉ Admin mới có thể sử dụng lệnh này.",
                discord.Color.red()
            ),
            ephemeral=True
        )

        return

    embed = create_embed(
        "👁️ ITACHI CONTROL PANEL",
        (
            "```ansi\n"
            "╔══════════════════════════════╗\n"
            "║       ITACHI SYSTEM          ║\n"
            "║      ADMIN CONTROL           ║\n"
            "╚══════════════════════════════╝\n"
            "```\n"
            "🔐 Vui lòng xác thực mật khẩu để mở menu."
        ),
        discord.Color.dark_red()
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

    await interaction.followup.send(
        "🔐",
        ephemeral=True
    )

    # Gửi modal thông qua interaction ban đầu
    # Vì interaction đã response nên dùng followup không mở modal được.
    # Do đó menu password được mở ngay bằng interaction.response.

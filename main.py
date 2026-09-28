import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# CONFIG
# =========================================================

TOKEN = os.getenv("DISCORD_TOKEN", "").strip()

ADMIN_USERNAME = "huy09153"
ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "provip👑"
)

MAX_SERVER_MESSAGES = 20
MAX_DM_MESSAGES = 10

# Delay tối thiểu giữa các tin
MESSAGE_DELAY = 2.0

# Chế độ theo giờ: tối đa 1 giờ
MAX_HOURS = 1.0

ITACHI_GIF = (
    "https://media1.giphy.com/media/"
    "VChsIl9WnreDJdIOyA/giphy.gif"
)


# =========================================================
# BOT
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# TASK MANAGER
# =========================================================

active_tasks = {}


def is_admin(user: discord.User) -> bool:
    return user.name == ADMIN_USERNAME


def make_embed(
    title: str,
    description: str,
    color: discord.Color = discord.Color.dark_red()
):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_image(url=ITACHI_GIF)

    embed.set_footer(
        text="👁️ ITACHI SYSTEM • ADMIN CONTROL"
    )

    return embed


# =========================================================
# PASSWORD
# =========================================================

class PasswordModal(discord.ui.Modal):

    def __init__(self):
        super().__init__(
            title="🔐 ITACHI • XÁC THỰC ADMIN"
        )

        self.password = discord.ui.TextInput(
            label="Mật khẩu",
            placeholder="Nhập mật khẩu Admin...",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )

        self.add_item(self.password)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if self.password.value != ADMIN_PASSWORD:

            await interaction.response.send_message(
                embed=make_embed(
                    "❌ XÁC THỰC THẤT BẠI",
                    "Mật khẩu không chính xác.",
                    discord.Color.red()
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=make_embed(
                "👁️ ITACHI CONTROL PANEL",
                (
                    "```ansi\n"
                    "╔══════════════════════════════╗\n"
                    "║        ITACHI SYSTEM         ║\n"
                    "║       ADMIN CONTROL          ║\n"
                    "╚══════════════════════════════╝\n"
                    "```\n"
                    "🔓 **Đã xác thực thành công.**\n\n"
                    "Chọn một trong 3 chế độ bên dưới."
                ),
                discord.Color.green()
            ),
            view=MainMenu(interaction.user),
            ephemeral=True
        )


# =========================================================
# MAIN MENU
# =========================================================

class MainMenu(discord.ui.View):

    def __init__(self, owner):
        super().__init__(timeout=180)
        self.owner = owner

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.owner.id:

            await interaction.response.send_message(
                "❌ Menu này không phải của m.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.select(
        placeholder="🔥 CHỌN CHẾ ĐỘ ITACHI...",
        options=[
            discord.SelectOption(
                label="⚡ Spam Server",
                description="Gửi tin trong kênh hiện tại",
                value="server",
                emoji="⚡"
            ),
            discord.SelectOption(
                label="💬 Spam DM",
                description="Chọn người nhận bằng tên",
                value="dm",
                emoji="💬"
            ),
            discord.SelectOption(
                label="⏱️ Spam theo giờ",
                description="Chọn Server hoặc DM",
                value="hour",
                emoji="⏱️"
            )
        ]
    )
    async def select_mode(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        mode = select.values[0]

        if mode == "server":

            await interaction.response.send_modal(
                ServerModal()
            )

        elif mode == "dm":

            await interaction.response.send_modal(
                FindMemberModal()
            )

        elif mode == "hour":

            await interaction.response.send_message(
                embed=make_embed(
                    "⏱️ CHẾ ĐỘ THEO GIỜ",
                    (
                        "Chọn nơi muốn chạy:\n\n"
                        "🖥️ **Server** — kênh hiện tại\n"
                        "💬 **DM** — người nhận được chọn"
                    ),
                    discord.Color.gold()
                ),
                view=HourTypeMenu(
                    interaction.user
                ),
                ephemeral=True
            )


# =========================================================
# SERVER SPAM MODAL
# =========================================================

class ServerModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="⚡ ITACHI • SERVER"
        )

        self.content = discord.ui.TextInput(
            label="Nội dung",
            placeholder="Nhập nội dung cần gửi...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.amount = discord.ui.TextInput(
            label=f"Số lượng (1-{MAX_SERVER_MESSAGES})",
            placeholder="Ví dụ: 5",
            required=True,
            max_length=2
        )

        self.add_item(self.content)
        self.add_item(self.amount)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:
            amount = int(self.amount.value)
        except ValueError:

            await interaction.response.send_message(
                "❌ Số lượng phải là số.",
                ephemeral=True
            )

            return

        if not 1 <= amount <= MAX_SERVER_MESSAGES:

            await interaction.response.send_message(
                f"❌ Số lượng phải từ 1 đến {MAX_SERVER_MESSAGES}.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        if channel is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy kênh.",
                ephemeral=True
            )

            return

        task_id = f"server_{interaction.user.id}"

        stop_event = asyncio.Event()

        active_tasks[task_id] = stop_event

        await interaction.response.send_message(
            embed=make_embed(
                "⚡ SERVER STARTED",
                (
                    f"📍 Kênh: {channel.mention}\n"
                    f"🔢 Số tin: **{amount}**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dùng `!okistop` để dừng."
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
                        self.content.value
                    )

                except discord.Forbidden:
                    break

                except discord.HTTPException:
                    await asyncio.sleep(3)
                    continue

                await asyncio.sleep(
                    MESSAGE_DELAY
                )

        finally:

            active_tasks.pop(
                task_id,
                None
            )


# =========================================================
# TÌM MEMBER
# =========================================================

class FindMemberModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="💬 CHỌN NGƯỜI NHẬN DM"
        )

        self.name = discord.ui.TextInput(
            label="Tên Discord",
            placeholder="Nhập username hoặc display name...",
            required=True,
            max_length=100
        )

        self.add_item(self.name)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Lệnh này phải dùng trong server.",
                ephemeral=True
            )

            return

        search = self.name.value.strip().lower()

        target = None

        # Tìm member trong cache
        for member in interaction.guild.members:

            if (
                member.name.lower() == search
                or member.display_name.lower() == search
            ):

                target = member
                break

        if target is None:

            await interaction.response.send_message(
                embed=make_embed(
                    "❌ KHÔNG TÌM THẤY",
                    (
                        f"Không tìm thấy:\n"
                        f"`{self.name.value}`\n\n"
                        "Hãy nhập đúng username/display name."
                    ),
                    discord.Color.red()
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            DMModal(target)
        )


# =========================================================
# DM MODAL
# =========================================================

class DMModal(discord.ui.Modal):

    def __init__(self, target):

        super().__init__(
            title="💬 ITACHI • DM"
        )

        self.target = target

        self.content = discord.ui.TextInput(
            label="Nội dung DM",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.amount = discord.ui.TextInput(
            label=f"Số lượng (1-{MAX_DM_MESSAGES})",
            placeholder="Ví dụ: 5",
            required=True,
            max_length=2
        )

        self.add_item(self.content)
        self.add_item(self.amount)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:
            amount = int(self.amount.value)
        except ValueError:

            await interaction.response.send_message(
                "❌ Số lượng phải là số.",
                ephemeral=True
            )

            return

        if not 1 <= amount <= MAX_DM_MESSAGES:

            await interaction.response.send_message(
                f"❌ Số lượng phải từ 1 đến {MAX_DM_MESSAGES}.",
                ephemeral=True
            )

            return

        task_id = f"dm_{interaction.user.id}"

        stop_event = asyncio.Event()

        active_tasks[task_id] = stop_event

        await interaction.response.send_message(
            embed=make_embed(
                "💬 DM STARTED",
                (
                    f"👤 Người nhận: **{self.target}**\n"
                    f"🔢 Số tin: **{amount}**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dùng `!okistop` để dừng."
                ),
                discord.Color.blurple()
            ),
            ephemeral=True
        )

        try:

            dm = await self.target.create_dm()

            for i in range(amount):

                if stop_event.is_set():
                    break

                try:

                    await dm.send(
                        self.content.value
                    )

                except discord.Forbidden:
                    break

                except discord.HTTPException:
                    await asyncio.sleep(3)
                    continue

                await asyncio.sleep(
                    MESSAGE_DELAY
                )

        finally:

            active_tasks.pop(
                task_id,
                None
            )


# =========================================================
# CHỌN SERVER / DM THEO GIỜ
# =========================================================

class HourTypeMenu(discord.ui.View):

    def __init__(self, owner):

        super().__init__(timeout=120)

        self.owner = owner

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.user.id != self.owner.id:

            await interaction.response.send_message(
                "❌ Menu này không phải của m.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.select(
        placeholder="⏱️ CHỌN HÌNH THỨC...",
        options=[
            discord.SelectOption(
                label="🖥️ Server theo giờ",
                description="Chạy trong kênh hiện tại",
                value="server"
            ),
            discord.SelectOption(
                label="💬 DM theo giờ",
                description="Chạy cho một người nhận",
                value="dm"
            )
        ]
    )
    async def select_type(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        if select.values[0] == "server":

            await interaction.response.send_modal(
                HourServerModal()
            )

        else:

            await interaction.response.send_modal(
                HourDMModal()
            )


# =========================================================
# SERVER THEO GIỜ
# =========================================================

class HourServerModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="🖥️ SERVER • THEO GIỜ"
        )

        self.content = discord.ui.TextInput(
            label="Nội dung",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.hours = discord.ui.TextInput(
            label=f"Thời gian (tối đa {MAX_HOURS} giờ)",
            placeholder="Ví dụ: 0.5",
            required=True,
            max_length=4
        )

        self.add_item(self.content)
        self.add_item(self.hours)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:
            hours = float(self.hours.value)
        except ValueError:

            await interaction.response.send_message(
                "❌ Thời gian không hợp lệ.",
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
                "❌ Không tìm thấy kênh.",
                ephemeral=True
            )

            return

        task_id = f"hour_server_{interaction.user.id}"

        stop_event = asyncio.Event()

        active_tasks[task_id] = stop_event

        total_seconds = hours * 3600

        await interaction.response.send_message(
            embed=make_embed(
                "⏱️ SERVER TREO ĐÃ BẬT",
                (
                    f"📍 Kênh: {channel.mention}\n"
                    f"⏰ Thời gian: **{hours} giờ**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dùng `!okistop` để dừng."
                ),
                discord.Color.gold()
            ),
            ephemeral=True
        )

        async def worker():

            start = asyncio.get_running_loop().time()

            try:

                while (
                    asyncio.get_running_loop().time() - start
                    < total_seconds
                ):

                    if stop_event.is_set():
                        break

                    try:

                        await channel.send(
                            self.content.value
                        )

                    except discord.Forbidden:
                        break

                    except discord.HTTPException:
                        await asyncio.sleep(3)
                        continue

                    await asyncio.sleep(
                        MESSAGE_DELAY
                    )

            finally:

                active_tasks.pop(
                    task_id,
                    None
                )

        asyncio.create_task(worker())


# =========================================================
# DM THEO GIỜ
# =========================================================

class HourDMModal(discord.ui.Modal):

    def __init__(self):

        super().__init__(
            title="💬 DM • THEO GIỜ"
        )

        self.name = discord.ui.TextInput(
            label="Username người nhận",
            placeholder="Nhập username...",
            required=True,
            max_length=100
        )

        self.content = discord.ui.TextInput(
            label="Nội dung",
            placeholder="Nhập nội dung...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.hours = discord.ui.TextInput(
            label=f"Thời gian (tối đa {MAX_HOURS} giờ)",
            placeholder="Ví dụ: 0.5",
            required=True,
            max_length=4
        )

        self.add_item(self.name)
        self.add_item(self.content)
        self.add_item(self.hours)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Phải dùng trong server.",
                ephemeral=True
            )

            return

        try:
            hours = float(self.hours.value)
        except ValueError:

            await interaction.response.send_message(
                "❌ Thời gian không hợp lệ.",
                ephemeral=True
            )

            return

        if hours <= 0 or hours > MAX_HOURS:

            await interaction.response.send_message(
                f"❌ Chỉ được tối đa {MAX_HOURS} giờ.",
                ephemeral=True
            )

            return

        search = self.name.value.strip().lower()

        target = None

        for member in interaction.guild.members:

            if (
                member.name.lower() == search
                or member.display_name.lower() == search
            ):

                target = member
                break

        if target is None:

            await interaction.response.send_message(
                "❌ Không tìm thấy người nhận.",
                ephemeral=True
            )

            return

        task_id = f"hour_dm_{interaction.user.id}"

        stop_event = asyncio.Event()

        active_tasks[task_id] = stop_event

        total_seconds = hours * 3600

        await interaction.response.send_message(
            embed=make_embed(
                "⏱️ DM TREO ĐÃ BẬT",
                (
                    f"👤 Người nhận: **{target}**\n"
                    f"⏰ Thời gian: **{hours} giờ**\n"
                    f"⏱️ Delay: **{MESSAGE_DELAY}s**\n\n"
                    "🛑 Dùng `!okistop` để dừng."
                ),
                discord.Color.purple()
            ),
            ephemeral=True
        )

        async def worker():

            start = asyncio.get_running_loop().time()

            try:

                dm = await target.create_dm()

                while (
                    asyncio.get_running_loop().time() - start
                    < total_seconds
                ):

                    if stop_event.is_set():
                        break

                    try:

                        await dm.send(
                            self.content.value
                        )

                    except discord.Forbidden:
                        break

                    except discord.HTTPException:
                        await asyncio.sleep(3)
                        continue

                    await asyncio.sleep(
                        MESSAGE_DELAY
                    )

            finally:

                active_tasks.pop(
                    task_id,
                    None
                )

        asyncio.create_task(worker())


# =========================================================
# /SPAM
# =========================================================

@bot.tree.command(
    name="spam",
    description="👁️ Mở bảng điều khiển Itachi"
)
async def spam(
    interaction: discord.Interaction
):

    if not is_admin(interaction.user):

        await interaction.response.send_message(
            embed=make_embed(
                "⛔ ACCESS DENIED",
                "Mày không phải Admin.",
                discord.Color.red()
            ),
            ephemeral=True
        )

        return

    await interaction.response.send_modal(
        PasswordModal()
    )


# =========================================================
# !OKISTOP
# =========================================================

@bot.command(
    name="okistop"
)
async def okistop(
    ctx: commands.Context
):

    if not is_admin(ctx.author):
        return

    if not active_tasks:

        await ctx.send(
            embed=make_embed(
                "ℹ️ ITACHI SYSTEM",
                "Hiện không có tiến trình nào đang chạy.",
                discord.Color.greyple()
            )
        )

        return

    count = len(active_tasks)

    for event in active_tasks.values():
        event.set()

    await ctx.send(
        embed=make_embed(
            "🛑 ĐÃ DỪNG TẤT CẢ",
            (
                f"Đã gửi tín hiệu dừng cho **{count}** "
                "tiến trình đang chạy."
            ),
            discord.Color.red()
        )
    )


# =========================================================
# ERROR HANDLER
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):

    print(
        f"[SLASH ERROR] {repr(error)}"
    )

    try:

        if interaction.response.is_done():

            await interaction.followup.send(
                f"❌ Lỗi: `{error}`",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                f"❌ Lỗi: `{error}`",
                ephemeral=True
            )

    except Exception as exc:

        print(
            f"[ERROR HANDLER] {repr(exc)}"
        )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    try:

        synced = await bot.tree.sync()

        print(
            "===================================="
        )

        print(
            f"✅ BOT ONLINE: {bot.user}"
        )

        print(
            f"✅ SLASH COMMANDS: {len(synced)}"
        )

        print(
            "===================================="
        )

    except Exception as error:

        print(
            f"❌ SYNC ERROR: {repr(error)}"
        )


# =========================================================
# START
# =========================================================

if not TOKEN:

    raise RuntimeError(
        "❌ THIẾU DISCORD_TOKEN. "
        "Hãy thêm DISCORD_TOKEN vào Railway Variables."
    )

bot.run(TOKEN)

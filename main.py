import os
import asyncio
import discord
from discord import ui
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== MODAL NHẬP THÔNG TIN SPAM ====================
class SpamModal(ui.Modal, title="⚙️ BẢNG ĐIỀU KHIỂN SPAM CỰC GẮT"):
    def __init__(self, member: discord.Member):
        super().__init__()
        self.target_member = member

    # Ô nhập nội dung văn bản hoặc icon
    noidung = ui.TextInput(
        label="Nội dung/Icon muốn spam",
        style=discord.TextStyle.paragraph,
        placeholder="Dán chuỗi icon flex hoặc văn bản vào đây...",
        required=True,
        max_length=500
    )

    # Ô nhập số lần spam
    so_lan = ui.TextInput(
        label="Muốn spam bao nhiêu lần?",
        style=discord.TextStyle.short,
        placeholder="Ví dụ: 5 hoặc 10...",
        required=True,
        max_length=3
    )

    # Ô nhập số giây nghỉ giữa các lần
    giay_nghi = ui.TextInput(
        label="Giây nghỉ giữa mỗi lần (Delay)",
        style=discord.TextStyle.short,
        placeholder="Ví dụ: 2 (cách 2 giây gửi 1 lần)...",
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        text = self.noidung.value
        try:
            count = int(self.so_lan.value)
            delay = int(self.giay_nghi.value)
        except ValueError:
            await interaction.response.send_message("❌ Số lần và số giây nghỉ phải là số nguyên!", ephemeral=True)
            return

        # Giới hạn an toàn chống lạm dụng sập bot
        if count > 20:
            await interaction.response.send_message("❌ Tối đa chỉ được spam 20 lần một lúc thôi sếp ơi!", ephemeral=True)
            return

        if delay < 1:
            await interaction.response.send_message("❌ Thời gian nghỉ tối thiểu phải từ 1 giây!", ephemeral=True)
            return

        # Phản hồi ẩn để bảng modal đóng lại mượt mà
        await interaction.response.send_message(f"🚀 Đã nhận lệnh! Chuẩn bị xả đạn **{count} lần** vào {self.target_member.mention}...", ephemeral=True)

        # Tiến hành vòng lặp spam có dừng hẳn
        for i in range(1, count + 1):
            await interaction.channel.send(f"{self.target_member.mention} — {text} *(Lần {i}/{count})*")
            if i < count:
                await asyncio.sleep(delay)

        # Gửi thông báo kết thúc
        await interaction.channel.send(f"🛑 **[HỆ THỐNG]** Đã hoàn thành chiến dịch spam triệu hồi cho {self.target_member.mention}!")


# ==================== LỆNH SLASH GỌI BẢNG MODAL ====================
@bot.tree.command(name="spam", description="Mở bảng nhập nội dung và thời gian spam chuyên nghiệp")
@discord.app_commands.checks.has_permissions(administrator=True)
async def spam_command(interaction: discord.Interaction, member: discord.Member):
    modal = SpamModal(member)
    await interaction.response.send_modal(modal)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} lệnh slash cho Bot Spam.")
    except Exception as e:
        print(f"Lỗi đồng bộ: {e}")
    print(f"Bot Spam Triệu Hồi ({bot.user.name}) đã sẵn sàng quẩy!")
    await bot.change_presence(activity=discord.Game(name="/spam | Triệu hồi cực gắt"))


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Lỗi: Không tìm thấy DISCORD_TOKEN trên Railway cho con bot này!")

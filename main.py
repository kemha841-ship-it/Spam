import os
import asyncio
import discord
from discord import ui
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== MODAL NHẬP THÔNG TIN (MỞ RỘNG SỐ LƯỢNG) ====================
class SpamModal(ui.Modal, title="⚙️ BẢNG ĐIỀU KHIỂN HỐI THÚC TỐC ĐỘ"):
    def __init__(self):
        super().__init__()

    ten_nan_nhan = ui.TextInput(
        label="Tên hoặc ID Discord của nó",
        style=discord.TextStyle.short,
        placeholder="Ví dụ: ten_no_tren_discord hoặc ID...",
        required=True,
        max_length=100
    )

    noidung = ui.TextInput(
        label="Nội dung hối học bài/nhắn riêng",
        style=discord.TextStyle.paragraph,
        placeholder="Ví dụ: Vào học bài ngay lập tức!",
        required=True,
        max_length=500
    )

    so_lan = ui.TextInput(
        label="Muốn gửi bao nhiêu lần? (Tối đa 500)",
        style=discord.TextStyle.short,
        placeholder="Ví dụ: 50 hoặc 100...",
        required=True,
        max_length=4
    )

    giay_nghi = ui.TextInput(
        label="Giây nghỉ giữa mỗi lần (Khuyên dùng từ 1s)",
        style=discord.TextStyle.short,
        placeholder="Ví dụ: 1...",
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        target_name = self.ten_nan_nhan.value.strip()
        text = self.noidung.value
        try:
            count = int(self.so_lan.value)
            delay = float(self.giay_nghi.value)
        except ValueError:
            await interaction.response.send_message("❌ Số lần và số giây nghỉ phải là số hợp lệ!", ephemeral=True)
            return

        if count > 500:
            await interaction.response.send_message("❌ Sếp chơi lớn thế, tối đa em cho phép 500 lần một lúc thôi nhé!", ephemeral=True)
            return

        if delay < 0.5:
            await interaction.response.send_message("⚠️ Delay dưới 0.5 giây dễ bị Discord chặn API lắm sếp ơi, hãy để từ 1 giây trở lên cho an toàn!", ephemeral=True)
            return

        await interaction.response.send_message(f"🚀 Bắt đầu chiến dịch oanh tạc **{count}** tin nhắn vào hộp thư của **{target_name}** với tốc độ {delay}s/tin...", ephemeral=True)

        target_user = None
        if target_name.isdigit():
            target_user = interaction.guild.get_member(int(target_name))
            if not target_user:
                try:
                    target_user = await bot.fetch_user(int(target_name))
                except:
                    pass
        
        if not target_user:
            for member in interaction.guild.members:
                if target_name.lower() in member.name.lower() or (member.nick and target_name.lower() in member.nick.lower()):
                    target_user = member
                    break

        if not target_user:
            await interaction.followup.send(f"❌ Không tìm thấy user **{target_name}** trong server này!", ephemeral=True)
            return

        success_count = 0
        for i in range(1, count + 1):
            try:
                await target_user.send(f"🔔 **[HỐI THÚC HỌC BÀI]** {text} *(Tin {i}/{count})*")
                success_count += 1
            except Exception as e:
                await interaction.followup.send(f"⚠️ Dừng lại do vướng lỗi (có thể nó chặn tin nhắn): `{e}`", ephemeral=True)
                break
            
            if i < count:
                await asyncio.sleep(delay)

        await interaction.followup.send(f"✅ Đã gửi xong **{success_count}/{count}** tin nhắn riêng cho **{target_user.name}**!", ephemeral=True)


@bot.tree.command(name="spam", description="Mở bảng hối thúc qua tin nhắn riêng với số lượng lớn")
@discord.app_commands.checks.has_permissions(administrator=True)
async def spam_command(interaction: discord.Interaction):
    modal = SpamModal()
    await interaction.response.send_modal(modal)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} lệnh.")
    except Exception as e:
        print(f"Lỗi: {e}")
    print(f"Bot {bot.user.name} đã sẵn sàng cày cuốc!")
    await bot.change_presence(activity=discord.Game(name="/spam | Hối học bài"))


TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)

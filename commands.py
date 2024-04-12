from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from database import list_mahasiswa_data

# command pada menu telegram
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo, saya adalah sebuah bot! Ketik /help atau pilih /help pada menu untuk menampilkan menu')
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        ('/start', 'Mulai bot'),
        ('/help', 'Tampilkan menu'),
        ('/mahasiswa', 'Cari mahasiswa'),
    ]
    help_message = 'Silahkan pilih perintah di bawah ini:\n'
    help_message += '\n'.join([f'{command[0]} - {command[1]}' for command in commands])
    await update.message.reply_text(help_message)
async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Saya sangat suka makan')
async def mahasiswa_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['searching_nim'] = False
    await update.message.reply_text('Silahkan pilih menu ini: '
                                    '\n 1. Cari NIM Mahasiswa '
                                    '\n 2. List Mahasiswa')

# kirim pesan ke pengguna yang memilih layanan 2
async def tampil_list_mahasiswa_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mahasiswa_data = list_mahasiswa_data()
    await update.message.reply_text(mahasiswa_data)
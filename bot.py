from typing import Final
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from commands import start_command, help_command, random_command, mahasiswa_command, tampil_list_mahasiswa_data
from response_handler import handle_response, cari_mahasiswa_nim, create_connection, write_to_inbox, write_to_outbox, handle_message, error

TOKEN: Final = '7160293944:AAFOrDZGonxotFT6IEzyMmgiuRtDTJpIc40'

if __name__ == '__main__':
    print('Bot sedang berjalan...')
    app = Application.builder().token(TOKEN).build()


    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('random', random_command))
    app.add_handler(CommandHandler('mahasiswa', mahasiswa_command))
    app.add_handler(CommandHandler('2', tampil_list_mahasiswa_data))

    app.add_handler(MessageHandler(filters.Regex(r'^\d{10}$'), cari_mahasiswa_nim))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
from telegram import Update
from telegram.ext import ContextTypes
from database import create_connection, write_to_inbox, write_to_outbox, cari_mahasiswa_by_nim, list_mahasiswa_data
# from bot import BOT_USERNAME
from typing import Final

BOT_USERNAME: Final = '@riko_mca_bot'

# respon ketika user memasukkan pesan
def handle_response(text: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    processed: str = text.lower()

    if 'halo' in processed or 'hello' in processed:
        return 'Hai, senang bertemu dengan anda!'

    if 'bagaimana kabarmu?' in processed:
        return 'Aku baik'

    if 'aku suka makan nasi goreng' in processed:
        return 'Aku lebih suka mie goreng'

    if 'bagaimana caranya membuat bot?' in processed:
        return 'Ini caranya: https://youtu.be/vZtm1wuA2yc?si=cyoEDUWIdH5VyE9x'

    if context.user_data.get('searching_nim', False):
        if processed.isdigit() and len(processed) == 10:
            nim = processed
            context.user_data['searching_nim'] = False
            result = cari_mahasiswa_by_nim(nim)
            return result
        else:
            return 'NIM tidak lengkap, silahkan ketikkan ulang NIM atau pilih layanan lainnya'
    else:
        if '1' in processed or 'cari nim mahasiswa' in processed:
            context.user_data['searching_nim'] = True
            return 'Ketikkan NIM yang ingin dicari (contoh: 2105551118)'
        elif '2' in processed or 'list nim dan nama mahasiswa' in processed:
            mahasiswa_data = list_mahasiswa_data()
            return mahasiswa_data

    return 'Saya tidak mengerti apa yang anda ketik'


# menangani pesan yang diterima oleh bot, menyimpan ke database, dan memberikan respon ke user
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    connection = create_connection()

    if connection:
        try:
            if message_type == 'private':
                username = update.message.from_user.username
            elif message_type == 'group':
                username = update.message.chat.username

            write_to_inbox(connection, username, text, str(update.message.date))

            if message_type == 'group':
                if BOT_USERNAME in text:
                    new_text: str = text.replace(BOT_USERNAME, '').strip()
                    response: str = handle_response(new_text, context)
                else:
                    return
            else:
                response: str = handle_response(text, context)

            write_to_outbox(connection, BOT_USERNAME, response, str(update.message.date))

            print('Bot:', response)
            await update.message.reply_text(response)
        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()
    else:
        print("Koneksi ke database gagal")

# menu 1 cari nim mahasiswa
async def cari_mahasiswa_nim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nim = update.message.text.strip()
    write_to_inbox(create_connection(), update.message.chat.id, nim, str(update.message.date))
    result = cari_mahasiswa_by_nim(nim)
    write_to_outbox(create_connection(), BOT_USERNAME, result, str(update.message.date))
    await update.message.reply_text(result)

# menangani kesalahan yang terjadi selama eksekusi bot
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
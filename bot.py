from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import mysql.connector

TOKEN: Final = '7160293944:AAFOrDZGonxotFT6IEzyMmgiuRtDTJpIc40'
BOT_USERNAME: Final = '@riko_mca_bot'

# command pada menu telegram
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Halo, saya adalah sebuah bot!')
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Ketikkan sesuatu supaya saya bisa merespon atau pilih perintah pada bagian menu')
async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Saya sangat suka makan')

async def mahasiswa_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Silahkan pilih menu ini: '
                                    '\n 1. Cari NIM Mahasiswa '
                                    '\n 2. List Mahasiswa')

# respon ketika user memasukkan pesan
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'halo' in processed or 'hello' in processed:
        return 'Hai, senang bertemu dengan anda!'

    if 'bagaimana kabarmu?' in processed:
        return 'Aku baik'

    if 'aku suka makan nasi goreng' in processed:
        return 'Aku lebih suka mie goreng'

    if 'bagaimana caranya membuat bot?' in processed:
        return 'Ini caranya: https://youtu.be/vZtm1wuA2yc?si=cyoEDUWIdH5VyE9x'

    if '1' in processed or 'cari nim mahasiswa' in processed:
        return 'Ketikkan NIM yang ingin dicari'

    if '2' in processed or 'list nim dan nama mahasiswa' in processed:
        mahasiswa_data = list_mahasiswa_data()
        return mahasiswa_data

    return 'Saya tidak mengerti apa yang anda ketik'

# menangani setiap pesan yang diterima oleh bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)

# menangani kesalahan yang terjadi selama eksekusi bot
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# konek ke database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_mca"
        )
        return connection
    except mysql.connector.Error as error:
        print("Error:", error)
        return None

# menyimpan pesan user ke tb_inbox
def write_to_inbox(connection, user_token, message, tgl):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO tb_inbox (usertoken, message, tgl) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_token, message, tgl))
        connection.commit()
        print("Data berhasil ditambahkan ke tb_inbox")
    except mysql.connector.Error as error:
        print("Error:", error)

# menyimpan pesan dari bot ke tb_outbox
def write_to_outbox(connection, user_token, message, tgl):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO tb_outbox (usertoken, message, tgl) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_token, message, tgl))
        connection.commit()
        print("Data berhasil ditambahkan ke tb_outbox")
    except mysql.connector.Error as error:
        print("Error:", error)

# menangani pesan yang diterima oleh bot, menyimpan ke database, dan memberikan respon ke user
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    connection = create_connection()

    if connection:
        try:
            write_to_inbox(connection, update.message.chat.id, text, str(update.message.date))

            if message_type == 'group':
                if BOT_USERNAME in text:
                    new_text: str = text.replace(BOT_USERNAME, '').strip()
                    response: str = handle_response(new_text)
                else:
                    return
            else:
                response: str = handle_response(text)

            write_to_outbox(connection, BOT_USERNAME, response, str(update.message.date))

            print('Bot:', response)
            await update.message.reply_text(response)
        finally:
            connection.close()
    else:
        print("Connection to database failed.")

# async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f'Update {update} caused error {context.error}')


# menu 1 cari nim mahasiswa
def cari_mahasiswa_by_nim(nim: str) -> str:
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT nama_mhs FROM tb_mahasiswa WHERE id_mhs = %s"
            cursor.execute(query, (nim,))
            result = cursor.fetchone()
            if result:
                return f"Mahasiswa dengan NIM {nim} adalah {result[0]}"
            else:
                return f"Tidak ada mahasiswa dengan NIM {nim}"
        except mysql.connector.Error as error:
            print("Error:", error)
        finally:
            connection.close()
    else:
        return "Koneksi ke database gagal!"

# menu 1 cari nim mahasiswa
async def cari_mahasiswa_nim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nim = update.message.text.strip()
    write_to_inbox(create_connection(), update.message.chat.id, nim, str(update.message.date))
    result = cari_mahasiswa_by_nim(nim)
    write_to_outbox(create_connection(), BOT_USERNAME, result, str(update.message.date))
    await update.message.reply_text(result)


# menu 2 list mahasiswa, ambil data dari database dan digunakan untuk respon bot
def list_mahasiswa_data() -> str:
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT id_mhs, nama_mhs FROM tb_mahasiswa"
            cursor.execute(query)
            mahasiswa_data = cursor.fetchall()

            response_text = "Berikut adalah list mahasiswa: \n"
            for data in mahasiswa_data:
                response_text += f"ID: {data[0]}, Nama: {data[1]}\n"

            return response_text
        except mysql.connector.Error as error:
            print("Error:", error)
        finally:
            connection.close()
    else:
        return "Koneksi ke database gagal!"

# kirim pesan ke pengguna yang memilih layanan 2
async def tampil_list_mahasiswa_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mahasiswa_data = list_mahasiswa_data()
    await update.message.reply_text(mahasiswa_data)


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

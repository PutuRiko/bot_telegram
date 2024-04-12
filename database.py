import mysql.connector

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
def write_to_inbox(connection, username, message, tgl):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO tb_inbox (usertoken, message, tgl) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, message, tgl))
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
                response_text += f"NIM: {data[0]}, Nama: {data[1]}\n"

            return response_text
        except mysql.connector.Error as error:
            print("Error:", error)
        finally:
            connection.close()
    else:
        return "Koneksi ke database gagal!"
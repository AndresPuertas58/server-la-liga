import pymysql

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",       # o la IP del servidor
    "user": "liga_agil_user",
    "password": "Nubeware2025.",
    "database": "liga_agil_db",
    "port": 3306               # Puerto por defecto de MySQL
}

try:
    print("🔌 Intentando conectar a la base de datos MySQL...")
    connection = pymysql.connect(**DB_CONFIG)
    print("✅ Conexión exitosa a la base de datos!")

    # Probar una consulta simple
    with connection.cursor() as cursor:
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        print("🕒 Fecha y hora del servidor MySQL:", result[0])

except pymysql.MySQLError as e:
    print("❌ Error al conectar a MySQL:", e)

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("🔒 Conexión cerrada correctamente.")

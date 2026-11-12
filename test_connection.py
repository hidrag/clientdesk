from modules.db_connection import get_connection

def test_connection():
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    version(),
                    current_database(),
                    current_user;
            """)

            result = cursor.fetchone()

        print("Database connection successful!")
        print("PostgreSQL version:", result[0])
        print("Database:", result[1])
        print("User:", result[2])

    except Exception as error:
        print("Connection error:", error)

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    test_connection()

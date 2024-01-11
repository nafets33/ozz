

import psycopg2
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

# # Connect to the PostgreSQL database
def postgre_db_connect(db_params=False):
    if not db_params:
        db_params = {
            "host": "localhost",
            "database": "ozz_db",
            "user": "stefanstapinski",
            "password": "ozz",
            "port": 5432
        }
    # conn = psycopg2.connect(
    #     dbname="ozz_db",
    #     user="stefanstapinski",
    #     password="ozz",
    #     host="localhost",
    #     port=5432,
    # )
    conn = psycopg2.connect(**db_params)
    return conn

### START
# utils.init_pollen_dbs all file creations for users i.e. client_users_db
# track save

#sneakpeak == client_user_db
# client_users.db
#2 masters, audio and images

# update save_json & Appends

def postgre_db_connect(db_params=False):
    # Host
    # ec2-3-230-24-12.compute-1.amazonaws.com
    # Database
    # dcp3airkvcc1u1
    # User
    # jdudpjkxggkbrv
    # Port
    # 5432
    # Password
    # c9db217ba584b1a549f9b35536fb52b6416b7c387e9cc3c49fab82614efb167f
    # URI
    # postgres://jdudpjkxggkbrv:c9db217ba584b1a549f9b35536fb52b6416b7c387e9cc3c49fab82614efb167f@ec2-3-230-24-12.compute-1.amazonaws.com:5432/dcp3airkvcc1u1
    # Heroku CLI
    # heroku pg:psql postgresql-cubic-10426 --app ozz
    conn = psycopg2.connect(**db_params)
    return conn





## utils utils
def insert_audio(conn, audio_data, title):
    try:
        # Insert the audio data and title into the database
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO audio_files (audio_data, title) VALUES (%s, %s)", (audio_data, title))
            conn.commit()

        print(f"Audio with title '{title}' inserted successfully.")
        
    except Exception as e:
        print(f"Error inserting audio: {e}")
        conn.rollback()  # Rollback changes in case of an error

def create_table_origin_query():
    create_table_sql = """
    CREATE TABLE audio_files (
        id serial PRIMARY KEY,
        title varchar(100),
        audio_data bytea
    );
    
    """

    return {'create_video_table': create_table_sql}

def confirm_db(tables=['audio_files']):
    conn = postgre_db_connect()
    # Create a cursor
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        # Check if the table exists
        for table_name in tables:
            try:
                cursor.execute(sql.SQL("SELECT 1 FROM information_schema.tables WHERE table_name = %s"), [table_name])
                table_exists = cursor.fetchone()

                if not table_exists:
                    print("missing table ", table_name)
                    if table_name == 'audio_files':
                        sql = create_table_origin_query().get('create_video_table')
                        # Execute the table creation query
                        cursor.execute(sql)
                        conn.commit()
            except Exception as e:
                print(f"Error: {e}")
    # Close the database connection
    if conn:
        conn.close()
    
    return True

def get_all_titles(conn, table_name):
    try:
        with conn.cursor() as cursor:
            # Select all titles from the specified table
            query = f"SELECT title FROM {table_name}"
            cursor.execute(query)
            titles = cursor.fetchall()

            return titles

    except Exception as e:
        print(f"Error retrieving titles: {e}")

def get_audio_by_title(conn, table_name, selected_title):
    try:
        with conn.cursor() as cursor:
            # Select audio data based on the selected title and specified table name
            query = f"SELECT audio_data FROM {table_name} WHERE title = %s"
            cursor.execute(query, (selected_title,))
            audio_data = cursor.fetchone()

            return audio_data[0] if audio_data else None

    except Exception as e:
        print(f"Error retrieving audio data: {e}")

    # # Example usage:
    # selected_title = "Your Selected Title"
    # audio_data = get_audio_by_title(conn, selected_title)

    # if audio_data:
    #     # Save the audio data locally (replace 'your_local_file.mp3' with the desired filename)
    #     with open("your_local_file.mp3", "wb") as local_file:
    #         local_file.write(audio_data)
    #     print(f"Audio data for title '{selected_title}' saved locally.")
    # else:
    #     print(f"No audio data found for title '{selected_title}'.")

# try:
#     # Connect to the database
#     

#     # Create a cursor object
#     cursor = conn.cursor()

#     # Execute the SQL statement to create the table
#     cursor.execute(create_table_sql)

#     # Commit the changes
#     conn.commit()

#     # Close the cursor and connection
#     cursor.close()
#     conn.close()

#     print("Table 'audio_files' created successfully.")

# except psycopg2.Error as e:
#     print("Error creating table:", e)
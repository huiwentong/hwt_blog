import sqlite3

conn = sqlite3.connect('D:/HWT/repository/hwt_blog/backend/data/hwt_blog.db')
cursor = conn.cursor()

# cursor.execute("PRAGMA table_info(h5_pages)")
# columns = cursor.fetchall()

# print([col[1] for col in columns])
cursor.execute("SELECT * FROM h5_pages")
print(cursor.description)

# rows = cursor.fetchall()

# for row in rows:
#     print(row)

conn.close()


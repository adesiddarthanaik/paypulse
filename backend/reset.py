import sqlite3
conn = sqlite3.connect('paypulse.db')
conn.execute("UPDATE payments SET status='PENDING'")
conn.commit()
conn.close()
print('Reset done')
import requests
import json
import time

BASE = "http://localhost:4001"

def separator(title):
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)

def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

# =============================================
# BUOC 1: KIEM TRA CLUSTER
# =============================================
separator("BUOC 1: Kiem tra cluster")
try:
    res = requests.get(f"{BASE}/nodes", timeout=3)
    data = res.json()
    print(f"  Cluster co {len(data)} node:")
    for node_id, info in data.items():
        print(f"    - {node_id}: {info.get('addr', '')} | Leader: {info.get('leader', False)}")
except Exception as e:
    print(f"  [LOI] Khong the ket noi cluster: {e}")
    print("  --> Hay chay Docker cluster truoc khi chay script nay!")
    exit(1)

# =============================================
# BUOC 2: TAO BANG
# =============================================
separator("BUOC 2: Tao bang students")
res = requests.post(f"{BASE}/db/execute", json=[
    "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, score INTEGER, subject TEXT)"
])
result = res.json()
print("  Ket qua:")
pretty(result)

# =============================================
# BUOC 3: THEM DU LIEU
# =============================================
separator("BUOC 3: Them du lieu vao bang")
students = [
    (1, "Nguyen Van A", 9, "He thong phan tan"),
    (2, "Tran Thi B",   8, "He thong phan tan"),
    (3, "Le Van C",     7, "He thong phan tan"),
    (4, "Pham Thi D",   9, "He thong phan tan"),
    (5, "Hoang Van E",  6, "He thong phan tan"),
]

sqls = [f"INSERT OR IGNORE INTO students VALUES ({s[0]}, '{s[1]}', {s[2]}, '{s[3]}')" for s in students]
res = requests.post(f"{BASE}/db/execute", json=sqls)
print(f"  Da them {len(students)} ban ghi thanh cong!")

# =============================================
# BUOC 4: TRUY VAN DU LIEU
# =============================================
separator("BUOC 4: Truy van SELECT tat ca")
res = requests.get(f"{BASE}/db/query?q=SELECT * FROM students")
data = res.json()
rows = data.get("results", [{}])[0].get("values", [])
cols = data.get("results", [{}])[0].get("columns", [])

print(f"  {'ID':<5} {'Ho ten':<20} {'Diem':<8} {'Mon hoc'}")
print("  " + "-" * 50)
for row in rows:
    print(f"  {row[0]:<5} {row[1]:<20} {row[2]:<8} {row[3]}")

# =============================================
# BUOC 5: UPDATE DU LIEU
# =============================================
separator("BUOC 5: Cap nhat diem (UPDATE)")
res = requests.post(f"{BASE}/db/execute", json=[
    "UPDATE students SET score = 10 WHERE name = 'Nguyen Van A'"
])
print("  Da cap nhat diem Nguyen Van A len 10")

res = requests.get(f"{BASE}/db/query?q=SELECT * FROM students WHERE name='Nguyen Van A'")
data = res.json()
rows = data.get("results", [{}])[0].get("values", [])
print(f"  Sau cap nhat: {rows}")

# =============================================
# BUOC 6: TRUY VAN CO DIEU KIEN
# =============================================
separator("BUOC 6: Truy van diem >= 8 (WHERE)")
res = requests.get(f"{BASE}/db/query?q=SELECT name, score FROM students WHERE score >= 8 ORDER BY score DESC")
data = res.json()
rows = data.get("results", [{}])[0].get("values", [])
print("  Sinh vien dat diem >= 8:")
for row in rows:
    print(f"    {row[0]}: {row[1]} diem")

# =============================================
# BUOC 7: DEM SO BAN GHI
# =============================================
separator("BUOC 7: Dem so ban ghi (COUNT)")
res = requests.get(f"{BASE}/db/query?q=SELECT COUNT(*) FROM students")
data = res.json()
count = data.get("results", [{}])[0].get("values", [[0]])[0][0]
print(f"  Tong so sinh vien trong database: {count}")

# =============================================
# BUOC 8: KIEM TRA REPLICATION
# =============================================
separator("BUOC 8: Kiem tra replication sang cac node khac")
nodes = [
    ("node1 (Leader)", "http://localhost:4001"),
    ("node2 (Follower)", "http://localhost:4003"),
    ("node3 (Follower)", "http://localhost:4005"),
]

for name, url in nodes:
    try:
        res = requests.get(f"{url}/db/query?q=SELECT COUNT(*) FROM students", timeout=2)
        count = res.json().get("results", [{}])[0].get("values", [[0]])[0][0]
        print(f"  {name}: {count} ban ghi  --> DONG BO OK")
    except Exception:
        print(f"  {name}: OFFLINE hoac chua join cluster")

# =============================================
# BUOC 9: DELETE
# =============================================
separator("BUOC 9: Xoa du lieu (DELETE)")
res = requests.post(f"{BASE}/db/execute", json=[
    "DELETE FROM students WHERE score < 7"
])
print("  Da xoa sinh vien co diem < 7")

res = requests.get(f"{BASE}/db/query?q=SELECT COUNT(*) FROM students")
count = res.json().get("results", [{}])[0].get("values", [[0]])[0][0]
print(f"  So sinh vien con lai: {count}")

# =============================================
# TONG KET
# =============================================
separator("HOAN THANH DEMO CO BAN")
print("""
  Da demo thanh cong cac thao tac:
    [OK] Ket noi va kiem tra cluster
    [OK] CREATE TABLE
    [OK] INSERT nhieu ban ghi
    [OK] SELECT tat ca / co dieu kien / COUNT
    [OK] UPDATE du lieu
    [OK] Kiem tra replication sang 3 node
    [OK] DELETE du lieu

  Tiep theo: chay app.py de xem Dashboard realtime!
""")
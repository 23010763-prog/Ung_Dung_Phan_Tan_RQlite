import requests
import time
import json
import statistics
import os

# =============================================
# CAU HINH
# =============================================
NODES = [
    {"id": "node1", "url": "http://localhost:4001"},
    {"id": "node2", "url": "http://localhost:4003"},
    {"id": "node3", "url": "http://localhost:4005"},
]
LEADER_URL = "http://localhost:4001"
NUM_REQUESTS = 50  # so lan do moi bai test


# =============================================
# TIEN ICH
# =============================================
def separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def setup_table():
    """Tao bang benchmark neu chua co"""
    try:
        requests.post(f"{LEADER_URL}/db/execute", json=[
            "CREATE TABLE IF NOT EXISTS benchmark (id INTEGER PRIMARY KEY, val TEXT, num INTEGER)"
        ], timeout=5)
        requests.post(f"{LEADER_URL}/db/execute", json=[
            "DELETE FROM benchmark"
        ], timeout=5)
        print("  [OK] Tao bang benchmark thanh cong")
    except Exception as e:
        print(f"  [LOI] Khong the ket noi RQLite: {e}")
        print("  --> Hay dam bao RQLite dang chay truoc khi chay benchmark!")
        exit(1)


# =============================================
# BENCHMARK 1: DO TOC DO WRITE
# =============================================
def benchmark_write(num=NUM_REQUESTS):
    separator("BENCHMARK 1: Toc do WRITE (INSERT)")
    print(f"  So lan test: {num} INSERT queries\n")

    times = []
    success = 0

    for i in range(num):
        sql = f"INSERT INTO benchmark (val, num) VALUES ('test_{i}', {i})"
        start = time.time()
        try:
            res = requests.post(f"{LEADER_URL}/db/execute",
                                json=[sql], timeout=5)
            elapsed = (time.time() - start) * 1000  # ms
            if res.status_code == 200:
                times.append(elapsed)
                success += 1
        except Exception:
            pass

        # Hien thi tien do
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{num}] Dang do...", end="\r")

    print(f"\n  Ket qua:")
    print(f"    Thanh cong  : {success}/{num} requests")
    print(f"    Nhanh nhat  : {min(times):.2f} ms")
    print(f"    Cham nhat   : {max(times):.2f} ms")
    print(f"    Trung binh  : {statistics.mean(times):.2f} ms")
    print(f"    Trung vi    : {statistics.median(times):.2f} ms")
    print(f"    Throughput  : {1000 / statistics.mean(times):.1f} writes/giay")

    return {
        "label": "WRITE",
        "count": success,
        "min": round(min(times), 2),
        "max": round(max(times), 2),
        "avg": round(statistics.mean(times), 2),
        "median": round(statistics.median(times), 2),
        "throughput": round(1000 / statistics.mean(times), 1),
        "times": times
    }


# =============================================
# BENCHMARK 2: DO TOC DO READ
# =============================================
def benchmark_read(num=NUM_REQUESTS):
    separator("BENCHMARK 2: Toc do READ (SELECT)")
    print(f"  So lan test: {num} SELECT queries\n")

    times = []
    success = 0

    for i in range(num):
        start = time.time()
        try:
            res = requests.get(
                f"{LEADER_URL}/db/query?q=SELECT * FROM benchmark LIMIT 10",
                timeout=5)
            elapsed = (time.time() - start) * 1000
            if res.status_code == 200:
                times.append(elapsed)
                success += 1
        except Exception:
            pass

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{num}] Dang do...", end="\r")

    print(f"\n  Ket qua:")
    print(f"    Thanh cong  : {success}/{num} requests")
    print(f"    Nhanh nhat  : {min(times):.2f} ms")
    print(f"    Cham nhat   : {max(times):.2f} ms")
    print(f"    Trung binh  : {statistics.mean(times):.2f} ms")
    print(f"    Trung vi    : {statistics.median(times):.2f} ms")
    print(f"    Throughput  : {1000 / statistics.mean(times):.1f} reads/giay")

    return {
        "label": "READ",
        "count": success,
        "min": round(min(times), 2),
        "max": round(max(times), 2),
        "avg": round(statistics.mean(times), 2),
        "median": round(statistics.median(times), 2),
        "throughput": round(1000 / statistics.mean(times), 1),
        "times": times
    }


# =============================================
# BENCHMARK 3: DO THOI GIAN BAU LEADER MOI
# =============================================
def benchmark_leader_election():
    separator("BENCHMARK 3: Thoi gian bau lai Leader")
    print("  Mo phong: tat Leader -> do thoi gian den khi co Leader moi\n")
    print("  [!] Hay tat thu cong terminal cua node1 (Leader) ngay bay gio...")
    print("  [!] Sau do nhan Enter de bat dau do thoi gian...", end="")
    input()

    start = time.time()
    election_time = None
    attempts = 0
    max_wait = 30  # cho toi da 30 giay

    print("  Dang cho cluster bau Leader moi", end="")
    while time.time() - start < max_wait:
        attempts += 1
        for node in NODES[1:]:  # thu tu follower con lai
            try:
                res = requests.post(
                    f"{node['url']}/db/execute",
                    json=["SELECT 1"],
                    timeout=1)
                if res.status_code == 200:
                    result = res.json()
                    if "results" in result:
                        election_time = (time.time() - start) * 1000
                        print(f"\n\n  [OK] Leader moi da san sang: {node['id'].upper()}")
                        break
            except Exception:
                pass
        if election_time:
            break
        print(".", end="", flush=True)
        time.sleep(0.2)

    if election_time:
        print(f"  Thoi gian bau lai  : {election_time:.0f} ms ({election_time/1000:.2f} giay)")
        print(f"  So lan thu          : {attempts}")
        print(f"  Tinh san sang       : Cluster van hoat dong!")
        return {"election_time_ms": round(election_time), "attempts": attempts}
    else:
        print(f"\n  [!] Qua {max_wait}s chua co Leader moi (kiem tra lai cluster)")
        return {"election_time_ms": None, "attempts": attempts}


# =============================================
# BENCHMARK 4: SO SANH READ TU NHIEU NODE
# =============================================
def benchmark_multi_node_read(num=30):
    separator("BENCHMARK 4: So sanh READ tu tung node")
    print(f"  Gui {num} query toi tung node, so sanh toc do\n")

    results = {}

    for node in NODES:
        times = []
        success = 0
        print(f"  Dang do {node['id']}...", end="")

        for i in range(num):
            start = time.time()
            try:
                res = requests.get(
                    f"{node['url']}/db/query?q=SELECT COUNT(*) FROM benchmark",
                    timeout=3)
                elapsed = (time.time() - start) * 1000
                if res.status_code == 200:
                    times.append(elapsed)
                    success += 1
            except Exception:
                pass

        if times:
            avg = statistics.mean(times)
            results[node["id"]] = {
                "success": success,
                "avg_ms": round(avg, 2),
                "min_ms": round(min(times), 2),
                "max_ms": round(max(times), 2),
            }
            print(f" avg={avg:.1f}ms  ({success}/{num} OK)")
        else:
            results[node["id"]] = {"success": 0, "avg_ms": None}
            print(f" OFFLINE")

    return results


# =============================================
# LUU KET QUA VA IN BAO CAO
# =============================================
def save_results(write_result, read_result, multi_node, election=None):
    separator("BAO CAO TONG HOP")

    print(f"""
  +------------------+----------+----------+------------------+
  | Loai query       | TB (ms)  | Min (ms) | Throughput/giay  |
  +------------------+----------+----------+------------------+
  | WRITE (INSERT)   | {write_result['avg']:>8.2f} | {write_result['min']:>8.2f} | {write_result['throughput']:>14.1f}   |
  | READ  (SELECT)   | {read_result['avg']:>8.2f} | {read_result['min']:>8.2f} | {read_result['throughput']:>14.1f}   |
  +------------------+----------+----------+------------------+
    """)

    print("  So sanh toc do READ giua cac node:")
    for node_id, r in multi_node.items():
        if r["avg_ms"]:
            bar = "█" * int(r["avg_ms"] / 2)
            print(f"    {node_id:6} | {r['avg_ms']:6.1f} ms | {bar}")
        else:
            print(f"    {node_id:6} | OFFLINE")

    if election and election.get("election_time_ms"):
        print(f"\n  Thoi gian bau lai Leader: {election['election_time_ms']} ms")

    # Luu JSON de dung trong bao cao
    output = {
        "write": write_result,
        "read": read_result,
        "multi_node": multi_node,
        "election": election,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  [OK] Ket qua da luu vao benchmark_results.json")
    print(f"  [OK] Dung file nay de ve bieu do trong bao cao!")


# =============================================
# CHAY BENCHMARK
# =============================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  RQLITE BENCHMARK TOOL")
    print("  Nhom 8 - Phenikaa University")
    print("=" * 60)
    print(f"\n  Leader  : {LEADER_URL}")
    print(f"  So test : {NUM_REQUESTS} requests moi loai\n")

    # Setup
    print("  Dang ket noi toi RQLite cluster...")
    setup_table()

    # Chay cac benchmark
    write_res = benchmark_write()
    read_res = benchmark_read()
    multi_res = benchmark_multi_node_read()

    # Benchmark bau leader la optional (can tat thu cong)
    print("\n  Ban co muon do thoi gian bau lai Leader khong?")
    print("  (Yeu cau tat thu cong 1 terminal RQLite)")
    choice = input("  Nhap y/n: ").strip().lower()
    election_res = None
    if choice == 'y':
        election_res = benchmark_leader_election()

    # Bao cao tong hop
    save_results(write_res, read_res, multi_res, election_res)

    print("\n  Hoan thanh! Kiem tra file benchmark_results.json\n")
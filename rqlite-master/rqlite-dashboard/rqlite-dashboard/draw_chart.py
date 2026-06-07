import json
import os

# Ve bieu do tu ket qua benchmark
# Chay sau khi da co file benchmark_results.json

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("[!] Chua cai matplotlib. Chay: pip install matplotlib")
    print("[!] Script van in ket qua dang text.\n")


def load_results():
    if not os.path.exists("benchmark_results.json"):
        print("[LOI] Khong tim thay benchmark_results.json")
        print("      Hay chay benchmark.py truoc!")
        return None
    with open("benchmark_results.json", "r", encoding="utf-8") as f:
        return json.load(f)


def print_text_report(data):
    """In ket qua dang bang text (khong can matplotlib)"""
    print("\n" + "=" * 55)
    print("  KET QUA BENCHMARK - RQLITE")
    print("=" * 55)

    w = data["write"]
    r = data["read"]

    print(f"\n  WRITE Performance:")
    print(f"    Trung binh : {w['avg']} ms")
    print(f"    Nhanh nhat : {w['min']} ms")
    print(f"    Cham nhat  : {w['max']} ms")
    print(f"    Throughput : {w['throughput']} writes/s")

    print(f"\n  READ Performance:")
    print(f"    Trung binh : {r['avg']} ms")
    print(f"    Nhanh nhat : {r['min']} ms")
    print(f"    Cham nhat  : {r['max']} ms")
    print(f"    Throughput : {r['throughput']} reads/s")

    print(f"\n  So sanh READ giua cac node:")
    for node, info in data["multi_node"].items():
        if info.get("avg_ms"):
            bar = "█" * int(info["avg_ms"])
            print(f"    {node:6}: {info['avg_ms']:6.1f} ms  {bar}")
        else:
            print(f"    {node:6}: OFFLINE")

    if data.get("election") and data["election"].get("election_time_ms"):
        print(f"\n  Thoi gian bau lai Leader: {data['election']['election_time_ms']} ms")

    print("\n" + "=" * 55)


def draw_charts(data):
    """Ve 3 bieu do va luu thanh PNG"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#0f1117')

    colors = {
        'write': '#63b3ed',
        'read':  '#68d391',
        'bar':   ['#63b3ed', '#68d391', '#f6ad55'],
        'bg':    '#1a1d2e',
        'text':  '#e2e8f0',
        'grid':  '#2d3748',
    }

    for ax in axes:
        ax.set_facecolor(colors['bg'])
        ax.tick_params(colors=colors['text'], labelsize=9)
        ax.spines['bottom'].set_color(colors['grid'])
        ax.spines['left'].set_color(colors['grid'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.grid(True, color=colors['grid'], linewidth=0.5, alpha=0.7)
        ax.set_axisbelow(True)

    # --- Bieu do 1: So sanh WRITE vs READ ---
    ax1 = axes[0]
    categories = ['WRITE\n(INSERT)', 'READ\n(SELECT)']
    avgs = [data['write']['avg'], data['read']['avg']]
    mins = [data['write']['min'], data['read']['min']]
    maxs = [data['write']['max'], data['read']['max']]
    x = np.arange(len(categories))
    width = 0.25

    ax1.bar(x - width, mins, width, label='Min', color=colors['write'], alpha=0.6)
    ax1.bar(x,         avgs, width, label='Avg', color=colors['write'])
    ax1.bar(x + width, maxs, width, label='Max', color=colors['write'], alpha=0.4)

    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, color=colors['text'])
    ax1.set_ylabel('Thoi gian (ms)', color=colors['text'])
    ax1.set_title('WRITE vs READ Latency (ms)', color=colors['text'], pad=12)
    ax1.legend(facecolor=colors['bg'], labelcolor=colors['text'], fontsize=8)

    for i, v in enumerate(avgs):
        ax1.text(i, v + 0.5, f'{v:.1f}ms', ha='center', color=colors['text'], fontsize=9, fontweight='bold')

    # --- Bieu do 2: Throughput so sanh ---
    ax2 = axes[1]
    labels = ['WRITE\nThroughput', 'READ\nThroughput']
    values = [data['write']['throughput'], data['read']['throughput']]
    bars = ax2.bar(labels, values, color=[colors['write'], colors['read']], width=0.4)

    ax2.set_ylabel('Queries / giay', color=colors['text'])
    ax2.set_title('Throughput So Sanh', color=colors['text'], pad=12)
    ax2.tick_params(axis='x', colors=colors['text'])

    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{val:.0f}/s', ha='center', color=colors['text'], fontsize=10, fontweight='bold')

    # --- Bieu do 3: READ latency tung node ---
    ax3 = axes[2]
    node_names = []
    node_avgs = []
    node_colors = []
    c_list = [colors['write'], colors['read'], colors['bar'][2]]

    for i, (node, info) in enumerate(data['multi_node'].items()):
        node_names.append(node.upper())
        node_avgs.append(info.get('avg_ms') or 0)
        node_colors.append(c_list[i % len(c_list)])

    bars3 = ax3.bar(node_names, node_avgs, color=node_colors, width=0.4)
    ax3.set_ylabel('Trung binh (ms)', color=colors['text'])
    ax3.set_title('READ Latency Tung Node', color=colors['text'], pad=12)
    ax3.tick_params(axis='x', colors=colors['text'])

    for bar, val in zip(bars3, node_avgs):
        if val > 0:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f'{val:.1f}ms', ha='center', color=colors['text'], fontsize=9, fontweight='bold')

    # Title chung
    fig.suptitle(
        f'RQLite Benchmark Results  —  {data.get("timestamp", "")}',
        color=colors['text'], fontsize=13, fontweight='bold', y=1.01
    )

    plt.tight_layout()
    plt.savefig('benchmark_chart.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print("\n  [OK] Da luu bieu do: benchmark_chart.png")
    print("  [OK] Dung anh nay gan vao bao cao Word!\n")
    plt.show()


if __name__ == "__main__":
    print("\n  === VE BIEU DO BENCHMARK RQLITE ===\n")
    data = load_results()
    if data is None:
        exit(1)

    print_text_report(data)

    if HAS_MATPLOTLIB:
        print("\n  Dang ve bieu do...")
        draw_charts(data)
    else:
        print("\n  [!] Cai matplotlib de ve bieu do dep hon:")
        print("      pip install matplotlib\n")
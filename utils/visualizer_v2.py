"""
Decision Path Visualizer - Simpel, Besar & Mudah Dibaca
Versi 4.0 - Clean vertical tree layout
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# Mapping nama fitur ke label Indonesia
FEAT_ID = {
    'Age': 'Usia',
    'Salt_Intake': 'Asupan Garam',
    'Stress_Score': 'Tingkat Stres',
    'BP_History': 'Riwayat Tekanan Darah',
    'Sleep_Duration': 'Durasi Tidur',
    'BMI': 'BMI',
    'Family_History': 'Riwayat Keluarga',
    'Exercise_Level': 'Aktivitas Fisik',
    'Smoking_Status': 'Status Merokok',
}


def plot_decision_path_only(path_info, reverse_maps=None):
    """
    Visualisasi Decision Path - Simpel & Besar
    - Layout vertikal (root di atas, leaf di bawah)
    - Node besar dengan font besar
    - Label YA/TIDAK yang jelas di koneksi
    - Leaf node besar dengan hasil dan confidence
    """
    steps = path_info['steps']
    pred_class = path_info['predicted_class']
    conf = path_info['confidence']

    decision_steps = [s for s in steps if not s.get('is_leaf')]
    n = len(decision_steps)

    # ============================================================
    # UKURAN NODE - BESAR & MUDAH DIBACA
    # ============================================================
    NODE_W = 6.0
    NODE_H = 3.2

    # ============================================================
    # LAYOUT PARAMETERS - Spacing & figure sizing
    # ============================================================
    # Decision levels: 0 (root) .. n-1, Leaf at level n
    N_LEVELS = n + 1        # total levels (decision + leaf)
    Y_STEP = 5.5            # vertical gap between levels
    y_top = (N_LEVELS - 1) * Y_STEP
    y_bottom = -1.0

    # Figure height proportional to number of nodes
    fig_h = max(12, N_LEVELS * 3.2 + 2)
    fig_w = 16
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor='white')
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('#FAFAFA')

    def level_y(lvl):
        """Y coordinate for a given level (0=top root, n=leaf)."""
        return y_top - lvl * Y_STEP

    # ============================================================
    # WARNA TEMA
    # ============================================================
    YA_BG   = '#E8F5E9'; YA_ED   = '#2E7D32'; YA_TXT  = '#1B5E20'
    TDK_BG  = '#FFEBEE'; TDK_ED  = '#C62828'; TDK_TXT = '#B71C1C'

    LEAF_NORMAL_BG = '#E3F2FD'; LEAF_NORMAL_ED = '#1565C0'; LEAF_NORMAL_TXT = '#0D47A1'
    LEAF_HYPER_BG  = '#FFEBEE'; LEAF_HYPER_ED   = '#C62828'; LEAF_HYPER_TXT  = '#B71C1C'

    # ============================================================
    # GAMBAR ARROW + LABEL YA/TIDAK
    # ============================================================
    for lvl in range(n):
        step = decision_steps[lvl]
        direction = step['direction']

        y1 = level_y(lvl)
        y2 = level_y(lvl + 1)
        x1 = 0.5

        if direction == 'left':
            arrow_color = YA_ED
            edge_label = 'YA'
            lx_off = 1.2
        else:
            arrow_color = TDK_ED
            edge_label = 'TIDAK'
            lx_off = -1.2

        # Vertical connector line
        ax.plot([x1, x1], [y1 - NODE_H / 2, y2 + NODE_H / 2 + 0.4],
            color=arrow_color, linewidth=3, zorder=2)

        # Arrow head pointing to next node
        ax.annotate('',
            xy=(x1, y2 + NODE_H / 2 + 0.1),
            xytext=(x1, y1 - NODE_H / 2 - 0.4),
            arrowprops=dict(
                arrowstyle='->',
                color=arrow_color,
                linewidth=4,
            ),
            zorder=3
        )

        # Label "YA" or "TIDAK" beside connector
        ax.text(x1 + lx_off, (y1 + y2) / 2, edge_label,
            fontsize=15, fontweight='bold',
            color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor=arrow_color,
                      edgecolor='none', linewidth=0),
            zorder=6)

    # ============================================================
    # GAMBAR DECISION NODES
    # ============================================================
    for lvl in range(n):
        step = decision_steps[lvl]
        feat = step['feature']
        val  = step['input_value']
        direction = step['direction']
        comparison = step.get('comparison', '')

        x, y = 0.5, level_y(lvl)
        feat_disp = FEAT_ID.get(feat, feat) if feat else feat

        # Format nilai input
        if isinstance(val, float) and val == int(val):
            val_str = str(int(val))
        elif isinstance(val, (int, float)):
            val_str = f"{val:.2f}".rstrip('0').rstrip('.')
        else:
            val_str = str(val)

        if direction == 'left':
            bg, ed = YA_BG, YA_ED
        else:
            bg, ed = TDK_BG, TDK_ED

        # Node box
        rect = FancyBboxPatch(
            (x - NODE_W / 2, y - NODE_H / 2), NODE_W, NODE_H,
            boxstyle="round,pad=0.1,rounding_size=0.35",
            facecolor=bg, edgecolor=ed, linewidth=4, zorder=4
        )
        ax.add_patch(rect)

        # Header: nama fitur
        ax.text(x, y + 0.85, feat_disp,
            fontsize=17, fontweight='bold',
            color=ed, ha='center', va='center', zorder=5)

        # Separator line
        ax.plot([x - NODE_W / 2 + 0.5, x + NODE_W / 2 - 0.5],
               [y + 0.45, y + 0.45],
               color=ed, linewidth=1.5, alpha=0.4, zorder=5)

        # Input value
        ax.text(x, y + 0.05, f'Nilai: {val_str}',
            fontsize=15, color='#333333',
            ha='center', va='center', zorder=5)

        # Comparison / threshold
        ax.text(x, y - 0.55, comparison,
            fontsize=11, color='#888888', style='italic',
            ha='center', va='center', zorder=5)

        # Direction badge inside node
        direction_label = 'YA' if direction == 'left' else 'TIDAK'
        ax.text(x, y - 1.15, direction_label,
            fontsize=14, fontweight='bold', color='white',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.35',
                      facecolor=ed, edgecolor='none'),
            zorder=6)

    # ============================================================
    # LEAF NODE - HASIL AKHIR
    # ============================================================
    lx = 0.5
    ly = level_y(n)

    if pred_class == 0:
        lbg, led, lt = LEAF_NORMAL_BG, LEAF_NORMAL_ED, LEAF_NORMAL_TXT
        result = 'TIDAK HIPERTENSI'
        icon = 'OK'
    else:
        lbg, led, lt = LEAF_HYPER_BG, LEAF_HYPER_ED, LEAF_HYPER_TXT
        result = 'HIPERTENSI'
        icon = '!'

    # Arrow from last decision node to leaf
    if n > 0:
        last_dir = decision_steps[-1]['direction']
        last_ed = YA_ED if last_dir == 'left' else TDK_ED
        y_last = level_y(n - 1)
        ax.plot([lx, lx], [y_last - NODE_H / 2, ly + NODE_H * 1.3 / 2 + 0.3],
            color=last_ed, linewidth=3, zorder=2)
        ax.annotate('',
            xy=(lx, ly + NODE_H * 1.3 / 2 + 0.1),
            xytext=(lx, y_last - NODE_H / 2),
            arrowprops=dict(arrowstyle='->', color=last_ed, linewidth=4),
            zorder=3
        )

    # Leaf box - more prominent
    lw, lh = NODE_W * 1.15, NODE_H * 1.4
    rect = FancyBboxPatch(
        (lx - lw / 2, ly - lh / 2), lw, lh,
        boxstyle="round,pad=0.1,rounding_size=0.35",
        facecolor=lbg, edgecolor=led, linewidth=5, zorder=4
    )
    ax.add_patch(rect)

    # Icon
    ax.text(lx, ly + 1.1, icon,
        fontsize=30, fontweight='bold',
        color=led, ha='center', va='center', zorder=5)

    # Result
    ax.text(lx, ly + 0.4, result,
        fontsize=19, fontweight='bold',
        color=lt, ha='center', va='center', zorder=5)

    # Confidence label
    ax.text(lx, ly - 0.35, 'Confidence',
        fontsize=12, color='#555555',
        ha='center', va='center', zorder=5)

    # Confidence value
    ax.text(lx, ly - 1.0, f'{conf * 100:.1f}%',
        fontsize=24, fontweight='bold',
        color=led, ha='center', va='center', zorder=5)

    # ============================================================
    # AXIS SETUP
    # ============================================================
    margin_x = NODE_W * 0.9 + 3
    ax.set_xlim(-margin_x, margin_x - NODE_W * 0.4)
    ax.set_ylim(y_bottom - 2, y_top + 2)
    ax.axis('off')

    plt.tight_layout(pad=2)
    return fig

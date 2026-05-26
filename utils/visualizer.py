"""
Utility: Visualizer
Berisi fungsi-fungsi untuk visualisasi Decision Tree dan Animated Walk.
Menggunakan Plotly untuk interaktif dan Matplotlib untuk static plots.
"""

import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import io


def create_animated_walk_figure(path_info, reverse_maps=None):
    """
    Buat animated walk visualization menggunakan Plotly.

    Args:
        path_info: dict dari tree_walker.get_decision_path()
        reverse_maps: dict mapping angka ke label untuk decode

    Returns:
        plotly Figure object
    """
    steps = path_info['steps']
    predicted_class = path_info['predicted_class']
    confidence = path_info['confidence']
    class_probs = path_info['class_probs']

    # Decode prediction label
    if reverse_maps and 'Has_Hypertension' in reverse_maps:
        pred_label = reverse_maps['Has_Hypertension'].get(predicted_class, str(predicted_class))
    else:
        pred_label = "Hipertensi" if predicted_class == 1 else "Tidak Hipertensi"

    # Buat frames untuk animasi
    frames = []

    # Generate layout nodes (horizontal tree layout)
    # Node positions: root di kiri, leaves di kanan
    n_steps = len(steps)

    for frame_idx in range(n_steps):
        current_step = steps[frame_idx]

        # Buat node traces untuk frame ini
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []

        # Node positions shifted by 0.1 to leave room for result box on right
        for i, step in enumerate(steps[:frame_idx + 1]):
            x_pos = 0.1 + (step['step'] - 1) / max(n_steps, 1) * 0.8
            y_pos = (i + 1) / (n_steps + 1)  # normalize vertically

            # Highlight current node
            color = '#FF6B6B' if i == frame_idx else '#4ECDC4'
            size = 40 if i == frame_idx else 30

            node_x.append(x_pos)
            node_y.append(y_pos)

            # Text untuk node - use ASCII <= for safety
            if i == frame_idx:
                comp_ascii = step['comparison'].replace('≤', '<=').replace('>', '>')
                text = (f"<b>STEP {step['step']}</b><br>"
                        f"<b>{step['feature']}</b><br>"
                        f"Input: {step['input_value']}<br>"
                        f"Threshold: {step['threshold']}<br>"
                        f"{comp_ascii}")
            else:
                text = (f"{step['feature']}<br>"
                        f"{step['input_value']}")

            node_text.append(text)
            node_colors.append(color)
            node_sizes.append(size)

        # Edges (koneksi antar nodes)
        edge_x = []
        edge_y = []
        for i in range(len(node_x) - 1):
            edge_x.extend([node_x[i], node_x[i+1], None])
            edge_y.extend([node_y[i], node_y[i+1], None])

        # Build frame
        frame_data = [
            go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(color='#95A5A6', width=2),
                hoverinfo='none',
                showlegend=False
            ),
            go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(color='white', width=2)
                ),
                text=node_text,
                textposition="middle center",
                textfont=dict(size=10, color='black'),
                hoverinfo='text',
                showlegend=False
            )
        ]

        # Highlight decision untuk node terakhir
        if frame_idx == n_steps - 1:
            # Decision box
            decision_text = (
                f"<b>KEPUTUSAN: {pred_label}</b><br>"
                f"Confidence: {confidence * 100:.1f}%<br><br>"
                f"Tidak Hipertensi: {class_probs[0]*100:.1f}%<br>"
                f"Hipertensi: {class_probs[1]*100:.1f}%"
            )
            frame_data.append(go.Scatter(
                x=[1.05], y=[0.5],
                mode='text',
                text=[decision_text],
                textfont=dict(size=14, color='#2C3E50'),
                hoverinfo='none',
                showlegend=False
            ))

        frames.append(go.Frame(data=frame_data, name=str(frame_idx)))

    # Initial data (frame 0)
    initial_node_x = [0]
    initial_node_y = [0.5]
    initial_text = [
        f"<b>STEP 1: {steps[0]['feature']}</b><br>"
        f"Input: {steps[0]['input_value']}<br>"
        f"Threshold: {steps[0]['threshold']}<br>"
        f"{steps[0]['comparison']}"
    ]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[0, 0.2], y=[0.5, 0.5],
                mode='lines',
                line=dict(color='#95A5A6', width=2),
                hoverinfo='none',
                showlegend=False
            ),
            go.Scatter(
                x=initial_node_x, y=initial_node_y,
                mode='markers+text',
                marker=dict(size=40, color='#FF6B6B', line=dict(color='white', width=2)),
                text=initial_text,
                textposition="middle center",
                textfont=dict(size=10, color='black'),
                hoverinfo='text',
                showlegend=False
            )
        ],
        frames=frames
    )

    # Tombol animasi
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                y=1.15,
                x=0.1,
                xanchor='left',
                buttons=[
                    dict(
                        label='▶ Play',
                        method='animate',
                        args=[None, {
                            'frame': {'duration': 1500, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': 500}
                        }]
                    ),
                    dict(
                        label='⏸ Pause',
                        method='animate',
                        args=[[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate'
                        }]
                    )
                ]
            )
        ],
        sliders=[{
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 14},
                'prefix': 'Step: ',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 500},
            'pad': {'b': 10, 't': 30},
            'len': 0.9,
            'x': 0.05,
            'y': 0,
            'steps': [
                {'args': [[str(i)], {'frame': {'duration': 0, 'redraw': True},
                                      'mode': 'immediate'}],
                 'label': str(i + 1),
                 'method': 'animate'}
                for i in range(n_steps)
            ]
        }]
    )

    fig.update_layout(
        title={
            'text': '<b>Animated Decision Path</b>',
            'font': {'size': 18}
        },
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        plot_bgcolor='white',
        height=400,
        margin=dict(l=50, r=150, t=60, b=50)
    )

    return fig


def create_feature_importance_chart(feature_names, importances, top_n=None):
    """
    Buat horizontal bar chart untuk feature importance.

    Args:
        feature_names: list nama fitur
        importances: list importance scores
        top_n: jumlah fitur teratas yang ditampilkan

    Returns:
        plotly Figure
    """
    # Sort by importance
    pairs = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)

    if top_n:
        pairs = pairs[:top_n]

    names = [p[0] for p in pairs]
    values = [p[1] for p in pairs]

    # Colors: highest is primary color, others fade
    max_val = max(values) if values else 1
    colors = [f'rgba(78, 205, 196, {0.4 + 0.6 * (v / max_val)})' for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation='h',
        marker_color=colors,
        text=[f'{v:.2%}' for v in values],
        textposition='outside'
    ))

    fig.update_layout(
        title={'text': '<b>Feature Importance</b>', 'font': {'size': 16}},
        xaxis_title='Importance Score',
        yaxis_title='Feature',
        height=300,
        margin=dict(l=120, r=30, t=40, b=40),
        xaxis=dict(range=[0, max(values) * 1.2]),
        plot_bgcolor='white'
    )

    return fig


def create_confusion_matrix_figure(cm, labels):
    """
    Buat heatmap confusion matrix.

    Args:
        cm: 2x2 confusion matrix
        labels: ['Tidak Hipertensi', 'Hipertensi']

    Returns:
        plotly Figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=labels,
        y=labels,
        text=[[str(v) for v in row] for row in cm],
        texttemplate='<b>%{text}</b>',
        textfont={"size": 20},
        colorscale='Blues',
        showscale=False
    ))

    fig.update_layout(
        title={'text': '<b>Confusion Matrix (Test Data)</b>', 'font': {'size': 16}},
        xaxis_title='Predicted',
        yaxis_title='Actual',
        height=350,
        width=400,
        plot_bgcolor='white'
    )

    return fig


def create_metrics_comparison_chart(baseline_metrics, tuned_metrics):
    """
    Buat grouped bar chart perbandingan baseline vs tuned model.

    Args:
        baseline_metrics: dict {'accuracy': float, ...}
        tuned_metrics: dict {'accuracy': float, ...}

    Returns:
        plotly Figure
    """
    metrics = ['accuracy', 'precision', 'recall', 'f1_score']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']

    baseline_vals = [baseline_metrics.get(m, 0) for m in metrics]
    tuned_vals = [tuned_metrics.get(m, 0) for m in metrics]

    fig = go.Figure(data=[
        go.Bar(
            name='Baseline',
            x=metric_labels,
            y=baseline_vals,
            marker_color='#FF6B6B'
        ),
        go.Bar(
            name='Tuned (GridSearchCV)',
            x=metric_labels,
            y=tuned_vals,
            marker_color='#4ECDC4'
        )
    ])

    fig.update_layout(
        title={'text': '<b>Model Comparison: Baseline vs Tuned</b>', 'font': {'size': 16}},
        barmode='group',
        yaxis_title='Score',
        yaxis=dict(range=[0, 1.1]),
        height=350,
        plot_bgcolor='white',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    return fig

def create_animated_decision_path(path_info, reverse_maps=None):
    """
    Buat visualisasi decision path dengan animasi menarik.
    Hanya menampilkan node-node yang dilalui user input.

    Args:
        path_info: dict dari tree_walker.get_decision_path()
        reverse_maps: dict mapping untuk decode label

    Returns:
        matplotlib Figure untuk static display
    """
    steps = path_info['steps']
    predicted_class = path_info['predicted_class']
    confidence = path_info['confidence']
    class_probs = path_info['class_probs']
    n_steps = len(steps)

    # Decode prediction
    if reverse_maps and 'Has_Hypertension' in reverse_maps:
        pred_label = reverse_maps['Has_Hypertension'].get(predicted_class, str(predicted_class))
    else:
        pred_label = "Hipertensi" if predicted_class == 1 else "Tidak Hipertensi"

    # Setup figure - vertical tree
    fig, ax = plt.subplots(figsize=(10, 4 + n_steps))
    ax.set_xlim(-0.5, 2.5)
    ax.set_ylim(-0.5, n_steps + 1)
    ax.axis('off')

    # Colors
    colors = {
        'node': '#3498db' if predicted_class == 0 else '#e74c3c',
        'leaf': '#27ae60' if predicted_class == 0 else '#c0392b',
        'edge': '#7f8c8d'
    }

    # Node positions (vertical)
    positions = [(1.0, n_steps - i) for i in range(n_steps + 1)]

    # Draw edges (arrows between nodes)
    for i in range(len(positions) - 1):
        y_start, y_end = positions[i][1], positions[i+1][1]
        arrow = FancyArrowPatch(
            positions[i], positions[i+1],
            arrowstyle='->', mutation_scale=25, linewidth=2.5,
            color=colors['edge'], alpha=0.5, zorder=1
        )
        ax.add_patch(arrow)

    # Draw nodes
    for i, (x, y) in enumerate(positions):
        size = 0.2 if i < n_steps else 0.25
        color = colors['leaf'] if i == n_steps else colors['node']

        # Node box
        bbox = FancyBboxPatch(
            (x - size/2, y - size/2), size, size,
            boxstyle="round,pad=0.03", linewidth=2.5,
            edgecolor='white', facecolor=color, zorder=2, alpha=0.9
        )
        ax.add_patch(bbox)

        # Step number
        ax.text(
            x, y + size/2 + 0.1, f"Step {i+1}" if i < n_steps else "HASIL",
            ha='center', va='bottom', fontsize=12, fontweight='bold', color=color
        )

        # Node content
        if i < n_steps:
            step = steps[i]
            ax.text(
                x, y, f"{step['feature']}\n{step['comparison']}",
                ha='center', va='center', fontsize=10, color='white', weight='bold'
            )
            # Input value
            ax.text(
                x + 0.5, y, f"Input: {step['input_value']}",
                ha='left', va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            )
        else:
            # Final result
            conf_pct = confidence * 100
            ax.text(
                x, y, f"{pred_label}\n{conf_pct:.1f}%",
                ha='center', va='center', fontsize=11, color='white', weight='bold'
            )
            # Probability
            prob_text = f"Tidak: {class_probs[0]*100:.1f}%\nYa: {class_probs[1]*100:.1f}%"
            ax.text(
                x + 0.6, y, prob_text, ha='left', va='center', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
            )

    # Title
    ax.text(
        1, n_steps + 0.8, "Decision Path Traversal",
        ha='center', va='top', fontsize=15, weight='bold'
    )

    plt.tight_layout()
    return fig

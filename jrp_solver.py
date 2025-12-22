import math
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Item:
    id: str
    a: float
    D: float
    v: float
    @property
    def a_over_Dv(self) -> float:
        return self.a / (self.D * self.v) if self.D * self.v > 0 else float('inf')

@dataclass
class JRPInstance:
    instance_name: str
    A: float
    r: float
    items: List[Item]

def find_optimal_policy(instance: JRPInstance):
    # Sort by a/Dv
    sorted_items = sorted(instance.items, key=lambda x: x.a_over_Dv)
    m_values = [1] * len(sorted_items)
    D1_v1 = sorted_items[0].D * sorted_items[0].v
    
    # Calculate m_i
    for i in range(1, len(sorted_items)):
        ratio = (sorted_items[i].a_over_Dv) * (D1_v1 / (instance.A + sorted_items[0].a))
        m_values[i] = max(1, round(math.sqrt(ratio)))
    
    # Calculate T*
    num = 2 * (instance.A + sum(item.a / m_values[i] for i, item in enumerate(sorted_items)))
    den = instance.r * sum(m_values[i] * item.D * item.v for i, item in enumerate(sorted_items))
    T_star = math.sqrt(num / den)
    
    item_results = []
    for i, item in enumerate(sorted_items):
        ti = m_values[i] * T_star
        h_cost = (item.D * ti * item.v * instance.r) / 2
        s_cost = item.a / ti
        item_results.append({
            "ID": item.id,
            "Multiplier (m)": m_values[i],
            "Individual Cycle (Ti)": round(ti, 5),
            "Setup Cost ($)": round(s_cost, 2),
            "Holding Cost ($)": round(h_cost, 2),
            "Total Item Cost ($)": round(s_cost + h_cost, 2)
        })

    total_system_cost = (instance.A / T_star) + sum(res["Total Item Cost ($)"] for res in item_results)
    return T_star, total_system_cost, item_results

def generate_visuals(item_results, palette):
    # Breakdown chart using your palette
    ids = [r["ID"] for r in item_results]
    setups = [r["Setup Cost ($)"] for r in item_results]
    holdings = [r["Holding Cost ($)"] for r in item_results]

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#f1faee')
    ax.set_facecolor('#f1faee')
    
    ax.bar(ids, setups, label='Setup Cost', color=palette[0]) # 1d3557
    ax.bar(ids, holdings, bottom=setups, label='Holding Cost', color=palette[1]) # 457b9d
    
    ax.set_ylabel('Cost ($)', fontweight='bold')
    ax.set_title('Cost Breakdown per Item', fontweight='bold', fontsize=14)
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig
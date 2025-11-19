# components/generic_taskgraphwidget.py
"""
通用任务图可视化组件

接受标准化的任务图数据格式，使用networkx绘制有向图。
只展示任务之间的逻辑依赖关系，使用简单的圆形节点和箭头。
"""
import networkx as nx
import hashlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from typing import Dict, Any, Optional
from .matplotlib_font_config import setup_chinese_font


class GenericTaskGraphWidget(FigureCanvas):
    """
    通用任务图组件，接受标准化绘图数据
    
    使用 networkx 进行图的构建和可视化，只展示任务关系。
    布局位置会被缓存，只有在图结构改变时才会重新计算。
    
    数据格式：
    {
        "nodes": [
            {
                "id": str | int,              # 节点ID（唯一标识）
                "label": str                   # 节点标签（显示文本）
            },
            ...
        ],
        "edges": [
            {
                "source": str | int,           # 源节点ID
                "target": str | int,          # 目标节点ID
                "type": str                    # 边类型："sequence"（先后顺序，有箭头）或 "parallel"（同时关系，无箭头虚线）
            },
            ...
        ],
        "layout": {                           # 布局配置（可选）
            "algorithm": str                  # 布局算法（"spring"/"circular"/"hierarchical"，默认"spring"）
        }
    }
    """
    
    def __init__(self):
        # 配置matplotlib使用中文字体
        setup_chinese_font()
        
        self.fig = Figure(facecolor="none")
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("none")
        self.ax.axis('off')
        
        # 缓存布局位置：{graph_hash: positions}
        self._layout_cache = {}
        # 当前图的hash值
        self._current_graph_hash = None
    
    def update_plot(self, graph_data: Dict[str, Any]):
        """
        更新任务图
        
        参数：
            graph_data: 标准化的任务图数据字典
        """
        self.ax.clear()
        self.ax.axis('off')
        
        # 获取数据
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        layout_config = graph_data.get("layout", {})
        
        if not nodes:
            self.draw()
            return
        
        # 构建 networkx 有向图
        G = nx.DiGraph()
        
        # 添加节点
        node_dict = {}
        for node in nodes:
            node_id = node["id"]
            G.add_node(node_id)
            node_dict[node_id] = node.get("label", str(node_id))
        
        # 添加边并存储边类型
        edge_types = {}  # {(source, target): type}
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            edge_type = edge.get("type", "sequence")  # 默认为先后顺序
            if source in node_dict and target in node_dict:
                G.add_edge(source, target)
                edge_types[(source, target)] = edge_type
        
        # 计算图的hash值（基于节点和边的结构）
        graph_hash = self._compute_graph_hash(G)
        
        # 检查是否需要重新计算布局
        algorithm = layout_config.get("algorithm", "spring")
        cache_key = f"{algorithm}_{graph_hash}"
        
        if cache_key in self._layout_cache:
            # 使用缓存的布局
            pos = self._layout_cache[cache_key]
        else:
            # 计算新布局（固定随机种子以确保稳定性）
            import numpy as np
            np.random.seed(42)  # 固定随机种子
            
            if algorithm == "circular":
                pos = nx.circular_layout(G)
            elif algorithm == "hierarchical":
                # 使用 spring 布局作为层次布局的近似
                pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
            else:  # spring (default)
                pos = nx.spring_layout(G, k=1.0, iterations=50, seed=42)
            
            # 缓存布局
            self._layout_cache[cache_key] = pos
        
        self._current_graph_hash = graph_hash
        
        # 绘制节点（统一小圆形，无颜色差异）
        nx.draw_networkx_nodes(
            G, pos,
            node_color='lightblue',
            node_size=300,
            ax=self.ax
        )
        
        # 按边类型分组绘制
        sequence_edges = [(u, v) for u, v in G.edges() 
                          if edge_types.get((u, v), "sequence") == "sequence"]
        parallel_edges = [(u, v) for u, v in G.edges() 
                         if edge_types.get((u, v), "sequence") == "parallel"]
        
        # 绘制先后顺序边（有箭头）
        if sequence_edges:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=sequence_edges,
                edge_color='gray',
                width=1.0,
                arrows=True,
                arrowsize=15,
                arrowstyle='->',
                ax=self.ax
            )
        
        # 绘制同时关系边（无箭头虚线）
        if parallel_edges:
            nx.draw_networkx_edges(
                G, pos,
                edgelist=parallel_edges,
                edge_color='gray',
                width=1.0,
                arrows=False,  # 无箭头
                style='dashed',  # 虚线样式
                ax=self.ax
            )
        
        # 绘制节点标签
        labels = {node_id: node_dict[node_id] for node_id in G.nodes()}
        nx.draw_networkx_labels(
            G, pos,
            labels=labels,
            font_size=9,
            ax=self.ax
        )
        
        self.ax.set_aspect('equal')
        self.fig.tight_layout()
        self.draw()
    
    def _compute_graph_hash(self, G: nx.DiGraph) -> str:
        """
        计算图的hash值，用于判断图结构是否改变
        
        基于节点和边的结构生成hash，忽略节点标签等不影响布局的属性
        """
        # 获取排序后的节点和边列表
        nodes = sorted(G.nodes())
        edges = sorted(G.edges())
        
        # 生成hash字符串
        graph_str = f"nodes:{nodes}_edges:{edges}"
        return hashlib.md5(graph_str.encode()).hexdigest()

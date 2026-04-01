import networkx as nx
from plotly.graph_objs import Scatter, Figure

def output_graph(g: nx.Graph, graph_type: str) -> Figure:
    """Outputs a visualization of a graph. Adapted from CSC111 A3
    """
    user_colour = 'rgb(252, 128, 159)'
    anime_colour = 'rgb(185, 10, 92)'
    line_colour = 'rgb(255, 192, 222)'

    pos = getattr(nx, 'spring_layout')(g)

    x_values = [pos[k][0] for k in g.nodes]
    y_values = [pos[k][1] for k in g.nodes]
    labels = list(g.nodes)

    kinds = [g.nodes[k]['kind'] for k in g.nodes]
    shapes = ['circle' if kind == graph_type else 'star' for kind in kinds]
    colours = [user_colour if kind == graph_type else anime_colour for kind in kinds]
    sizes = [5 if kind == graph_type else 10 for kind in kinds]
    font_size = [8 if kind == graph_type else 12 for kind in kinds]

    x_edges = []
    y_edges = []
    for edge in g.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=line_colour, width=1),
                     hoverinfo='none',
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers+text',
                     textposition='bottom center',
                     name='nodes',
                     marker=dict(symbol=shapes,
                                 size=sizes,
                                 color=colours,
                                 line=dict(color='rgb(50, 50, 50)', width=0.5)
                                 ),
                     text=labels,
                     textfont_size= font_size,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = [trace3, trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    return fig

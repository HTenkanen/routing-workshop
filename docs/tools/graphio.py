import time
import pandas as pd

def build_graph_from_Digiroad(gdf, direction='AJOSUUNTA', both_ways=2, against=3, along=4):
    """Creates a NetworkX MultiDiGraph from Digiroad 2.0 road network GeoDataFrame.

    Parameters
    ----------

    gdf : GeoDataFrame
        GeoDataFrame containing Digiroad 2.0 road network data.

    direction : str
        Name for column that contains information about the allowed driving directions

    both_ways : int
        Value specifying that the road is drivable to both directions.

    against : int
        Value specifying that the road is drivable against the digitizing direction.

    along : int
        Value specifying that the road is drivable along the digitizing direction.

    """
    import networkx as nx

    tot_t = time.time()
    node_dict = {}
    edge_list = []
    node_list = []

    i = 1

    # Get unique set of nodes
    for edge in gdf.itertuples():
        coords = edge.geometry.coords
        # Get from and to nodeids (drop possible Z information)
        fr, to = coords[0][:2], coords[-1][:2]
        node_dict[fr] = i
        i += 1
        node_dict[to] = i
        i += 1

    # Make sequential numbers for all nodes
    i = 1
    for nodecoords, nodeid in node_dict.items():
        node_dict[nodecoords] = i
        i += 1

    # Generate edge dictionary
    for edge in gdf.itertuples():
        coords = edge.geometry.coords

        # Get from and to nodeids (drop Z information)
        fr, to = coords[0][:2], coords[-1][:2]

        # Get nodeid for the edge
        from_node_id = node_dict[fr]
        to_node_id = node_dict[to]

        # Edge attributes
        edge_attr = dict(edge._asdict())

        # Remove unnecessary attributes
        if 'Index' in edge_attr.keys():
            del edge_attr['Index']
        if 'index' in edge_attr.keys():
            del edge_attr['index']

        # Generate edge indices
        e_idx = edge.index

        # Create edge in Networkx format
        if edge_attr[direction] == both_ways:

            # Keep track on the direction
            along_idx = "{edge_index}a".format(edge_index=e_idx)
            against_idx = "{edge_index}b".format(edge_index=e_idx)

            # If road is bi-directional add it in both ways
            edge_list.append([from_node_id, to_node_id, along_idx, edge_attr])
            edge_list.append([to_node_id, from_node_id, against_idx, edge_attr])

        elif edge_attr[direction] == along:

            # Keep track on the direction
            along_idx = "{edge_index}a".format(edge_index=e_idx)

            # Add the edge along digitization direction
            edge_list.append([from_node_id, to_node_id, along_idx, edge_attr])

        elif edge_attr[direction] == against:
            # Keep track on the direction
            against_idx = "{edge_index}b".format(edge_index=e_idx)

            # Add the edge along digitization direction
            edge_list.append([to_node_id, from_node_id, against_idx, edge_attr])

    # Flip node dictionary
    inv_nodes = {v: k for k, v in node_dict.items()}

    # Create nodes in Networkx format
    for nodeid, coords in inv_nodes.items():
        # Create node
        n = [nodeid, {'node_id': nodeid, 'x': coords[0], 'y': coords[1]}]
        node_list.append(n)

    # Create the NetworkX graph
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(node_list)
    graph.add_edges_from(edge_list)
    graph.graph['crs'] = gdf.crs
    graph.graph['name'] = "Digiroad 2.0 NetworkX MultiDiGraph"

    print("Lasted %s seconds" % (round(time.time() - tot_t, 1)))
    return graph

def build_igraph_from_Digiroad(gdf, direction='AJOSUUNTA',
                                           both_ways=2, against=3, along=4):
    """Creates a iGraph network from Digiroad 2.0 road network GeoDataFrame.

    Parameters
    ----------

    gdf : GeoDataFrame
        GeoDataFrame containing Digiroad 2.0 road network data.

    direction : str
        Name for column that contains information about the allowed driving directions

    both_ways : int
        Value specifying that the road is drivable to both directions.

    against : int
        Value specifying that the road is drivable against the digitizing direction.

    along : int
        Value specifying that the road is drivable along the digitizing direction.
    """
    import igraph

    from_col = 'from_node_id'
    to_col = 'to_node_id'

    # Containers for nodes and edges
    tot_t = time.time()
    node_dict = {}
    node_attributes = []
    edge_list = []
    edge_attributes = []

    # Start nodeids from 0
    i = 0

    # Get unique set of nodes
    for edge in gdf.itertuples():
        coords = edge.geometry.coords
        # Get from and to nodeids
        fr, to = coords[0], coords[-1]
        node_dict[fr] = i
        i += 1
        node_dict[to] = i
        i += 1

    # Make sequential numbers for all nodes
    # Start nodeids from 0
    i = 0
    for nodecoords, nodeid in node_dict.items():
        node_dict[nodecoords] = i
        i += 1


    # Generate edge dictionary
    for edge in gdf.itertuples():
        coords = edge.geometry.coords
        # Get from and to coordinates
        fr, to = coords[0], coords[-1]

        # Get nodeids for the edge
        from_node_id = node_dict[fr]
        to_node_id = node_dict[to]

        # Edge attributes
        edge_attr = dict(edge._asdict())
        # Remove unnecessary attributes
        del edge_attr['Index']

        # Create edge in Networkx format
        if edge_attr[direction] == both_ways:

            # If road is bi-directional add it in both ways
            # ---------------------------------------------

            # Along
            edge_list.append([from_node_id, to_node_id])
            # Take a deepcopy with dict-comprehension,
            # so that from_node_id and to_node_id attribute info stays correct
            # in the dictionary. This is needed only with bi-directional road segments.
            along_attr = dict((k, v) for k, v in edge_attr.items())
            along_attr[from_col] = from_node_id
            along_attr[to_col] = to_node_id
            edge_attributes.append(along_attr)

            # Against - Flip the link nodes
            edge_list.append([to_node_id, from_node_id])
            edge_attr[from_col] = to_node_id
            edge_attr[to_col] = from_node_id
            edge_attributes.append(edge_attr)

        elif edge_attr[direction] == along:

            # Along
            edge_list.append([from_node_id, to_node_id])
            edge_attr[from_col] = from_node_id
            edge_attr[to_col] = to_node_id
            edge_attributes.append(edge_attr)

        elif edge_attr[direction] == against:

            # Against - Flip the link nodes
            edge_list.append([to_node_id, from_node_id])
            edge_attr[from_col] = to_node_id
            edge_attr[to_col] = from_node_id
            edge_attributes.append(edge_attr)

    # Flip node dictionary
    inv_nodes = {v: k for k, v in node_dict.items()}
    del node_dict

    # Create nodes in Networkx format
    for nodeid, coords in inv_nodes.items():
        # Create node attributes
        n_attributes = {'node_id': nodeid, 'x': coords[0],
                            'y': coords[1]}

        node_attributes.append(n_attributes)
    del inv_nodes

    # Convert to DataFrame so that it is easy to pass the data in correct format
    node_attributes = pd.DataFrame(node_attributes)
    edge_attributes = pd.DataFrame(edge_attributes)

    # Create directed graph from Digiroad
    graph = igraph.Graph(n=len(node_attributes), directed=True, edges=edge_list,
                         vertex_attrs=node_attributes.to_dict(orient='list'),
                         edge_attrs=edge_attributes.to_dict(orient='list'))

    print("Lasted %s seconds" % (round(time.time() - tot_t, 1)))
    return graph

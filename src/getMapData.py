import osmnx as ox
import matplotlib.pyplot as plt
import time
import sys
from osmnx._errors import InsufficientResponseError

def main():
    location = ["", "Padova", "Veneto", "Italy"]
    validQuery = False
    while validQuery == False:
        keyboard = input("Specify city, province, region, state (splitted with single commas). \
                        \nExample: EMPTY,Padova,Veneto,Italy \
                        \n(Note: use EMPTY to not specify a field) \
                        \nWaiting for location: ");
        location = [word for word in keyboard.split(",") if word != "EMPTY"]
        queryLocation = ", ".join(location)
        imagePath = "_".join(location) +"_network.png"

        ox.settings.log_console = True
        ox.settings.use_cache   = True

        userValidResponse = False
        while userValidResponse == False:
            keyboard = input(f"\nLocation{'\033[92m'} {queryLocation} {'\033[0m'}will be obtained from OpenStreetMap, continue? (Y/n): ")
            if keyboard == "Y" or keyboard == "y" or keyboard == "":
                validQuery = True
                userValidResponse = True
            elif keyboard == "N" or keyboard == "n":
                userValidResponse = True
            else:
                print("Invalid response.")

        if validQuery:
            print(f"Starting download for: {queryLocation}")

            try:
                G = ox.graph_from_place(queryLocation, network_type="all", simplify=True, retain_all=False)
            except InsufficientResponseError as e:
                print(f"\n{'\033[91m'}ERROR: specified location not found by OSM! Check the input given and try again.{'\033[0m'}", file=sys.stderr)
                time.sleep(1);
                validQuery = False
            except Exception as e:
                print(f"{'\033[91m'}There is an unexpected error. {'\033[0m'}" + e);
                print(f"Quitting the program...");
                sys.exit(1)

    print("Resulting graph:")
    print(f"Nodes: {len(G.nodes):,}")
    print(f"fields for each node: {list(G.nodes(data=True))[0]}")
    print(f"Edges: {len(G.edges):,}")
    print(f"fields for each edge: {list(G.edges(data=True))[0]}")
    fig, ax = ox.plot_graph(G, filepath=imagePath, node_size=0, edge_color="#006600",
                        edge_linewidth=0.8, show=False, close=True, save=True, bgcolor="w",)
    print(f"\nPlot of the graph saved in {imagePath}")

    dataPath = "_".join(location) + "_full_network.gpkg"
    ox.save_graph_geopackage(G, filepath=dataPath)

    print("\nData has been saved in the current directory.")

    userConfirmation = False
    while userConfirmation == False:
        keyboard = input("Do you also want to convert the .gpkg file into a .csv? \nAnswer (Y/n): ")
        if keyboard == "Y" or keyboard == "y" or keyboard == "":
            userConfirmation = True
        elif keyboard == "N" or keyboard == "n":
            print("Check the current directory for the resulting data and plot. Now quitting...")
            sys.exit(0)
        else:
            print("Invalid response.")

    csvFilename = "_".join(location)
    convertGpkgToCsv(G, csvFilename)
    print("\nCheck the current directory for the resulting data and plot. Now quitting...")

# converts a .gpkg file to 2 csv files, one for the nodes and one for the edges.
def convertGpkgToCsv(graph, dataFilename):
    # Nodes extraction #
    # GDF-related columns are removed (geometry) and the OSM id is discarded for a sequential Id.
    nodesData = ox.graph_to_gdfs(graph, edges=False)
    nodesData = nodesData.reset_index()
    nodesData = nodesData.drop(columns=['geometry'])

    nodesFilename = f"{dataFilename}_nodes.csv"
    nodesData.to_csv(nodesFilename, index=False)
    print(f"Saved: {nodesFilename} ({len(nodesData):,} nodes)")

    # Edges extraction #
    EdgesData = ox.graph_to_gdfs(graph, nodes=False)
    EdgesData = EdgesData.reset_index()
    EdgesData = EdgesData.drop(columns=['geometry'])

    edgesFilename = f"{dataFilename}_edges.csv"
    EdgesData.to_csv(edgesFilename, index=False)
    print(f"Saved: {edgesFilename} ({len(EdgesData):,} edges)")


if __name__ == "__main__":
    main()

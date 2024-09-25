from requests import get
import pandas as pd
from pathlib import Path
from pprint import pprint
import matplotlib.pyplot as mpl
from pywaffle import Waffle
import seaborn as sns

# #b68863 dark chess square colour
# #f0dab7 light chess square colour




def get_chess_data() -> pd.DataFrame:

    filepath = Path(r".\TidyTuesday\data\lichess.csv")

    if not filepath.exists():

        with filepath.open(mode="w") as file:
            data = get('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2024/2024-10-01/chess.csv').text
            file.write(data)

    df_lichess = pd.read_csv(filepath)

    return df_lichess


def get_wins_values(df_lichess: pd.DataFrame) -> dict[str, int]:

    return {
        winner: df_lichess[df_lichess['winner'] == winner].shape[0] 
        for winner in df_lichess['winner'].unique()
    }


def draw_waffle_plot(win_values: list[int, int, int]) -> None:

    filepath = Path("./TidyTuesday/plots/waffle_plot_chess_wins.png")

    figure = mpl.figure(
        figsize= (12, 12),
        FigureClass = Waffle,
        rows = 34,
        columns = 23,
        values = win_values,
        vertical = True,
        colors = ["#FFFFFF","#888888","#000000"],
        title = {
            "label": "Wins by Colour\n(1 square ≈ 25 wins)",
            "loc": "center",
            "fontdict": {
                "fontsize": 64,
            }
        },
        # icons = "chess-pawn",
        # font_size = 4,
        interval_ratio_x = 0.8,
        interval_ratio_y = 0.8,
        plot_anchor = "SE"
    )

    figure.savefig(
        filepath, 
        facecolor="#b68863", 
        bbox_inches="tight",
        pad_inches = 0.25
        )
    

def draw_column_chart(data: pd.DataFrame) -> None:

    filepath = Path("./TidyTuesday/plots/barplot_opening_freq.png")

    figure = mpl.figure(figsize=(12,12))
    sns.set_style("ticks", {"axes.facecolor": "#f0dab7"})
    chart = sns.barplot(
        data=data, 
        x="opening_groupname", 
        y="count",
        hue="opening_groupname",
        palette= sns.color_palette("crest"),
        fill=True
        )
    figure.add_axes(chart)
    mpl.title("Most Popular Openings", {"fontsize": 64})
    mpl.xlabel("Opening", {"fontsize": 32})
    mpl.xticks(rotation = 60)
    mpl.ylabel("Number of Games used for", {"fontsize": 32})
    figure.savefig(
        filepath, 
        facecolor="#f0dab7", 
        bbox_inches="tight",
        pad_inches = 0.25
        )


def get_data_for_waffle_plot(data) -> tuple[list, list]:

    values: dict[str, int] = get_wins_values(df_lichess=data)
    white_wins: int = values['white']
    black_wins: int = values['black']
    draws: int = values['draw']
    win_values: list[int, int, int] = [white_wins, draws, black_wins]
    win_percents:list[float, float, float] = [str(round((value/sum(win_values))*100, 1))+"%" for value in win_values]

    return win_values, win_percents
    

def clean_data_for_barplot(data) -> pd.DataFrame:

    df_lichess: pd.DataFrame = data
    openings = df_lichess["opening_name"]
    openings = openings.str.replace("|", ":")
    openings_group = openings.str.split(":", expand=True)[0]
    df_lichess["opening_groupname"] = openings_group

    df_openings_counts = df_lichess[["opening_groupname", "game_id"]].groupby("opening_groupname").count()
    df_openings_counts.rename(columns={"game_id": "count"}, inplace=True)

    df_openings_counts.sort_values("count", ascending=False, inplace=True)
    df_top_openings = df_openings_counts[0:15]
    df_other_openings = pd.DataFrame.from_records(
            {
            "opening_groupname": ["Other"],
            "count": [df_openings_counts["count"].sum() - df_top_openings["count"].sum()]
            }
        )
    df_other_openings.set_index("opening_groupname", inplace=True)
    df_openings_counts = pd.concat([df_top_openings, df_other_openings])
    return df_openings_counts


def get_data_for_grouped_columns(data):

    df_lichess: pd.DataFrame = data
    openings = df_lichess["opening_name"]
    openings = openings.str.replace("|", ":")
    openings_group = openings.str.split(":", expand=True)[0]
    df_lichess["opening_groupname"] = openings_group

    df_openings_counts = df_lichess[["opening_groupname", "game_id"]].groupby("opening_groupname").count()
    df_openings_counts.rename(columns={"game_id": "count"}, inplace=True)

    df_openings_counts.sort_values("count", ascending=False, inplace=True)
    df_top_openings = df_openings_counts[0:5].reset_index() 

    df_openings_data = df_lichess[df_lichess["opening_groupname"].isin(list(df_top_openings["opening_groupname"].unique()))]
    
    totals =  df_openings_data[["opening_groupname", "game_id"]].groupby(["opening_groupname"]).count().reset_index()
    totals.rename(columns={"game_id": "total"}, inplace=True)
    
    df_openings_data = df_openings_data[["opening_groupname", "winner", "game_id"]].groupby(["opening_groupname", "winner"]).count().reset_index()
    df_openings_data.rename(columns={"game_id": "count"}, inplace=True)


    df_openings_data = df_openings_data.merge(totals, "outer", on="opening_groupname")

    df_openings_data["ratio"] = df_openings_data["count"] / df_openings_data["total"] * 100

    return df_openings_data


def draw_grouped_columns(data):

    filepath = Path("./TidyTuesday/plots/grouped_bar_top5openings.png")

    figure = mpl.figure(figsize=(12,12))
    sns.set_style("ticks", {"axes.facecolor": "#f0dab7"})

    colours = ["#000000", "#888888", "#FFFFFF"]

    chart = sns.barplot(
        data=data, 
        x="opening_groupname", 
        y="count",
        hue="winner",
        palette= sns.color_palette(colours),
        fill=True
        )
    
    figure.add_axes(chart)

    mpl.title("Win splits for popular openings", {"fontsize": 64})
    mpl.xlabel("Opening", {"fontsize": 32})
    mpl.xticks(rotation = 60)
    mpl.ylabel("Games won", {"fontsize": 32})

    figure.savefig(
        filepath, 
        facecolor="#f0dab7", 
        bbox_inches="tight",
        pad_inches = 0.25
        )


if __name__ == "__main__":

    df_lichess = get_chess_data()

    win_values, win_percents = get_data_for_waffle_plot(df_lichess)
    draw_waffle_plot(win_values=win_values)

    clean_openings_df = clean_data_for_barplot(df_lichess)
    draw_column_chart(clean_openings_df)

    data = get_data_for_grouped_columns(df_lichess)

    draw_grouped_columns(data)


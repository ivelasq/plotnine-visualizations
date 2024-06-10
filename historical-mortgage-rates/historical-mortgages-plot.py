import pandas as pd
import os
import matplotlib.font_manager as fm
from siuba import _, mutate
from plotnine import (
    ggplot,
    geom_line,
    aes,
    scale_x_datetime,
    scale_y_continuous,
    scale_color_manual,
    theme_minimal,
    theme,
    element_text,
    element_rect,
    labs,
)

project_dir = os.getcwd()
font_path = os.path.join(project_dir, "Raleway-VariableFont_wght.ttf")
prop = fm.FontProperties(fname=font_path)

rates_clean = pd.read_csv("data/rates_clean.csv")
rates_clean["date"] = pd.to_datetime(rates_clean["date"])

rates_long = rates_clean.melt(
    id_vars="date",
    value_vars=["fixed_30", "fixed_15"],
    var_name="type",
    value_name="rate",
).dropna()

p = (
    ggplot(rates_long, aes(x="date", y="rate", color="type"))
    + geom_line()
    + scale_x_datetime(date_breaks="10 years", date_labels="%Y")
    + scale_y_continuous(breaks=range(0, 20, 2))
    + scale_color_manual(values=["#DB583A", "#305776"], labels=["15-year", "30-year"])
    + theme_minimal()
    + labs(
        title="15- and 30-Year Fixed Rate Mortgage Average in the United States",
        caption="Source: FRED, Federal Reserve Bank of St. Louis",
        x="",
        y="",
        color="",
    )
    + theme(
        title=element_text(hjust=0, fontproperties=prop),
        text=element_text(fontproperties=prop),
        plot_background=element_rect(fill="white")
    )
)

p.show()

p.save("./historical-mortgage-rates/historical_mortgages_plot.png", dpi=300, height=4.5, width=8)

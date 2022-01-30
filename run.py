from re import M
from utils import (
    gsheet_to_df,
    make_index_html,
    make_geojsons
)

DF = gsheet_to_df()
make_index_html(DF)
make_geojsons(DF)
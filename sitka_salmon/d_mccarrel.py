import os
import numpy as np
import pandas as pd
import datetime
from sitka_salmon import config


_mark_present = {
    'N': 0.0,
    'Y': 1.0,
    'Null': np.nan,
    '': np.nan,
    ' ': np.nan,
}


def get():
    ifname = os.path.join(config.HARNESS, 'data', 'McCarrel', 'Chum Data 2013-2021.csv')

    df = pd.read_csv(ifname)
    df['MarkPresent'] = df.MarkPresent.map(lambda x: _mark_present[x])

    df['year'] = df.SurveyDate.map(lambda x: int(x[-4:]))
    df['SurveyDate'] = df.SurveyDate.map(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date())
    return df

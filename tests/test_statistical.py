
import pandas as pd
from tn_anomaly.statistical import rolling_iqr, moving_average_deviation, percentile_detection, dynamic_threshold

def test_statistical_utilities():
    s=pd.Series(list(range(1,101))+[1000])
    assert len(rolling_iqr(s,20))==len(s)
    assert moving_average_deviation(s,20).prediction.iloc[-1]==1
    assert percentile_detection(s).prediction.iloc[-1]==1
    assert len(dynamic_threshold(s,20))==len(s)

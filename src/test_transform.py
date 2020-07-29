import pytest
from src.transform import get_binary
from src.transform import get_length
from src.transform import get_dept_hour_bucket
import pandas as pd
import numpy as np



def test_get_binary():
    # happy path
    d = {"DEP_DELAY":[1, -5, 4, 6, -7, 2, -2]}
    df = pd.DataFrame(d)
    assert pd.Series(['delay', 'on_time', 'delay', 'delay', 'on_time', 'delay', 'on_time']).equals(pd.Series(get_binary(df)))

def test_get_binary_none():
    # unhappy path
    d = {"visible_min": [0, 1, 3, 4, 6, 1, 5]}
    df = pd.DataFrame(d)
    # with pytest.raises(AttributeError):
    assert get_binary(df) is None

def test_get_length():
    # happy path
    d = {"CRS_ELAPSED_TIME": [45, 120, 119, 60, 45, 87, 100]}
    df = pd.DataFrame(d)
    assert pd.Series([0, 2, 1, 1, 0, 1, 1]).equals(get_length(df))

def test_get_length_none():
    # happy path
    d = {"CRS_ELAPSED_TIME_1": [45, 120, 119, 60, 45, 87, 100]}
    df = pd.DataFrame(d)
    assert get_length(df) is None

def test_get_dept_hour_bucket():
    # happy path
    d = {"CRS_DEP_TIME": ["59", "1001", "1202", "143"]}
    df = pd.DataFrame(d)
    assert pd.Series(['0', "10", "12", "01"]).equals(pd.Series(get_dept_hour_bucket(df)))

def test_get_dept_hour_bucket_none():
    # happy path
    d = {"CRS_DEP_TIME_1": ["59", "1001", "1202", "143"]}
    df = pd.DataFrame(d)
    assert get_dept_hour_bucket(df) is None
import requests
import pandas as pd
import numpy as np
from datetime import datetime


class TksRequest():
    def __init__(self) -> None:
        pass


    def organize_data(self, df:pd.DataFrame) -> pd.DataFrame:
        df.drop("entry_id", axis = 1, inplace = True)
        df["created_at"] = df["created_at"].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"))
        df["date"] = np.nan * len(df)
        df["time"] = np.nan * len(df)
        df["local"] = np.nan * len(df)
        for idx, value in enumerate(df.created_at):
            df["date"][idx] = df["created_at"][idx].split("-")[0]
        for idx, value in enumerate(df.created_at):
            df["time"][idx] = df["created_at"][idx].split("-")[1]
        for idx, value in enumerate(df.created_at):
            df["local"][idx] = df["created_at"][idx].split("-")[-1]
        df.drop("created_at", axis = 1, inplace = True)
        df = df.reindex(["date", "time", "local", "field1", "field2", "field3", "field4", "field5", "field6", "field7", "field8"], axis = 1)
        df.local = df.local.apply(lambda x: 0 if x == "UTC" else 1)
        for col in df.columns:
            df[col] = df[col].astype(float)
        return df


    def get_data_response(self) -> pd.DataFrame:
        config_data = requests.get("https://api.thingspeak.com/channels/2167188/feeds.json").json()["feeds"]
        df = pd.DataFrame(config_data)
        df = self.organize_data(df)
        return df



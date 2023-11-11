"""Preprocess eye tracking data"""

import pandas as pd
import json 

from keys.keys import AFE_PATHS, SENTIMENT_PATH, AFE_PREPROCESSED_PATH

def preprocess_file(file): 
    # Read data
    with open(file) as f: 
        s = f.read()

    # Normalize JSON
    d = json.loads(s)
    df = pd.json_normalize(d)

    # Drop battery and auxSensors
    df = df.loc[:, ~df.columns.str.startswith("battery")]
    df = df.loc[:, ~df.columns.str.startswith("auxSensors")]

    # Preprocess AFE data
    eyes = ["left", "right"]
    df[eyes] = pd.json_normalize(df["afe"]).iloc[:, :2]
    for eye in eyes:
        df_ = pd.json_normalize(df[eye])
        df_.columns = [f"{eye}_{col}" for col in df_.columns]
        
        # Preprocess i data
        temp = df_[eye + "_i"].apply(pd.Series)
        temp.columns = [eye + "_i" + "_" + str(c) for c in temp.columns]
        df_ = pd.concat([df_, temp], axis=1)

        # Process m data 
        df_[eye + "_m"] = [x[0] for x in df_[eye + "_m"]]
        temp = df_[eye + "_m"].apply(pd.Series)
        temp.columns = [eye + "_m" + "_" + str(c) for c in temp.columns]
        df_ = pd.concat([df_, temp], axis=1)

        df = pd.concat([df, df_], axis=1)

    # Drop unnecessary columns
    cols_to_drop = ["afe", "left", "right", "left_i", "right_i", "left_m", "right_m", "left_t", "right_t", "left_m_6", "left_m_7", "right_m_6", "right_m_7"]
    df = df.drop(columns=cols_to_drop)

    return df

def add_sentiment_to_afe(df, sentiment_df): 
    # Standardize time
    df["left_ticktime_standardized"] = df["left_ticktime"] - df["left_ticktime"].min()
    sentiment_df["start_standardized"] = sentiment_df["start"] - sentiment_df["start"].min()
    sentiment_df["end_standardized"] = sentiment_df["end"] - sentiment_df["start"].min()

    # Add sentiment to AFE data
    for i in range(len(sentiments)): 
        start = sentiments.iloc[i]["start_standardized"]
        end = sentiments.iloc[i]["end_standardized"]
        sentim = sentiments.iloc[i]["Sentiment"]
        df.loc[(df["left_ticktime_standardized"] >= start) & (df["left_ticktime_standardized"] <= end), "sentiment"] = sentim

    return df

if __name__ == "__main__": 
    # Preprocess AFE data
    dfs = []
    for file in AFE_PATHS: 
        dfs.append(preprocess_file(file))

    # Transform to dataframe
    df = pd.concat(dfs, ignore_index=True)

    # Rename columns
    renames = {
        "left_i_0": "left_ticktime",
        "right_i_0": "right_ticktime",
        "left_i_1": "left_timestamp",
        "right_i_1": "right_timestamp",
        "left_i_2": "left_status",
        "right_i_2": "right_status",
        "left_i_3": "left_counter",
        "right_i_3": "right_counter",
        "blinks.left.peakTime": "left_blinks_peakTime",
        "blinks.left.index": "left_blinks_index",
        "blinks.left.beginTime": "left_blinks_beginTime",
        "blinks.left.endTime": "left_blinks_endTime",
        "blinks.right.peakTime": "right_blinks_peakTime",
        "blinks.right.index": "right_blinks_index",
        "blinks.right.beginTime": "right_blinks_beginTime",
        "blinks.right.endTime": "right_blinks_endTime",
    }
    df = df.rename(columns=renames)

    # Read sentiment data
    sentiments = pd.read_csv(SENTIMENT_PATH)

    # Add sentiment to AFE data
    df = add_sentiment_to_afe(df, sentiments)

    # Save to CSV
    df.to_csv(AFE_PREPROCESSED_PATH, index=False)


    
    
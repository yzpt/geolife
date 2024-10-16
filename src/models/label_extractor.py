import pandas as pd
import os

class LabelExtractor:
    def extract_labels(self, user_path: str) -> pd.DataFrame:
        """
        Extract the labels from the labels.txt file, return a DataFrame
        """
        labels_file = os.path.join(user_path, 'labels.txt')
        if not os.path.exists(labels_file):
            return pd.DataFrame(columns=['start_datetime', 'end_datetime', 'mode'])

        df_labels = pd.DataFrame(columns=['start_datetime', 'end_datetime', 'mode'])
        with open(labels_file) as f:
            for line in f:
                if 'Time' in line:
                    continue
                start_datetime, end_datetime, mode = line.strip().split('\t')
                df_labels = pd.concat([df_labels, pd.DataFrame({
                    'start_datetime': [start_datetime],
                    'end_datetime': [end_datetime],
                    'mode': [mode]
                })])
        
        df_labels['start_datetime'] = pd.to_datetime(df_labels['start_datetime'])
        df_labels['end_datetime'] = pd.to_datetime(df_labels['end_datetime'])
        return df_labels

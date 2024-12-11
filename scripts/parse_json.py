import json
from typing import List, Optional
import pandas as pd


""" example data:
{ 
    "periodStart": "15/02/11",
    "periodEnd": "34/08/21",
    "monthlyPostingDay": 11,
    "comments": [
        ["2/3/21", "Justin Bieber", 5],
        ["5/4/21", "Lady Gaga", 6],
        ["5/4/21", "Snoop Dog", 2],
        ["13/5/21", "Justin Bieber", 3]
    ]
}
"""

### requirements:
# no post data is present in the json file, so will write the class in a generic way that can also take into "post" interaction, pending future data availability for further test usage. for "comment" interaction, process the data as per the following requirements 

# 1. parse the specified json data - assumed to come from the scraper
# 2. store the number of (i) posts and (ii) comments on a daily basis across the time period in a python class
# 3. calculate the sum of posts and comments on a daily basis
# 4. calculate the aggregate number of posts and comments on a monthly basis
# 5. store the monthly totals for the whole period for (i) posts and (ii) comments in a csv file


### python class design:
# class name: PostingStats
# attributes:
# - user_id: not present in the json file, but assumed to be present in the future
# - periodStart: datetime
# - periodEnd: datetime
# - monthlyPostingDay: int
# - comments: list[list[str, str, int]]
# methods:
# - get_interaction_daily_bytype(interaction_type: str): dict[str, int]
# - calculate_interaction_daily_sum(): dict[str, int]
# - calculate_aggregate_monthly_sum(): dict[str, int]
# - save_monthly_interaction_totals(filepath: str): None


class InteractionStats:
    def __init__(self, data_file: str, user_id: Optional[str] = None, interaction_types: List[str] = ['comments','posts']):
        """
        Initialize the InteractionStats class
        - set up attributes and load the data
        - set up interaction types
        - set up interaction dataframe for easy data stat generation
        """
        self.data_file = data_file
        self.user_id = user_id
        self.data = self.load_data()
        self.periodStart = self.data['periodStart']
        self.periodEnd = self.data['periodEnd']
        self.monthlyPostingDay = self.data['monthlyPostingDay']
        self.set_interaction_types(interaction_types)
        self.__set_interaction_df__()

    def set_interaction_types(self, interaction_types: List[str]):
        """
        Set up interaction types
        """
        self.interaction_types = interaction_types

    def load_data(self):
        """
        Load the data from the json file
        """
        with open(self.data_file, 'r') as file:
            return json.load(file)

    def __set_interaction_df__(self):
        """
        set up interaction dataframe for easy data stat generation, catering for different interaction types
        """
        interactions_list = []
        for interaction_type in self.interaction_types:
            if interaction_type in self.data.keys():
                for item in self.data[interaction_type]:
                    item_dict = {
                        'interaction_type': interaction_type,                        
                        'date': item[0],
                        'author': item[1], 
                        'daily_interaction_number': item[2],
                    }
                    interactions_list.append(item_dict)
        self.interactions_df = pd.DataFrame.from_dict(interactions_list)
        # Add month column in mm/yy format
        self.interactions_df['month'] = pd.to_datetime(self.interactions_df['date']).dt.strftime('%m/%y')

    def get_interaction_daily_num_bytype(self, interaction_type: str) -> int:
        """
        Get the daily interaction numbers by type
        """
        return self.interactions_df[self.interactions_df['interaction_type'] == interaction_type].groupby('date')['daily_interaction_number'].sum().to_dict()

    def calculate_interaction_daily_sum(self):
        """
        Calculate the daily interaction sum of all interaction types
        """
        return self.interactions_df.groupby('date')['daily_interaction_number'].sum().to_dict()

    def calculate_aggregate_monthly_sum(self):
        """
        Calculate the monthly interaction sum of each interaction type, and return a dictionary of the results
        """
        monthly_totals = {}
        for interaction_type in self.interaction_types:
            type_df = self.interactions_df[self.interactions_df['interaction_type'] == interaction_type]
            monthly_totals[interaction_type] = type_df.groupby('month')['daily_interaction_number'].sum().to_dict()
        return monthly_totals

    def save_monthly_interaction_totals(self, filepath: str):
        """
        Save the monthly interaction totals to a csv file
        """
        monthly_totals = self.calculate_aggregate_monthly_sum()
        monthly_totals_df = pd.DataFrame.from_dict(monthly_totals).fillna(0)
        monthly_totals_df.to_csv(filepath, index=False)



if __name__ == '__main__':
    # class usage example
    # 1. load the data
    file_path = '../data/data.json'
    instat = InteractionStats(file_path)

    # 2. get the daily interaction numbers by type
    interaction_daily_num = instat.get_interaction_daily_num_bytype('comments')
    
    # 3. calculate the daily interaction sum
    interaction_daily_sum = instat.calculate_interaction_daily_sum()
    
    # 4. calculate the monthly interaction sum
    monthly_totals = instat.calculate_aggregate_monthly_sum()
    
    # 5. save the monthly interaction totals to a csv file
    monthly_totals = instat.calculate_aggregate_monthly_sum()
    instat.save_monthly_interaction_totals('monthly_interaction_totals.csv')


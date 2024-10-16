import os
from notion_client import Client
from pathlib import Path
from dotenv import load_dotenv
import datetime, pytz
from notion_client import Client, APIResponseError
import logging

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
notion = Client(auth=os.environ["NOTION_TOKEN"])

def get_current_time():
    korea_timezone = pytz.timezone('Asia/Seoul')
    now = datetime.datetime.now(korea_timezone)
    return now.strftime('%Y-%m-%d')

def get_a_list_of_workflows_created_today_from_notion():
    try:
        current_time = get_current_time()
        list_of_workflows_created_today = notion.databases.query(
            database_id=os.environ['NOTION_DATABASE_ID'],
            filter={
                "and": [
                    {
                        "property": "날짜",
                        "date": {
                            "on_or_after": current_time
                        }
                    },
                ],
            },
        )

        contents = list_of_workflows_created_today['results']
        for content in contents:
            page_id = content['id']
            properties = content['properties']
            title = properties["이름"]["title"][0]["text"]["content"]
            enrolled_user_name = properties['작성자']['people']
            label = properties["라벨"]['multi_select']
            print(title)
            if title.startswith("#20") and len(title) == 5 and enrolled_user_name ==[] and label == []:
                notion.pages.update(
                    page_id= page_id,
                    archived= True
                )
                return 
    except APIResponseError as error:
        logging.error(f"API error: {error}")


get_a_list_of_workflows_created_today_from_notion()
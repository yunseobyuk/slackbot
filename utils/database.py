import copy
import datetime
import json
import logging
import os
import uuid
from pathlib import Path
from pprint import pprint

import pytz
from dotenv import load_dotenv
from notion_client import APIResponseError, Client

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
notion = Client(auth=os.environ["NOTION_TOKEN"])


def get_user_information(slack_user_id):
    with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "r") as json_file:
        json_data = json.load(json_file)
        return json_data[slack_user_id]


def get_current_time_detail():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def string_to_list(text):
    result = []
    splitted_contents = text.split("\n")

    for value in splitted_contents:
        temp = delete_indentions(value)
        if temp.startswith("#") or temp.startswith("*"):
            result.append(value)
        else:
            if result == []:
                result.append(value)
            else:
                result[-1] += value
    return result


# Users
def get_username(slack_user_id):
    with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "r") as json_file:
        json_data = json.load(json_file)
        return json_data[slack_user_id]["slack_user_name"]


def get_users_notion_id(slack_user_id):
    with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "r") as json_file:
        json_data = json.load(json_file)
        return json_data[slack_user_id]["notion_user_id"]


def get_user_names_on_a_notion_worktask_page():
    try:
        response = notion.databases.query(
            database_id=os.environ["NOTION_DATABASE_ID"],
            filter={
                "property": "날짜",
                "date": {"on_or_after": "2024-01-01"},
            },
        )
        users_name_and_email = []
        user_name_list = []

        for result in response["results"]:
            if result["properties"]["작성자"]["people"] == []:
                continue
            user_email = result["properties"]["작성자"]["people"][0]["person"]["email"]
            user_name = result["properties"]["작성자"]["people"][0]["name"]
            user_id = result["properties"]["작성자"]["people"][0]["id"]

            if user_name in user_name_list:
                continue

            users_name_and_email.append(
                {
                    "user_email": user_email,
                    "user_name": user_name,
                    "user_id": user_id,
                }
            )

            user_name_list.append(user_name)

        return users_name_and_email
    except APIResponseError as error:
        logging.error(f"API error: {error}")


def split_todos(aligned_last_updated_pages_content):
    todo_samples = [
        "To do",
        "To do:",
        "To do: ",
        "To-do",
        "To-do:",
        "To-do :",
        "Todo",
        "Todo:",
        "Todo: ",
        "to do",
        "todo",
        "to-do",
        "to do:",
        "todo:",
        "to-do:",
        "to do :",
        "todo :",
        "to-do :",
    ]
    doing_samples = ["Doing", "Doing:", "Doing :", "doing", "doing:", "doing :"]
    done_samples = ["Done", "Done:", "Done :", "done", "done:", "done :"]

    todo_counter = 0
    doing_counter = 0
    done_counter = 0
    for i in range(len(aligned_last_updated_pages_content["elements"])):
        tblock = aligned_last_updated_pages_content["elements"][i]
        if tblock["type"] == "rich_text_section":
            for elem in tblock["elements"]:
                if elem["text"] in todo_samples:
                    todo_counter = i
                elif elem["text"] in doing_samples:
                    doing_counter = i
                elif elem["text"] in done_samples:
                    done_counter = i

    todos = copy.deepcopy(aligned_last_updated_pages_content)
    doings = copy.deepcopy(aligned_last_updated_pages_content)
    dones = copy.deepcopy(aligned_last_updated_pages_content)

    todos["elements"] = todos["elements"][todo_counter + 1 : doing_counter]
    doings["elements"] = doings["elements"][doing_counter + 1 : done_counter]
    dones["elements"] = dones["elements"][done_counter + 1 :]

    return todos, doings, dones


def get_a_recent_workflow_content_from_cache(slack_user_id):
    try:
        with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            if slack_user_id not in json_data:
                return None, None, None, None, None, None

            recent_workflow = json_data[slack_user_id]
            title = recent_workflow["title"]
            user_name = recent_workflow["user_name"]
            last_updated_date = recent_workflow["last_updated_date"]
            worktask_input = recent_workflow["content"]
            page_id = recent_workflow["page_id"]
            todos, doings, dones = split_todos(worktask_input)

            worktask_divided = {
                "todos": todos,
                "doings": doings,
                "dones": dones,
            }
            label = recent_workflow["label"]
            return worktask_divided, user_name, last_updated_date, title, label, page_id

    except Exception as error:
        logging.error(f"{error}")
        return None, None, None, None, None, None


def update_a_cache_worktask_located_at_the_backend_server(slack_user_id, new_contents):
    with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "r", encoding="utf-8") as json_file:
        if os.stat(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json").st_size == 0:
            with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "w") as json_file:
                json.dump({}, json_file, indent=4)

        json_data = json.load(json_file)

    notion_user_id = get_users_notion_id(slack_user_id)
    (
        aligned_last_updated_pages_content,
        enrolled_user_name,
        last_updated_date,
        title,
        label,
        page_id,
    ) = get_a_recent_workflow_content_from_notion(notion_user_id)

    new_contents = {
        "title": title,
        "label": label,
        "user_name": enrolled_user_name,
        "last_updated_date": last_updated_date,
        "content": aligned_last_updated_pages_content,
        "page_id": page_id,
    }

    json_data[slack_user_id] = new_contents

    with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    return "Success"


def format_database_data(database_data):
    todo_samples = [
        "To do",
        "To do:",
        "To do: ",
        "To-do",
        "To-do:",
        "To-do :",
        "Todo",
        "Todo:",
        "Todo: ",
        "to do",
        "todo",
        "to-do",
        "to do:",
        "todo:",
        "to-do:",
        "to do :",
        "todo :",
        "to-do :",
    ]
    initial_block = {"type": "rich_text", "elements": []}

    for block in database_data:
        block_type = block["type"]
        current_id = block["id"]

        if block[block_type] == {}:
            continue
        content = block[block_type]["rich_text"][0]["plain_text"] if block[block_type]["rich_text"] else " "
        annotations = block[block_type]["rich_text"][0]["annotations"] if block[block_type]["rich_text"] else {}

        keys_annotations = list(annotations.keys())
        styles = {}
        for key in keys_annotations:
            if annotations[key] == "false":
                annotations[key] = False
            elif annotations[key] == "true":
                annotations[key] = True

            if key == "strikethrough":
                styles["strike"] = annotations["strikethrough"]
            elif key == "color" or key == "underline":
                continue
            else:
                styles[key] = annotations[key]

        if block_type == "bulleted_list_item":
            initial_block["elements"].append(
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "indent": block["depth"],
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": content,
                                    "style": styles,
                                }
                            ],
                        },
                    ],
                }
            )
        elif block_type == "quote":
            initial_block["elements"].append(
                {
                    "type": "rich_text_quote",
                    "elements": [
                        {
                            "type": "text",
                            "text": content,
                            "style": styles,
                        },
                    ],
                }
            )
        elif block_type == "heading_1" or block_type == "heading_2" or block_type == "heading_3":
            initial_block["elements"].append(
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": content,
                            "style": {"bold": True},
                        },
                        {"type": "text", "text": "\n", "style": {}},
                    ],
                }
            )
            if content not in todo_samples:
                initial_block["elements"][-1]["elements"].insert(0, {"type": "text", "text": "\n", "style": {}})
        else:
            initial_block["elements"].append(
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": content,
                            "style": styles,
                        },
                    ],
                }
            )

        initial_block["block_id"] = current_id
    return initial_block


def enroll_users_id_to_notion(slack_user_id, slack_user_name, user_email, job_title, image_url):
    json_data = {}
    if not os.path.isfile(f"{os.environ['ROOT_PATH']}/db/user_info.json"):
        with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    if not os.path.isfile(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json"):
        with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "w") as json_file:
            json.dump({}, json_file, indent=4)

    try:
        notion_user_name = ""
        users_name_and_email = get_user_names_on_a_notion_worktask_page()
        notion_user_name = ""
        notion_user_id = ""
        for user in users_name_and_email:
            if user["user_email"] == user_email:
                notion_user_name = user["user_name"]
                notion_user_id = user["user_id"]
                break

        if notion_user_id == "":
            return "노션 데이터베이스에서 사용자를 찾을 수 없습니다. 노션 워크태스크 페이지에 글을 작성한 후 다시 시도해주세요."

        with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "r") as json_file:
            json_data = json.load(json_file)
            key_list = list(json_data.keys())
            if slack_user_id in key_list:
                return f"이미 등록된 계정입니다: {slack_user_name}"

            json_data[slack_user_id] = {
                "slack_user_name": slack_user_name,
                "notion_user_id": notion_user_id,
                "notion_user_name": notion_user_name,
                "user_email": user_email,
                "job_title": job_title,
                "image_url": image_url,
            }

        with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "w", encoding="utf-8") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        with open(f"{os.environ['ROOT_PATH']}/db/cache_worktask.json", "r") as json_file:
            json_data = json.load(json_file)
            if slack_user_id not in json_data:
                response = update_a_cache_worktask_located_at_the_backend_server(slack_user_id, {})
                if response != "Success":
                    return "Notion database에 등록된 워크태스크 문서가 없습니다. 새로운 워크태스크를 등록해주세요."

        return f"{slack_user_name} 님을 사용자 리스트에 새로 등록했습니다. 이제 지피다봇을 통해 워크태스크를 등록할 수 있습니다."
    except APIResponseError as error:
        logging.error(f"API error: {error}")


# Workflows
def get_current_time():
    # get current time. for example, 2021-07-21
    korea_timezone = pytz.timezone("Asia/Seoul")
    now = datetime.datetime.now(korea_timezone)
    return now.strftime("%Y-%m-%d")


def delete_indentions(text):
    for character in text:
        if character == " ":
            text = text[1:]
        else:
            break
    return text


def count_the_number_of_tabs(text):
    count = 0
    for character in text:
        if character == " ":
            count += 1
        else:
            break
    return count // 4


def split_dictionary_elements(original_dict):
    """
    Splits each element in the 'elements' key of the original dictionary into separate dictionaries.

    :param original_dict: The original dictionary with a key 'elements'.
    :return: A list of dictionaries, each containing one element from the original 'elements' list.
    """
    new_dictionaries = []
    for element in original_dict["elements"]:
        # Create a new dictionary with the same keys as the original except for 'elements'
        new_dict = {key: original_dict[key] for key in original_dict if key != "elements"}
        # Add the current element to the 'elements' key of the new dictionary
        new_dict["elements"] = [element]
        new_dictionaries.append(new_dict)

    return new_dictionaries


def analyze_relationships(task_list):
    # 결과를 저장할 리스트 초기화
    lines_list = task_list["elements"]
    new_lines_list = []
    for item in lines_list:
        if item["type"] == "rich_text_list":
            resp = split_dictionary_elements(item)
            new_lines_list.extend(resp)
        else:
            new_lines_list.append(item)
    lines_list = new_lines_list

    content_list = []
    result = []
    current_parent_uuid = None
    prior_depth = 0
    parent_stack = [None]
    # 각 항목에 대해 순회
    for item in lines_list:
        current_depth = 0
        if item["type"] == "rich_text_section":
            temp = item["elements"]
            if temp == []:
                continue
            if len(temp) != 1:
                for i in range(len(temp)):
                    if temp[i]["text"] != "\n":
                        content = temp[i]["text"]
                        key_style = list(item["elements"][0].keys())
                        if "style" in key_style:
                            style = item["elements"][0]["style"]
                        else:
                            style = {}
                        break
            else:
                content = item["elements"][0]["text"]
                key_style = list(item["elements"][0].keys())
                if "style" in key_style:
                    style = item["elements"][0]["style"]
                else:
                    style = {}
            text_format = "text"
        elif item["type"] == "rich_text_list":
            if item["elements"][0]["elements"] == []:
                continue
            content = item["elements"][0]["elements"][0]["text"]
            key_style = list(item["elements"][0]["elements"][0].keys())
            if "style" in key_style:
                style = item["elements"][0]["elements"][0]["style"]
            else:
                style = {}
            text_format = "bulleted_list_item"
            current_depth = item["indent"]
        elif item["type"] == "rich_text_quote":
            if item["elements"] == []:
                continue
            content = item["elements"][0]["text"]
            key_style = list(item["elements"][0].keys())
            if "style" in key_style:
                style = item["elements"][0]["style"]
            else:
                style = {}
            text_format = "quote"

        elif item["type"] == "heading_1":
            content = item["heading_1"]["rich_text"][0]["text"]["content"]
            style = item["heading_1"]["rich_text"][0]["annotations"]
            text_format = "heading_1"
        else:
            content = item["text"]
            style = item["style"]

        key_style = list(style.keys())
        if "strike" in key_style:
            style["strikethrough"] = style["strike"]
            del style["strike"]

        if content in content_list:
            content = content + " "

        content_list.append(content)
        item_dict = {
            "content": content,
            "uuid": str(uuid.uuid4()),
            "parent": None,
            "style": style,
            "children": [],
            "text_format": text_format,
        }

        # 현재 항목의 깊이가 이전 항목의 깊이보다 크면 부모 업데이트
        if current_depth > prior_depth:
            current_parent_uuid = result[-1]["uuid"]
            parent_stack.append(current_parent_uuid)
        # 깊이가 같으면 같은 부모
        elif current_depth == prior_depth:
            current_parent_uuid = parent_stack[-1]
        # 깊이가 작아지면(돌아올 때) 부모를 계속해서 이전 것으로 업데이트
        elif current_depth < prior_depth:
            for i in range(prior_depth - current_depth):
                parent_stack.pop()
            current_parent_uuid = parent_stack[-1]

        # 현재 항목의 부모 업데이트
        item_dict["parent"] = current_parent_uuid
        prior_depth = current_depth
        # 부모의 자식 목록 업데이트
        if current_parent_uuid:
            for r in result:
                if r["uuid"] == current_parent_uuid:
                    r["children"].append(content)
                    break

        result.append(item_dict)
    return result


def append_blocks(contents, pages_id):
    relationship_data = analyze_relationships(contents)
    content_and_block_id = {}
    for item in relationship_data:
        children = item["children"]
        text_format = item["text_format"]
        if text_format == "text":
            text_format = "paragraph"
        parent = item["parent"]
        appended_blocks = []
        content = item["content"]
        if parent == None:
            block = [
                {
                    f"{text_format}": {
                        "rich_text": [
                            {
                                "text": {"content": content},
                                "annotations": item["style"],
                            }
                        ]
                    }
                }
            ]
            notion_append_child_block_api_response = notion.blocks.children.append(pages_id, children=block)
            content_and_block_id[content] = notion_append_child_block_api_response["results"][0]["id"]

        if children:
            for child in children:
                style_for_child = next(
                    (item["style"] for item in relationship_data if item["content"] == child),
                    {},
                )
                block = {
                    f"{text_format}": {
                        "rich_text": [
                            {
                                "text": {"content": child},
                                "annotations": style_for_child,
                            }
                        ]
                    }
                }
                appended_blocks.append(block)
            block_id = content_and_block_id[content]
            notion_append_child_block_api_response = notion.blocks.children.append(block_id, children=appended_blocks)

            for i in range(len(notion_append_child_block_api_response["results"])):
                content_and_block_id[children[i]] = notion_append_child_block_api_response["results"][i]["id"]

    return "Success"


def extract_specific_information(data):
    # Initialize a dictionary to hold the extracted information
    extracted_info = {}
    heading = ""

    # Iterate over the data to find main headings and their respective contents
    for block in data:
        if block["type"] == "heading_1":
            heading = block["heading_1"]["rich_text"][0]["plain_text"]
            # Initialize a list to store items under this heading
            extracted_info[heading] = []

        elif block["type"] == "bulleted_list_item":
            # Extract the bullet point text
            if block["bulleted_list_item"]["rich_text"] == []:
                continue
            bullet_text = block["bulleted_list_item"]["rich_text"][0]["plain_text"]
            tabbing = block["depth"]
            bullet_text = "    " * tabbing + "* " + bullet_text
            if heading in extracted_info:
                extracted_info[heading].append(bullet_text)

    return extracted_info


def extract_documents(page_id, block_child_n_depth_data, depth=0):
    block_child_data = notion.blocks.children.list(block_id=page_id)
    # use recursive function to extract all data. if each block has children, then call this function again.
    for block_child in block_child_data["results"]:
        block_child["depth"] = depth
        block_child_n_depth_data.append(block_child)
        if block_child["has_children"] == True:
            child_block_id = block_child["id"]
            block_child_n_depth_data = extract_documents(child_block_id, block_child_n_depth_data, depth + 1)

    return block_child_n_depth_data


def dict_to_markdown(d):
    markdown_text = ""
    for key in d:
        markdown_text += f"# {key}\n"
        for item in d[key]:
            markdown_text += f"{item}\n"
    return markdown_text


def get_a_recent_workflow_content_from_notion(notion_user_id):
    try:
        sort_option = [{"property": "날짜", "direction": "descending"}]

        last_updated_page = notion.databases.query(
            database_id=os.environ["NOTION_DATABASE_ID"],
            filter={
                "and": [
                    {"property": "날짜", "date": {"on_or_after": "2024-01-01"}},
                    {"property": "작성자", "people": {"contains": notion_user_id}},
                ],
            },
            sorts=sort_option,
            page_size=1,
        )

        content = last_updated_page["results"][0]
        properties = content["properties"]

        last_updated_pages_id = content["id"]
        title = properties["이름"]["title"][0]["plain_text"]
        last_updated_date = properties["날짜"]["date"]["start"]
        enrolled_user_name = properties["작성자"]["people"][0]["name"]
        label = properties["라벨"]["multi_select"]
        if label == []:
            label = "작업중"
        else:
            label = label[0]["name"]

        last_updated_pages_content = extract_documents(last_updated_pages_id, [])
        aligned_last_updated_pages_content = format_database_data(last_updated_pages_content)

        # contents = extract_documents(response)
        return (
            aligned_last_updated_pages_content,
            enrolled_user_name,
            last_updated_date,
            title,
            label,
            last_updated_pages_id,
        )

    except APIResponseError as error:
        logging.error(f"API error: {error}")


def delete_indentions(text):
    for character in text:
        if character == " ":
            text = text[1:]
        else:
            break
    return text


def divided_contents(contents):
    splitted_contents = contents.split("\n")
    new_contents = []
    for i in range(len(splitted_contents)):
        temp = delete_indentions(splitted_contents[i])
        if temp.startswith("## ") or temp.startswith("# ") or temp.startswith("* "):
            new_contents.append(splitted_contents[i])
        else:
            new_contents[-1] += splitted_contents[i]

    return new_contents


def count_the_number_of_tabs(text):
    count = 0
    for character in text:
        if character == " ":
            count += 1
        else:
            break
    return count // 4


def post_a_new_workflow(slack_user_id, title, label):
    try:
        json_data = {}
        # now = datetime.datetime.now().strftime('%Y/%m/%d')

        notion_user_id = ""
        with open(f"{os.environ['ROOT_PATH']}/db/user_info.json", "r") as json_file:
            json_data = json.load(json_file)
            notion_user_id = json_data[slack_user_id]["notion_user_id"]

        if notion_user_id == "":
            return "등록되지 않은 사용자입니다. 신규 등록을 진행해주세요."

        response = notion.pages.create(
            parent={
                "type": "database_id",
                "database_id": os.environ["NOTION_DATABASE_ID"],
            },
            properties={
                "이름": {
                    "title": [
                        {
                            "annotations": {
                                "bold": False,
                                "code": False,
                                "color": "default",
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                            },
                            "href": None,
                            "plain_text": title,
                            "text": {"content": title, "link": None},
                            "type": "text",
                        }
                    ],
                    "type": "title",
                },
                "라벨": {"type": "multi_select", "multi_select": [{"name": label}]},
                "날짜": {
                    "date": {
                        "end": None,
                        "start": get_current_time(),
                        "time_zone": None,
                    }
                },
                "작성자": {
                    "people": [
                        {
                            "object": "user",
                            "id": notion_user_id,
                        }
                    ]
                },
            },
        )

        return response
    except APIResponseError as error:
        logging.error(f"API error: {error}")

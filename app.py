import copy
import datetime
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from notion_client import Client
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.INFO)

from core.const import (
    EVENT_APP_MENTION_BLOCKS,
    EVENT_APP_MENTION_TEXT,
    MSG_CREATING_NEW_WORKTASK_IN_NOTION,
    MSG_DELETING_SLACK_WORKTASK_MESSAGE,
    MSG_LOADING_WORKTASKS,
    MSG_NO_NEW_WORKTASKS_TODAY,
    MSG_NO_WORKTASKS_FOUND,
    MSG_REGISTERING_USER,
    MSG_SLACK_WORKTASK_MESSAGE_DELETED,
    MSG_USER_NOT_REGISTERED,
    MSG_WORKTASK_REGISTRATION_FAILED,
    MSG_WORKTASKS_SAVED_FROM_NOTION,
)
from utils import make_form
from utils.database import (
    append_blocks,
    enroll_users_id_to_notion,
    get_a_recent_workflow_content_from_cache,
    get_a_recent_workflow_content_from_notion,
    get_current_time,
    get_current_time_detail,
    get_user_information,
    get_username,
    get_users_notion_id,
    post_a_new_workflow,
    split_todos,
    string_to_list,
    update_a_cache_worktask_located_at_the_backend_server,
)
from utils.slack_modal import open_modal, update_modal

# Initializes your app with your bot token and signing secret
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
WORKTASK_CHANNEL_ID = os.environ["WORKTASK_CHANNEL_ID"]
ROOT_PATH = os.environ["ROOT_PATH"]

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)
notion = Client(auth=NOTION_TOKEN)


@app.command("/enroll")
def enroll_new_user(ack, body, client):
    ack()
    slack_user_id = body["user_id"]
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=MSG_REGISTERING_USER,
    )
    user_info = client.users_profile_get(user=slack_user_id)["profile"]

    user_email = user_info["email"]
    job_title = user_info["title"]
    real_user_name = user_info["real_name"]
    image_url = user_info["image_72"]

    response = enroll_users_id_to_notion(slack_user_id, real_user_name, user_email, job_title, image_url)
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=f"{response}",
    )


@app.command("/reset")
def get_recent_worktask(ack, body, client):
    ack()
    slack_user_id = body["user_id"]
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=MSG_LOADING_WORKTASKS,
    )

    with open(f"{ROOT_PATH}/db/cache_worktask.json", "r", encoding="utf-8") as f:
        cache_worktask = json.load(f)
        keys_cache_worktask = list(cache_worktask.keys())
        if slack_user_id not in keys_cache_worktask:
            client.chat_postEphemeral(
                channel=WORKTASK_CHANNEL_ID,
                user=slack_user_id,
                text=MSG_USER_NOT_REGISTERED,
            )
            return

    response = update_a_cache_worktask_located_at_the_backend_server(slack_user_id, {})
    if response != "Success":
        client.chat_postEphemeral(
            channel=WORKTASK_CHANNEL_ID,
            user=slack_user_id,
            text=MSG_NO_WORKTASKS_FOUND,
        )
        return

    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=MSG_WORKTASKS_SAVED_FROM_NOTION,
    )

    _, user_name, last_updated_date, title, label, page_id = get_a_recent_workflow_content_from_cache(slack_user_id)
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=f"작성자: {user_name}\n최근 작성일: {last_updated_date}\n제목: {title}\n라벨: {label}\n업데이트 시간: {get_current_time_detail()}",
    )


@app.command("/worktask")
def handle_worktask(ack, body, client):
    ack()
    result = open_modal(client, body["trigger_id"])

    slack_user_id = body["user_id"]
    worktask_dict, user_name, last_updated_date, title, label, page_id = get_a_recent_workflow_content_from_cache(
        slack_user_id
    )
    if worktask_dict == "None":
        client.chat_postEphemeral(
            channel=WORKTASK_CHANNEL_ID,
            user=slack_user_id,
            text=MSG_USER_NOT_REGISTERED,
        )
        return

    n_trigger_id = result["view"]["id"]
    n_trigger_hash = result["view"]["hash"]
    update_modal(
        client,
        n_trigger_id,
        n_trigger_hash,
        worktask_dict,
        user_name,
        last_updated_date,
        title,
        label,
    )


@app.command("/delete")
def delete_my_recent_message_on_the_slack_channel(ack, body, client):
    ack()
    slack_user_id = body["user_id"]

    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=MSG_DELETING_SLACK_WORKTASK_MESSAGE,
    )
    slack_user_name = get_user_information(slack_user_id)["slack_user_name"]

    result = client.conversations_history(channel=WORKTASK_CHANNEL_ID, limit=50)
    conversation_history = result["messages"]
    conversation_history.sort(key=lambda x: x["ts"], reverse=True)

    for conversation in conversation_history:
        conversation_keys = list(conversation.keys())
        if "subtype" in conversation_keys:
            conversation_type = conversation["subtype"]
        elif "type" in conversation_keys:
            conversation_type = conversation["type"]

        timestamp = conversation["ts"]
        dt_object = datetime.datetime.fromtimestamp(float(timestamp))
        dt_object = dt_object.strftime("%Y-%m-%d")

        currunt_time = get_current_time()

        if "user" in conversation_keys:
            user_name = conversation["user"]
        elif "username" in conversation_keys:
            user_name = conversation["username"]

        if conversation_type == "bot_message" and (user_name == slack_user_name or user_name == slack_user_id):
            if currunt_time != dt_object:
                client.chat_postEphemeral(
                    channel=WORKTASK_CHANNEL_ID,
                    user=slack_user_id,
                    text=MSG_NO_NEW_WORKTASKS_TODAY,
                )
                return
            client.chat_delete(channel=WORKTASK_CHANNEL_ID, ts=timestamp)
            client.chat_postEphemeral(
                channel=WORKTASK_CHANNEL_ID,
                user=slack_user_id,
                text=MSG_SLACK_WORKTASK_MESSAGE_DELETED,
            )
            return


@app.view("worktask_modal")
def handle_view_submission_events(ack, body, client, view):
    ack()
    slack_user_id = body["user"]["id"]
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=MSG_CREATING_NEW_WORKTASK_IN_NOTION,
    )
    _, _, page_updated_date, _, _, page_id = get_a_recent_workflow_content_from_cache(slack_user_id)
    state = view["state"]["values"]
    state_keys = list(state.keys())
    keys = []
    for key in state_keys:
        keys.append(state[key])

    for value in keys:
        first_key = next(iter(value))
        if first_key == "title":
            title = value[first_key]["value"]
        elif first_key == "label_static_select-action":
            label = value[first_key]["selected_option"]["text"]["text"]
        elif first_key == "todos_input":
            todos = value[first_key]["rich_text_value"]
        elif first_key == "doings_input":
            doings = value[first_key]["rich_text_value"]
        elif first_key == "dones_input":
            dones = value[first_key]["rich_text_value"]

    Todo_header = make_form.heading_1_header(content="To do")
    Doing_header = make_form.heading_1_header(content="Doing")
    Done_header = make_form.heading_1_header(content="Done")

    todos_elements = todos["elements"]
    todos_elements.insert(0, Todo_header)
    doings_elements = doings["elements"]
    doings_elements.insert(0, Doing_header)
    dones_elements = dones["elements"]
    dones_elements.insert(0, Done_header)

    content = {"elements": todos_elements + doings_elements + dones_elements}

    current_time = get_current_time()
    if page_updated_date == current_time:
        notion.pages.update(page_id=page_id, archived=True)

    resp = post_a_new_workflow(slack_user_id, title, label)
    success = append_blocks(content, resp["id"])
    username = get_username(slack_user_id)

    if success == "Success":
        updated_page_url = resp["url"]
        client.chat_postEphemeral(
            channel=WORKTASK_CHANNEL_ID,
            user=slack_user_id,
            text=f"{username}님의 워크태스크 등록이 끝났습니다.\nURL: {updated_page_url}\n\nwork-task 채널에 업데이트를 알립니다. 잠시만 기다려주세요.",
        )
        with open(f"{ROOT_PATH}/db/cache_worktask.json", "r", encoding="utf-8") as f:
            cache_worktask = json.load(f)

        notion_user_id = get_users_notion_id(slack_user_id)
        (
            aligned_last_updated_pages_content,
            enrolled_user_name,
            last_updated_date,
            title,
            label_before,
            page_id,
        ) = get_a_recent_workflow_content_from_notion(notion_user_id)

        new_contents = {
            "title": title,
            "label": label_before,
            "user_name": enrolled_user_name,
            "last_updated_date": last_updated_date,
            "content": aligned_last_updated_pages_content,
            "page_id": page_id,
        }

        cache_worktask[slack_user_id] = new_contents

        with open(f"{ROOT_PATH}/db/cache_worktask.json", "w", encoding="utf-8") as f:
            json.dump(cache_worktask, f, ensure_ascii=False, indent=4)

        post_block = copy.deepcopy(aligned_last_updated_pages_content)
        todos, doings, dones = split_todos(post_block)

        slack_todo_header = make_form.rich_text_section_header("To do")
        slack_doing_header = make_form.rich_text_section_header("Doing")
        slack_done_header = make_form.rich_text_section_header("Done")

        rb = []
        if label == "작업중":
            todos["elements"].insert(0, slack_todo_header)
            doings["elements"].insert(0, slack_doing_header)
            todos["elements"].extend(doings["elements"])
            rb = todos
        elif label == "완료":
            doings["elements"].insert(0, slack_doing_header)
            dones["elements"].insert(0, slack_done_header)
            doings["elements"].extend(dones["elements"])
            rb = doings
        else:
            todos["elements"].insert(0, slack_todo_header)
            doings["elements"].insert(0, slack_doing_header)
            dones["elements"].insert(0, slack_done_header)
            todos["elements"].extend(doings["elements"])
            todos["elements"].extend(dones["elements"])
            rb = todos

        client.chat_postMessage(
            channel=WORKTASK_CHANNEL_ID,
            username=username,
            icon_url=get_user_information(slack_user_id)["image_url"],
            blocks=[rb],
        )

    else:
        client.chat_postEphemeral(
            channel=WORKTASK_CHANNEL_ID,
            user=slack_user_id,
            text=MSG_WORKTASK_REGISTRATION_FAILED,
        )


@app.event("app_mention")
def message_hello(ack, body, client):
    ack()
    slack_user_id = body["event"]["user"]
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        text=EVENT_APP_MENTION_TEXT,
    )
    client.chat_postEphemeral(
        channel=WORKTASK_CHANNEL_ID,
        user=slack_user_id,
        blocks=EVENT_APP_MENTION_BLOCKS,
    )


if __name__ == "__main__":
    handler = SocketModeHandler(
        app,
        os.environ["SLACK_APP_TOKEN"],
    )
    handler.start()

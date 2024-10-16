# Function to create a modal
def open_modal(client, trigger_id):
    return client.views_open(
        trigger_id=trigger_id,
        view={
            "type": "modal", 
            "callback_id": "worktask_modal",
            "title": {
                "type": "plain_text",
                "text": "Today's Work Task", 
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*지난 워크태스크를 불러오고 있습니다. 잠시만 기다려주세요.*\n\n"
                    }
                },
            ],
        }
    )
def update_modal(client, trigger_id, trigger_hash, worktask_dict, enrolled_user_name, created_date, title, label):
    todos = worktask_dict['todos']
    doings = worktask_dict['doings']
    dones = worktask_dict['dones']
    client.views_update(
        view_id=trigger_id,
        hash=trigger_hash,
        view= {
            "type": "modal", 
            "callback_id": "worktask_modal",
            "title": {
                "type": "plain_text",
                "text": "Today's Work Task", 
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },

            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "안녕하세요! :smile: 오늘의 *워크태스크* 를 입력해주세요 ;)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"지난 등록 일자:  *{created_date}*  \n작성자: *{enrolled_user_name}*"
                    }
                },
                {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "현재 베타테스트 진행중입니다.\n 오류 및 개선사항은 이 곳에 남겨주세요 ^^\nhttps://www.notion.so/slackbot-issues-bd6ad371fbb84d5abde6c11a7e298560?pvs=4"
			}
		},
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title",
                        "initial_value": title
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Title"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*라벨*"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True
                        },
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": label,
                                "emoji": True
                            },
                            "value": f"value-{label}"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "작업중",
                                    "emoji": True
                                },
                                "value": "value-작업중"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "완료",
                                    "emoji": True
                                },
                                "value": "value-완료"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "휴가",
                                    "emoji": True
                                },
                                "value": "value-휴가"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "외부일정",
                                    "emoji": True
                                },
                                "value": "value-외부일정"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "자택",
                                    "emoji": True
                                },
                                "value": "value-자택"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "병가",
                                    "emoji": True
                                },
                                "value": "value-병가"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "대체",
                                    "emoji": True
                                },
                                "value": "value-대체"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "반차",
                                    "emoji": True
                                },
                                "value": "value-반차"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "반반차",
                                    "emoji": True
                                },
                                "value": "value-반반차"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "취소",
                                    "emoji": True
                                },
                                "value": "value-취소"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "이벤트",
                                    "emoji": True
                                },
                                "value": "value-이벤트"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "요청",
                                    "emoji": True
                                },
                                "value": "value-요청"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "확인",
                                    "emoji": True
                                },
                                "value": "value-확인"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "공휴일",
                                    "emoji": True
                                },
                                "value": "value-공휴일"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "건강검진",
                                    "emoji": True
                                },
                                "value": "value-건강검진"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "교육",
                                    "emoji": True
                                },
                                "value": "value-교육"
                            },
                        ],
                        "action_id": "label_static_select-action"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*주의사항* : 라벨이 '작업중'인 경우, 슬랙 work-task 채널에 Todo, Doing 섹션만 출력됩니다.\n라벨이 '완료'인 경우, 슬랙 work-task 채널에 Doing, Done 섹션만 출력됩니다."
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "rich_text_input",
                        "action_id": "todos_input",
                        "focus_on_load": True,
                        "initial_value": todos
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "TO DO",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "rich_text_input",
                        "action_id": "doings_input",
                        "initial_value": doings
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "DOING",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "element": {
                        "type": "rich_text_input",
                        "action_id": "dones_input",
                        "initial_value": dones
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "DONE",
                        "emoji": True
                    }
                },
            ]
        },
    )

    

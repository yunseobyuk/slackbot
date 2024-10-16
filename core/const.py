MSG_LOADING_WORKTASKS = (
    "사용자의 최근 워크태스크를 불러오고 있습니다. 잠시만 기다려주세요."
)
MSG_REGISTERING_USER = f"사용자 등록을 진행하고 있습니다. 잠시만 기다려주세요."
MSG_USER_NOT_REGISTERED = "미등록 사용자입니다. 사용자 등록을 진행해주세요."
MSG_NO_WORKTASKS_FOUND = "Notion database에 등록된 워크태스크 문서가 없습니다. 새로운 워크태스크를 등록해주세요."
MSG_WORKTASKS_SAVED_FROM_NOTION = "노션 데이터베이스로부터 최근 워크태스크를 불러와 저장했습니다. 인덱스는 다음과 같습니다."
MSG_DELETING_SLACK_WORKTASK_MESSAGE = "최근 Slack work-task 페이지에 작성하신 메시지를 삭제하고 있습니다. 잠시만 기다려주세요."
MSG_NO_NEW_WORKTASKS_TODAY = "오늘 새로 작성한 워크태스크가 없습니다."
MSG_SLACK_WORKTASK_MESSAGE_DELETED = (
    "최근 Slack work-task 페이지에 작성하신 메시지를 삭제했습니다."
)
MSG_CREATING_NEW_WORKTASK_IN_NOTION = (
    "노션 데이터베이스에 새로운 워크태스크 문서를 작성중입니다. 잠시 기다려주세요."
)
MSG_NOTIFYING_WORKTASK_CHANNEL_UPDATE = (
    "work-task 채널에 업데이트를 알립니다. 잠시만 기다려주세요."
)
MSG_WORKTASK_REGISTRATION_FAILED = "워크태스크 등록에 실패했습니다."

EVENT_APP_MENTION_TEXT = f"""지피다봇은 워크태스크 등록 및 관리를 위한 봇으로, 사용 전 사용자 등록이 필요합니다.\n
    사용자 등록은 `/enroll` 명령어, 워크태스크 작성은 `/worktask` 명령어, 최신화는 `/reset` 명령어로 진행합니다. /reset는 선택사항으로, enroll시 자동 수행됩니다.\n 
    만약 슬랙 워크태스크 채널에 업데이트된 오늘의 워크태스크를 삭제하려면, /delete 명령어를 사용하세요. 삭제 후 새로 워크태스크를 등록하면 슬랙과 노션에 워크태스크 업데이트가 진행됩니다.\n
    워크태스크 문서는 #으로 시작하text는 제목, 날짜 정보, 라벨, Todo/Doing/Done 블록 구조를 따라 작성해야 하며 비어있어서는 안됩니다. 인용구, 코드, 코드블록은 지원하지 않습니다.\n
    작성 예시는 다음과 같습니다.\n"""

EVENT_APP_MENTION_BLOCKS = [
    {
        "type": "rich_text",
        "elements": [
            {
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": "To do", "style": {"bold": True}}
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1: "},
                            {"type": "text", "text": "Say hello"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.1: "},
                            {"type": "text", "text": "こんにちは."},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.2: "},
                            {"type": "text", "text": "你好!"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.3: "},
                            {"type": "text", "text": "안녕하세요 :)"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 0,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 2: "},
                            {"type": "text", "text": "치키차카초코초"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": "\nDoing", "style": {"bold": True}}
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1: "},
                            {"type": "text", "text": "Say hello"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.1: "},
                            {"type": "text", "text": "こんにちは."},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.2: "},
                            {"type": "text", "text": "你好!"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 1,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 1.3: "},
                            {"type": "text", "text": "안녕하세요 :)"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 0,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": "item 2: "},
                            {"type": "text", "text": "치키차카초코초"},
                        ],
                    }
                ],
            },
            {
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": "\nDone", "style": {"bold": True}}
                ],
            },
            {
                "type": "rich_text_list",
                "style": "bullet",
                "indent": 0,
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {"type": "text", "text": " "},
                            {"type": "text", "text": "끝!"},
                        ],
                    }
                ],
            },
        ],
    }
]

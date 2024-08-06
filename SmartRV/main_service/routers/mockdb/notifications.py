notifications = [
    {
        "id": 1,
        "level": "CRITICAL",
        "header": "Super Important",
        "body": "Something is about to happen, if you do not ...",
        "footer": {
        "actions": ["dismiss", "navigate"],
        "action_dismiss": {
            "type": "dismiss",
            "action": {
            "text": "Dismiss"
            }
        },
        "action_navigate": {
            "type": "navigate",
            "action": {
            "icon": None,
            "text": "Update Now",
            "href": "/home/swupdates",
            "event_href": "/notifications/1/navigate"
            }
        }
        }
    },
    {
        "id": 2,
        "level": "WARNING",
        "header": "Gray Water Levels",
        "body": "Your gray water tank is approaching 3/4 full.",
        "footer": {
            "actions": ["dismiss"],
            "action_dismiss": {
                "type": "dismiss",
                "action": {
                "text": "OK",
                "event_href": "/notifications/2/dismiss"
                }
            }
        }
    }
]

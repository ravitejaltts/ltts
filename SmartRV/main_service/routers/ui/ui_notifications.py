from asyncio import base_futures
import datetime
import json
import os
from typing import Optional, List
from urllib import response

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel

from common_libs.models.lighting import *

# from .common import ResultLevel, not_implemented

# from main_service.modules.hardware.hal import hw_layer
from common_libs.models.common import KeyValue, RVEvents, EventValues
from main_service.modules.constants import (
    TEMP_UNITS,
    TEMP_UNIT_PREFERENCE_KEY,
    TEMP_UNIT_FAHRENHEIT,
    _celcius_2_fahrenheit
)

from common_libs.models.notifications import dismiss_note

# BASE_URL = 'http://192.168.12.220:8000'


BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

PREFIX = 'notifications'
router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['NOTIFICATIONS',]
)


@router.get('')
async def get_notifications(request: Request, http_response: Response) -> dict:
    '''Endpoint for notification retrieval.'''
    http_response.headers['cache-control'] = 'no-store'
    notifications = []
    # print('4 Note  lock wait')

    # Aquire the notification lock the list can change in other places
    with request.app.n_lock:
        try:
            notifications = sorted(request.app.notifications[:], key=lambda x:x['level'])
        except Exception as err:
            print('Get Top exception', err)
            raise

    # return {
    #     'notifications': notifications
    # }
    return notifications


@router.get('/{notification_id}/{action}')
async def track_notifications(request: Request, notification_id: int, action: str) -> dict:
    '''Endpoint to track notification events.'''
    # TODO: Make action a proper enum considered by docs
    if action not in ('dismiss', 'navigate', 'api_call'):
        raise HTTPException('Unknown action')
    # print('5 Note  lock wait')
    with request.app.n_lock:
        all_notifications = list(request.app.event_notifications.values())
        try:
            notification_ids = [x.notification_id for x in all_notifications]
        except Exception as err:
            print(err)
            print('Get Top exception')
            raise

    if notification_id not in notification_ids:
        return {'result': 'STALE_REQUEST'}

    if action == 'dismiss':
        print("Try to dismiss id", notification_id)
        dismiss_note(
            request.app,
            request.app.event_notifications[notification_id]
        )

    return {'result': 'OK'}


@router.put('/{notification_id}/{action}')
async def set_track_notifications(request: Request, notification_id: int, action: str) -> dict:
    '''Endpoint for actions for notifications.'''
    # TODO: Make action a proper enum considered by docs
    if action not in ('dismiss', 'navigate', 'api_call', 'clear_notification'):
        raise HTTPException('Unknown action')
    # print('5 Note  lock wait')
    with request.app.n_lock:
        all_notifications = list(request.app.event_notifications.values())
        try:
            notification_ids = [x.notification_id for x in all_notifications]
        except Exception as e:
            print('Get Top exception', e)

    if notification_id not in notification_ids:
        return {
            'result': 'STALE_REQUEST'
        }

    if action == 'dismiss':
        # print("Try to dismiss id",notification_id)
        dismiss_note(request.app, request.app.event_notifications[notification_id])

    elif action == 'clear_notification':
        try:
            request.app.event_notifications[notification_id].user_cleared = True
            request.app.user_db.update_notification(request.app.event_notifications[notification_id])
        except Exception as e:
            print('clear notifications exception', e)

    return {'result': 'OK'}


@router.get('/all')
async def get_all_notifications(request: Request):
    all_notifications = []
    try:
        all_notifications = list(request.app.event_notifications.values())
        all_notifications =  sorted(all_notifications[:], key=lambda x:x.priority)
    except Exception as e:
        print('Get all notifications exception', e)
    return all_notifications


# @router.get('/settings')
# async def get_notifications_settings(request: Request):

#     all_notifications = list(request.app.event_notifications.values())
#     notifications = []

#     for note in all_notifications:
#         # print(note)
#         note_id = note.notification_id
#         note_state = 0  # temp
#         # print('Note current State', note_state)

#         notification = {
#             'title': note_id.name,
#             'name': note_id.name,
#             'user_selected': note.user_selected,
#             'user_cleared': note.user_cleared,
#             'trigger_type': note.trigger_type.name,
#             'trigger_value': note.trigger_value,
#         }
#         if note_id == RVEvents.REFRIGERATOR_OUT_OF_RANGE:
#             # check the units for the range
#             current_temp_unit = request.app.config.get(
#                     'climate', {}
#                 ).get(
#                     'TempUnitPreference',
#                     TEMP_UNIT_FAHRENHEIT
#             )

#         notifications.append(notification)

#     return notifications


@router.get('/center')
async def get_all_notifications(request: Request):
    '''Retrieve all notifications/ alerts that are active or have not been dismissed.'''
    all_notifications = list(request.app.event_notifications.values())
    status_alerts = []
    status_general = []
    for note in all_notifications:
        print("NOTE ACTIVE /center ", note.active)
        if bool(note.active) is True:
            print("NOTE ACTIVE /center note ", note)
        note_id = note.notification_id
        note_state = 0  # temp

        notification = {
            'header': note.header,
            'ts_active': note.ts_active,    # this is timestamp
            'priority': note.priority,
            'message': note.msg,
            'active': note.active,
            'user_cleared': note.user_cleared,  # need this for later logic
            'actions': {
                'clear_notification': {
                    'type': 'api_call',
                    'action': {
                        'href': f'/ui/notifications/{note_id}/clear_notification',
                        'type': 'PUT',
                    }
                },
            }
        }
        if bool(notification['active']) is True:
            status_alerts.append(notification)
        elif notification['active'] is False and notification['user_cleared'] is False:
            # NOTE: There is no way to use current notifications if ts_active is cleared
            if notification['ts_active'] == 0.0:
                continue
            status_general.append(notification)

    status_alerts_sorted = sorted(status_alerts, key=lambda x: x['priority'], reverse=True)
    status_general_sorted = sorted(status_general, key=lambda x: x['active'], reverse=True)

    response = {
        'title': 'Notifications',
        'type': 'SECTIONS_LIST',
        'data': [
            {
                'title': 'Status Alerts',
                'type': 'SECTIONS_LIST_ITEM',
                'data': status_alerts_sorted,
            },
            {
                'title': 'GENERAL',
                'type': 'SECTIONS_LIST_ITEM',
                'data': status_general_sorted,
            },
            {
                'subtext': 'Clear all',
                'actions': {
                    'CLEAR_ALL': {
                        'type': 'api_call',
                        'action': {
                            'href': '/ui/notifications/clearall',
                            'type': 'PUT',
                        }
                    }
                }
            }
        ]
    }

    return response


@router.put('/clearall')
async def set_clear_all(request: Request):
    '''Clear all notifications.'''

    all_notifications = list(request.app.event_notifications.values())
    # user_clear_value = 1
    try:
        for note in all_notifications:
            note.user_cleared = True
            request.app.user_db.update_notification(note)
    except Exception as e:
        print('clear-all exception', e)
    return 'Notifications Updated'

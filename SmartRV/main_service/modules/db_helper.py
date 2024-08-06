'''WGO Database Module.

Database module to write to the non-volatile storage for user config,
log events and query for retrieval.

'''

# TODO: Check for tables on boot and create if needed
#   If creation is needed this is a log event itself that should be noted
# TODO: Create callback mechanism to provide the caller infor on success or failure of each operation
# TODO: Make sure that write succeds, is retried but will nto break the system when it ultimately fails
# TODO: Develop strategy to recover from disaster (DB cannot be recovered) but device needs to boot
#   - Report data loss
# TODO: Discuss the concept of an in-memory database with size constraints and a regular check

# TODO: Test the following scenarios
# - DB cannot write to storage
# - Write fails due to schema

import os
from datetime import datetime
from main_service.modules.constants import _celcius_2_fahrenheit
from common_libs.models.common import RVEvents, convert_utc_to_local
from threading import Lock
import json
import sqlite3
import time
from common_libs import environment
_env = environment()

EVENT_SQL = '''
    INSERT INTO coach_events (
        timestamp,
        event,
        instance,
        valueType,
        value,
        meta
    ) VALUES (
        ?,
        ?,
        ?,
        ?,
        ?,
        ?)
'''

NOTIFICATION_SQL = '''
    INSERT INTO notifications (
        notification_id,
        instance,
        ts_active,
        ts_dismissed,
        ts_cleared,
        priority,
        code,
        active,
        user_selected,
        user_cleared,
        mobile_push,
        trigger_events,
        trigger_type,
        trigger_value,
        header,
        msg,
        type,
        meta
        ) VALUES (
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?)
'''

# 'UPDATE config SET value = ? WHERE key = ?'

UPDATE_NOTIFICATION_SQL = \
    '''
    UPDATE notifications
    SET instance = ?,
        ts_active = ?,
        ts_dismissed = ?,
        ts_cleared = ?,
        priority = ?,
        code = ?,
        active = ?,
        user_selected = ?,
        user_cleared = ?,
        mobile_push = ?,
        trigger_events = ?,
        trigger_type = ?,
        trigger_value = ?,
        header = ?,
        msg = ?,
        type = ?,
        meta = ?
    WHERE notification_id = ?
'''

UPDATE_NOTIFICATION_TRIGGER_VALUE_SQL = \
    '''
    UPDATE notifications
    SET trigger_value = ?
    WHERE notification_id = ?
'''

SELECT_MANY = '''
    SELECT * FROM coach_events ORDER BY timestamp LIMIT ? OFFSET ?
'''

DUMP_ALL_EVENTS = '''
    SELECT * FROM coach_events
'''
# DUPLICATE ?? See below
# GET_EVENTS = '''
#     SELECT * FROM coach_events WHERE timestamp >= ? AND timestamp <= ?
# '''

DELETE_EVENTSTABLE_SQL = '''
    DROP TABLE coach_events
    '''
DELETE_NOTIFICATIONSTABLE_SQL = '''
    DROP TABLE notifications
'''

DELETE_CONFIG_TABLE_SQL = '''
    DROP TABLE config
'''

EMPTY_CONFIG_TABLE = '''
    DELETE from config
'''

DELETE_SQLLITE_SEQUENCE_SQL = '''
    DROP TABLE sqlite_sequence
'''
DUMP_ALL_NOTIFICATIONS = '''
    SELECT * FROM notifications
'''

COUNT_EVENTS = '''
    SELECT COUNT() FROM coach_events
'''

COUNT_NOTIFICATIONS = '''
    SELECT COUNT() FROM notifications
'''

GET_EVENTS = '''SELECT * FROM coach_events WHERE timestamp BETWEEN ? AND ?'''

DROP_EVENTS_OLDER_THAN = '''DELETE FROM coach_events WHERE timestamp < ?'''

GET_NOTIFICATIONS = '''SELECT * FROM notifications WHERE notification_id = ?'''

GET_COACH_EVENTS = '''SELECT * FROM coach_events ORDER BY timestamp DESC, value DESC LIMIT 1'''

SELECT_RANKED_EVENTS = '''WITH RankedRecords AS ( \
  SELECT event, value, instance, ROW_NUMBER() OVER (PARTITION BY event ORDER BY timestamp DESC) AS rn FROM coach_events ) \
  SELECT * FROM RankedRecords WHERE rn = 1'''


class DBHandler(object):
    is_initialized = False

    def connect_to_db(self, config):
        try:
            self.config = config
            self.db = sqlite3.connect(config.get(
                'path'), check_same_thread=False)

            self.init_tables()
            # Lock individual tables as speed increase effort
            self.db_coach_events_lock = Lock()
            self.db_notifications_lock = Lock()
            # TODO: Verify config does not need a lock
            self.db_lock = Lock()
            self.is_initialized = True
        except Exception as err:
            print('DB error: ', err, " Retry")
            os.remove(config.get('path'))


    def __init__(self, config):
        cnt = 0
        while self.is_initialized is False and cnt < 3:
            cnt += 1
            self.connect_to_db(config=config)
        if cnt >= 3:
            print('DB error - TOO Many retries we need Big Alert')

    def init_tables(self):
        cur = self.db.cursor()
        # TODO: Perform proper checks for tables and schemas
        created = False
        try:
            cur.execute('''CREATE TABLE coach_events(
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp,
                event,
                instance,
                valueType,
                value,
                meta
            );''')
            created = True
        except sqlite3.OperationalError as err:
            print('Cannot open DB', err)

        # try:  # Drop the Notifications to recreate.
        #     cur.execute(DELETE_NOTIFICATIONSTABLE_SQL)
        #     created = True
        # except sqlite3.OperationalError as err:
        #     print('Notifications table - ok to not be found: ', err)

        try:
            cur.execute('''CREATE TABLE notifications(
                notification_id INTEGER PRIMARY KEY,
                instance NOT NULL,
                ts_active,
                ts_dismissed,
                ts_cleared,
                priority,
                code,
                active,
                user_selected,
                user_cleared,
                mobile_push,
                trigger_events,
                trigger_type,
                trigger_value,
                header,
                msg,
                type,
                meta
            ) WITHOUT ROWID;''')
            created = True
        except sqlite3.OperationalError as err:
            print(err)

        try:
            cur.execute('CREATE TABLE config(key, value)')
            created = True
        except sqlite3.OperationalError as err:
            print('Note ERR Cannot create', err)

        if created is True:
            self.db.commit()
        else:
            self.check_note_table()

    def check_note_table(self):
        '''Check if we need the new field in Notifications'''
        cur = self.db.cursor()
        cur.execute(f"PRAGMA table_info({'notifications'})")
        table_info = cur.fetchall()
        type_exists = any(field[1] == 'type' for field in table_info)
        if type_exists is False:
            cur.execute(
                f"ALTER TABLE {'notifications'} ADD COLUMN {'type'} INTEGER DEFAULT 0")
            self.db.commit()
            print('Adding type field to notifications')
        meta_exists = any(field[1] == 'meta' for field in table_info)
        if meta_exists is False:
            cur.execute(
                f"ALTER TABLE {'notifications'} ADD COLUMN {'meta'} TEXT DEFAULT ''")
            self.db.commit()
            print('Adding meta field to notifications')

    def get_config(self, key: str):
        '''Get a specific config item from DB.'''
        cur = self.db.cursor()
        cur.execute('SELECT value from config WHERE key=?', (key,))
        config_value = cur.fetchone()
        # print('Config in db', config_value)
        if config_value is None:
            return None
        else:
            try:
                return json.loads(config_value[0])
            except TypeError as err:
                print(err)
                # TODO: Handle all known json failures
                # Create a system event and potentially notification
                raise

    def set_config(self, key: str, value: dict):
        '''Set a specific config item in the DB.'''
        # TODO: Handle failures to load because of schema migrations
        # Such
        previous_value = self.get_config(key)
        json_value = json.dumps(value)
        # print('Previous value for', key, previous_value)
        if previous_value == json_value:
            # Nothing to do, value is the same
            return previous_value

        cur = self.db.cursor()
        # print('10  DB  lock wait')
        # TODO: Verify that config table does not need a lock
        with self.db_lock:
            try:
                # print('10  DB  lock acquire')
                if previous_value is None:
                    cur.execute(
                        'INSERT INTO config (key, value) VALUES (?, ?)', (key, json_value))
                else:
                    cur.execute(
                        'UPDATE config SET value = ? WHERE key = ?', (json_value, key))

                self.db.commit()
            except Exception as err:
                print('Set Config exception', err)

        return self.get_config(key)

    def add_event(self, event):
        '''Add a log event to the database.'''
        # TODO: Fix this type check and put in the right place
        try:
            value = event.value.value
            value_type = 1       # ENUM
        except AttributeError:
            value = event.value
            value_type = 2       # Anything else
            # TODO: Create proper enum for stuff

        if value_type == 1 and type(value) is not int:
            # TODO: Why do we need this ?
            raise ValueError("Event Value Error - not INT")

        cur = self.db.cursor()

        data = [
            event.timestamp,
            event.event.value,
            event.instance,
            value_type,
            value,
            json.dumps(event.meta)
        ]
        # print('11  DB  lock wait')
        commit = False
        with self.db_coach_events_lock:
            try:
                result = cur.execute(EVENT_SQL, tuple(data))
                commit = self.db.commit()
            except OverflowError as err:
                print(
                    '[ERROR][DB][EVENT]',
                    err,
                    'Cannot convert value to int, need to force string',
                    value
                )
                data[4] = str(data[4])
                result = cur.execute(EVENT_SQL, tuple(data))
                commit = self.db.commit()
            except Exception as err:
                print('[ERROR][DB][EVENT] Non Overflow Add Event exception', data, err)
                result = None
            # TODO: Find the proper exception and why it occurs and handle that

        return result, commit

    def dump_all(self):
        '''Get all events in the database.'''
        cur = self.db.cursor()
        # print('2  DB  lock wait')

        with self.db_coach_events_lock:
            try:
                # print('2  DB  lock aquired')
                all_event = cur.execute(DUMP_ALL_EVENTS)
            except Exception as err:
                print('Dump All exception', err)

        return all_event

    def dump_all_notifications(self):
        '''Get the list of notifications from the database.'''
        cur = self.db.cursor()

        with self.db_notifications_lock:
            try:
                all_note = cur.execute(DUMP_ALL_NOTIFICATIONS)
            except Exception as e:
                print('Dump all notes exception', e)

        return all_note

    def event_count(self):
        '''Get event count in database.'''
        cur = self.db.cursor()
        self.db_coach_events_lock.acquire()
        try:
            n_estimate = cur.execute(COUNT_EVENTS).fetchone()[0]
        except Exception as e:
            print('Event Count exception', e)
        self.db_coach_events_lock.release()
        return n_estimate

    def notification_count(self):
        '''Get notification count.'''
        cur = self.db.cursor()
        # NOTE: Which way is better, seem with would be best ?
        with self.db_notifications_lock:
            try:
                n_estimate = cur.execute(COUNT_NOTIFICATIONS).fetchone()[0]
            except Exception as e:
                print('Notification count exception!', e)
        return n_estimate

    def fetch_many(self, count, offset=0):
        '''Fetch many results.'''
        cur = self.db.cursor()
        data = (count, offset)
        with self.db_coach_events_lock:
            try:
                cur.execute(SELECT_MANY, data)
            except Exception as e:
                print('Fetch Many exception!', e)
        return cur

    def get_events(self, start_ts: float = 0, end_ts: float = 0):
        '''Get all events in the database.'''
        cur = self.db.cursor()

        self.db_coach_events_lock.acquire()
        try:
            if (start_ts == 0) and (end_ts == 0):
                cur.execute(DUMP_ALL_EVENTS)
            else:
                if (end_ts == 0):
                    end_ts = time.time()
                data = (start_ts, end_ts,)
                cur.execute(GET_EVENTS, data)
        except:
            print('Get Events exception!')
        self.db_coach_events_lock.release()
        return cur

    def drop_events(self, newest_ts: float = 0):
        '''Drop older than x events in the database.'''
        cur = self.db.cursor()

        self.db_coach_events_lock.acquire()
        try:
                data = (newest_ts, )
                cur.execute(DROP_EVENTS_OLDER_THAN, data)
                print(f'Drop Events older than: {newest_ts}')
        except Exception as e:
            print(f'Drop Events exception! {e}')
        self.db_coach_events_lock.release()
        return cur

    def get_coach_events(self, event_id: int = None):
        '''Get one event - latest or if none get latest of each event id'''
        if event_id is None:
            cur = self.db.cursor()
            with self.db_coach_events_lock:
                cur.execute(SELECT_RANKED_EVENTS)
            return cur

    def add_notification(self, notification):
        '''Add a notification to the database.'''
        cur = self.db.cursor()

        # TODO: Fix this type check and put in the right place
        try:
            value = json.dumps(notification.trigger_value.value)
        except AttributeError as err:
            value = json.dumps(notification.trigger_value)

        try:
            ntype = notification.type
        except:
            ntype = 0

        triggers = json.dumps(notification.trigger_events)
        meta = json.dumps(notification.meta)

        data = (
            notification.notification_id,
            notification.instance,
            notification.ts_active,
            notification.ts_dismissed,
            notification.ts_cleared,
            notification.priority,
            notification.code,
            notification.active,
            notification.user_selected,
            notification.user_cleared,
            notification.mobile_push,
            triggers,
            notification.trigger_type,
            value,
            notification.header,
            notification.msg,
            ntype,
            meta
        )
        # print("Adding noteification", data)

        with self.db_notifications_lock:
            try:
                result = cur.execute(NOTIFICATION_SQL, data)
                commit = self.db.commit()
            except sqlite3.IntegrityError as err:
                if err.args == ('UNIQUE constraint failed: notifications.notification_id',):
                    # This case is hit when we are loading - we don't need the duplicates.
                    result = "OK"
                    commit = "NA"
                else:
                    raise

                # If this was not in the initialization then we would use update
                # But it proabably is failing when we check for any new 'default' notes to add
                # so we don't have to delete and recreate the table each time
                # and we don't overwrtie something the user may have changed
        return result, commit

    def get_notification(self, notification_id):
        data = (notification_id,)
        cur = self.db.cursor()
        n_dict = None
        with self.db_notifications_lock:
            try:
                #print(UPDATE_NOTIFICATION_SQL, data)
                result = cur.execute(GET_NOTIFICATIONS, data)
            except Exception as err:
                print('GET Notification exception!', err)
                return None
        try:
            n_dict = cur.fetchone()
        except Exception as err:
            print('GET Notification exception! 2', err)

        return n_dict

    def update_notification(self, notification):
        cur = self.db.cursor()
        try:
            value = json.dumps(notification.trigger_value.value)
        except AttributeError as err:
            value = json.dumps(notification.trigger_value)
            #print(f"[update_notification] found: {err} SO we will json dump it!")
        try:

            triggers = json.dumps(notification.trigger_events)
            print(f"[update_notification] meta: {notification.meta}")
            meta = json.dumps(notification.meta)

            data = (
                notification.instance,
                notification.ts_active,
                notification.ts_dismissed,
                notification.ts_cleared,
                notification.priority,
                notification.code,
                notification.active,
                notification.user_selected,
                notification.user_cleared,
                notification.mobile_push,
                triggers,
                notification.trigger_type,
                value,
                notification.header,
                notification.msg,
                notification.type,
                meta,
                notification.notification_id
            )
        except Exception as err:
            print(f"[update_notification] 2 error: {err}")
        #print('8  DB  lock wait')
        with self.db_notifications_lock:
            try:
                #print(UPDATE_NOTIFICATION_SQL, data)
                result = cur.execute(UPDATE_NOTIFICATION_SQL, data)
                commit = self.db.commit()
            except Exception as err:
                print(f'[Update Notification] exception! {meta}', err)

    def update_notification_trigger_value(self, _notification):
        cur = self.db.cursor()
        data = (
            json.dumps(_notification.trigger_value),
            _notification.notification_id,
        )
        #print('8  DB  lock wait')
        with self.db_notifications_lock:
            try:
                #print(UPDATE_NOTIFICATION_TRIGGER_VALUE_SQL, data)
                result = cur.execute(
                    UPDATE_NOTIFICATION_TRIGGER_VALUE_SQL, data)
                commit = self.db.commit()
            except Exception as err:
                print('Update Notification trigger exception!', err)

    def delete_database(self):
        '''Delete the database entries.'''
        cur = self.db.cursor()
        with self.db_coach_events_lock:
            with self.db_notifications_lock:
                with self.db_lock:
                    try:
                        # drop all four tables
                        cur.execute(DELETE_NOTIFICATIONSTABLE_SQL)
                        cur.execute(DELETE_CONFIG_TABLE_SQL)
                        cur.execute(DELETE_EVENTSTABLE_SQL)
                        # cur.execute(DELETE_SQLLITE_SEQUENCE_SQL)
                        self.db.commit()
                        #self.db.close()
                        #self.db= sqlite3.connect(self.config.get(
                        #                'path'), check_same_thread=False)
                        self.init_tables()
                        print('Recreated DB tables')
                    except Exception as err:
                        print(err, 'db close error')

    def reset_config_table(self):
        '''Remove all entries from config table so it has to initialize.'''
        cur = self.db.cursor()
        with self.db_lock:
            cur.execute(EMPTY_CONFIG_TABLE)

        return {}



# query needed by refrigerator

    def get_coach_event_refrigerator_freezer_query(self, start_timestamp, end_timestamp, instance):

        temp_change_event = RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE.value
        if instance not in [1, 2]:
             raise ValueError("Invalid instance")
        if instance == 1:
            out_of_range_event = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
            return f"SELECT * FROM coach_events WHERE instance = {instance} AND (event = {temp_change_event} OR event = {out_of_range_event}) AND timestamp between {start_timestamp} AND {end_timestamp} ORDER BY timestamp DESC"
        else:
            out_of_range_event = RVEvents.FREEZER_OUT_OF_RANGE.value
            return f"SELECT * FROM coach_events WHERE instance = {instance} AND (event = {temp_change_event} OR event = {out_of_range_event}) AND timestamp between {start_timestamp} AND {end_timestamp} ORDER BY timestamp DESC"

    # pass the user selection
    def execute_refrigerator_freezer_query(self, sql, onlyActive=False, current_temp_short="F", timezone="America/Chicago"):
        data_list = []
        cur = self.db.cursor()
        event_row = cur.execute(sql)

        last_event = ()
        event_count = 0
        for row in event_row:
            if event_count == 0:
                last_event = row
            event_count += 1
            d = dict()
            d['event'] = RVEvents(row[2])
            try:
                val = float(row[5])
                if current_temp_short == 'F':
                    d['value'] = f"{round(_celcius_2_fahrenheit(val, 1))}° {current_temp_short}"
                else:
                    d['value'] = f"{round(val)}° {current_temp_short}"
            except ValueError:
                d['value'] = '--'
                raise ValueError('Invalid temperature value')

            d['text'] = str(d['value'])
            d['time'] = convert_utc_to_local(row[1], timezone).strftime('%I:%M %p')
            d['timestamp'] = row[1]
            meta = json.loads(row[6])
            if (meta is not None and type(meta) is dict and meta.get('active') == True):
                d['alert'] = True
            else:
                d['alert'] = False

            if onlyActive:
                if d['alert'] == True:
                    data_list.append(d)
            else:
                data_list.append(d)
        return data_list, last_event


if __name__ == '__main__':

   # Test DB load

    db_config = {
        'path': _env.storage_file_path('wgo_user.db')
    }

    try:
        user_db = DBHandler(db_config)
    except sqlite3.OperationalError:
        # Fallback for local non linux testing (or whereever else there is not such path)
        user_db = DBHandler({'path': './wgo_user.db'})

    print("Check Notifications", user_db.notification_count())

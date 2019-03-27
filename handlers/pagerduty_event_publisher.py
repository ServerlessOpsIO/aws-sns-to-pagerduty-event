'''Publish message from SNS to Slack'''

import json
import logging
import os

import pypd

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

PD_INT_KEY = os.environ.get('PD_INT_KEY')
PD_SEVERITY = os.environ.get('PD_SEVERITY')
PD_SOURCE = os.environ.get('PD_SOURCE')


def _get_message_from_event(event: dict) -> str:
    '''Get the message from the event'''
    return event.get('Records')[0].get('Sns').get('Message')


def _publish_event_to_pagerduty(msg: str,
                                integration_key: str = PD_INT_KEY,
                                severity: str = PD_SEVERITY,
                                source: str = PD_SOURCE) -> dict:
    '''Publish a message to the PagerDuty API'''
    r = pypd.EventV2.create(
        data={
            'routing_key': integration_key,
            'event_action': 'trigger',
            'payload': {
                'summary': msg,
                'severity': severity,
                'source': source,
            }
        }
    )
    return r


def handler(event, context):
    '''Function entry'''
    _logger.debug('Event received: {}'.format(json.dumps(event)))

    msg = _get_message_from_event(event)

    pagerduty_response = _publish_event_to_pagerduty(msg)

    resp = {
        'pagerduty_response': pagerduty_response,
        'status': 'OK'
    }

    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp


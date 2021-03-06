'''Publish message from SNS to Slack'''

import json
import logging
import os
import sys

import pypd
from pypd.errors import Error as PdError
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_exponential

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

PD_INT_KEY = os.environ.get('PD_INT_KEY')
PD_SEVERITY = os.environ.get('PD_SEVERITY')
PD_SOURCE = os.environ.get('PD_SOURCE')


class HandlerBaseError(Exception):
    '''Base error class'''


class PagerDutyBaseError(HandlerBaseError):
    '''Base PagerDuty Error'''


class PagerDutyApiError(PagerDutyBaseError):
    '''PagerDuty Communication Error'''


class PagerDutyApiRetryableError(PagerDutyBaseError):
    '''PagerDuty Communication Error (Retryable)'''


class PagerDutyDataSeverityTypeError(PagerDutyBaseError):
    '''PagerDuty Severity Not Valid Type Error'''


class PagerDutyDataEventValidationError(PagerDutyBaseError):
    '''PagerDuty Event Data Validation Error'''


PD_ALLOWED_SEVERITIES = pypd.EventV2.SEVERITY_TYPES
if PD_SEVERITY not in PD_ALLOWED_SEVERITIES:
    raise PagerDutyDataSeverityTypeError(
        'Event source "{}" not in "{}"'.format(PD_SEVERITY, PD_ALLOWED_SEVERITIES)
    )


def _get_message_from_event(event: dict) -> str:
    '''Get the message from the event'''
    return event.get('Records')[0].get('Sns').get('Message')

@retry(wait=wait_exponential(),
       stop=stop_after_delay(20),
       retry=retry_if_exception_type(PagerDutyApiRetryableError),
       reraise=True)
def _publish_event_to_pagerduty(msg: str,
                                integration_key: str = PD_INT_KEY,
                                severity: str = PD_SEVERITY,
                                source: str = PD_SOURCE) -> dict:
    '''Publish a message to the PagerDuty API'''
    try:
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
    except PdError as e:
        tb = sys.exc_info()[2]
        if hasattr(e, 'code'):
            if e.code == 400 or e.code >= 500:
                raise PagerDutyApiRetryableError(e).with_traceback(tb)

        raise PagerDutyApiError(e).with_traceback(tb)

    except AssertionError as e:
        tb = sys.exc_info()[2]
        raise PagerDutyDataEventValidationError(e).with_traceback(tb)

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


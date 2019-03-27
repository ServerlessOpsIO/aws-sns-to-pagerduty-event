# aws-sns-to-pagerduty-event
[![Serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![Build Status](https://travis-ci.org/ServerlessOpsIO/aws-sns-to-pagerduty-event.svg?branch=master)](https://travis-ci.org/ServerlessOpsIO/aws-sns-to-pagerduty-event)

Publish a message received from SNS to PagerDuty as an event.

This service provides an SNS topic with a Lambda function as a subscriber. A message published to this topic will be published to the PagerDuty Events API.

## Service Interface

* Event Type: AWS SNS
* SNS Message: The value of the SNS Message attribute will be passed directly to PagerDuty as formatted in the SNS message.

## Configuration

The following Parameters are available.

* __PagerDutyIntegrationKey__: Integration key for the PagerDuty integration the event will be routed to.
* __PagerDutySeverity__ (optional): Set the severity of the event. A default is provided.
* __PagerDutySource__ (optional): Set the name of the source as show in PagerDuty. A default is provided.


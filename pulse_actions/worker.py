import json
import logging
import os

from pulse_actions.handlers import config

from mozillapulse.config import PulseConfiguration
from mozillapulse.consumers import GenericConsumer

logging.basicConfig(format='%(levelname)s:\t %(message)s')
LOG = logging.getLogger()


class PulseConsumer(GenericConsumer):
    """
    Creates a consumer object for the given exchange.

    Documentation for the exchanges:
    https://wiki.mozilla.org/Auto-tools/Projects/Pulse/Exchanges
    """

    def __init__(self, exchange, **kwargs):
        super(PulseConsumer, self).__init__(
            PulseConfiguration(**kwargs), exchange, **kwargs)


def run_pulse(exchange, topic, event_handler, dry_run=True):
    """
    Listen to a pulse exchange in a infinite loop.

    Call event_handler on every message.
    """

    label = 'pulse_actions'
    user = os.environ.get('PULSE_USER')
    password = os.environ.get('PULSE_PW')
    pulse_args = {
        'applabel': label,
        'topic': topic,
        'durable': True,
        'user': user,
        'password': password
    }

    # Pulse consumer's callback passes only data and message arguments
    # to the function, we need to pass dry-run
    def handler_with_dry_run(data, message):
        return event_handler(data, message, dry_run)

    pulse = PulseConsumer(exchange,
                          callback=handler_with_dry_run,
                          **pulse_args)
    LOG.info('Listening on %s, with topic %s', exchange, topic)

    while True:
        pulse.listen()


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'run_time_config.json')
    with open(config_path, 'r') as config_file:
        options = json.load(config_file)

    LOG.setLevel(logging.INFO)
    # requests is too noisy
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Finding the right event handler for the given exchange and topic
    topic_base = options['topic'].split('.')[0]
    try:
        handler_data = config.HANDLERS_BY_EXCHANGE[options['exchange']]
        handler_function = handler_data["topic"][topic_base]
    except KeyError:
        LOG.error("We don't have an event handler for %s with topic %s.",
                  options['exchange'], options['topic'])
        exit(1)

    run_pulse(
        exchange=options['exchange'],
        topic=options['topic'],
        event_handler=handler_function,
        dry_run=True)


if __name__ == '__main__':
    main()

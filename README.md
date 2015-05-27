# Pulse Actions

This project is Pulse listener that listens to Treeherder's job cancellation and retrigger actions in 'exchange/treeherder/v1/job-actions' and acts upon them.

### What it does

worker.py listens to exchange/treeherder/v1/job-actions in an infinite loop. It calls make_retrigger_request when it sees a retrigger action and make_cancel_request when it sees a cancel action. Currently everything is run with dry_run=True, so instead of doing requests the script just logs the requests it would have made.

### Current status:

- worker.py reads exchange and topic from run_time_config.json. It then uses HANDLERS_BY_EXCHANGE, a dictionary defined in config.py to decide what function it will use to handle incoming messages.

- Only buildbot topics (e.g. buildbot.#.# or buildbot.try.retrigger) in exchange/treeherder/v1/job-actions are supported for now.

- The functions to deal with TH's job-actions are defined in the module treeherderactions.py


See [bug 1168148](https://bugzilla.mozilla.org/show_bug.cgi?id=1168148) for more details.

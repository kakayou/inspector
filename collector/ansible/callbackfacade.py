from ansible.plugins.callback import CallbackBase
import traceback
import logging

logger = logging.getLogger('run')


class CallBackFacade(CallbackBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []

    def v2_runner_on_unreachable(self, result):
        logger.error('unreachable %s -> %s' % (result._host.get_name(), result._result['msg']))

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.results.append(result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        logger.error('failed %s -> %s : %s' % (result._host.get_name(), result.task_name, result._result['msg']))

    def v2_runner_on_skipped(self, result):
        logger.warning('skipped %s ' % result._host.get_name())
        self.results.append(result)

    def v2_playbook_on_play_start(self, play):
        self.playbook_on_play_start(play.name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        logger.info('task start: %s ' % task.name)
        self.playbook_on_task_start(task.name, is_conditional)

    def v2_playbook_on_stats(self, stats):
        try:
            for result in self.results:
                if 'exception' in result._result:
                    alert_line = result._result['exception']
                    logger.error('%s -> %s' % (result._host, alert_line))

                if result._task_fields['ignore_errors']:
                    continue

                if 'stderr_lines' in result._result:
                    rc = result._result['rc']
                    if rc != 0:
                        logger.error('%s -> %s' % (result._host, result._result['stdout']))
                else:
                    pass
        except Exception as e:
            logger.error('os call back error: %s' % traceback.format_exc())

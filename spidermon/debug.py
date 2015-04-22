import jinja2
from terminaltables import AsciiTable

MONITOR_REPORT = """
====================================================
MONITOR: {{ monitor.name }}
====================================================
_____________________ rules ________________________

{% if monitor.rules_manager.definitions %}
{{ rules_table.table }}
TOTAL: {{ monitor.rules_manager.definitions|length }}
{% else %}
No rules defined
{% endif %}

====================================================

____________________ actions _______________________

{% if monitor.actions_manager.definitions %}
{{ actions_table.table }}
TOTAL: {{ monitor.actions_manager.definitions|length }}
{% else %}
No actions defined
{% endif %}

"""

MONITOR_RESULT_REPORT = """
====================================================
MONITOR REPORT: {{result.monitor.name}}
====================================================
_____________________ checks _______________________

{% if result.checks %}
{{ checks_table.table }}
 TOTAL: {{ result.n_checks }}
PASSED: {{ result.n_passed_checks }}
FAILED: {{ result.n_failed_checks }}
ERRORS: {{ result.n_error_checks }}
    {% if result.n_error_checks %}

_________________ check errors _____________________

        {% for check in result.error_checks %}
RULE: {{ check.definition.name }}
TYPE: {{ check.definition.type }}
ERROR: {{ check.error_message }}
TRACEBACK: {{ check.error_traceback }}
        {% endfor %}
    {% endif %}
{% else %}
No rules defined
{% endif %}

____________________ actions _______________________

{% if result.actions %}
{{ actions_table.table }}
    TOTAL: {{ result.n_actions }}
PROCESSED: {{ result.n_processed_actions }}
  SKIPPED: {{ result.n_skipped_actions }}
   ERRORS: {{ result.n_error_actions }}
    {% if result.n_error_actions %}

_________________ action errors ____________________

        {% for action in result.error_actions %}
ACTION: {{ action.definition.name }}
ERROR: {{ action.error_message }}
TRACEBACK: {{ action.error_traceback }}
        {% endfor %}
    {% endif %}
{% else %}
No actions defined
{% endif %}

====================================================

"""
TEMPLATES = {
    'MONITOR_RESULT_REPORT': MONITOR_RESULT_REPORT,
    'MONITOR_REPORT': MONITOR_REPORT,
}


class Table(AsciiTable):
    CHAR_VERTICAL = ''
    CHAR_CORNER_LOWER_LEFT = ''
    CHAR_CORNER_LOWER_RIGHT = ''
    CHAR_CORNER_UPPER_LEFT = ''
    CHAR_CORNER_UPPER_RIGHT = ''
    CHAR_INTERSECT_BOTTOM = ''
    CHAR_INTERSECT_CENTER = ''
    CHAR_INTERSECT_LEFT = ''
    CHAR_INTERSECT_RIGHT = ''
    CHAR_INTERSECT_TOP = ''
    inner_column_border = False
    outer_border = True


class Report(object):
    def __init__(self):
        self.template_loader = jinja2.DictLoader(self.get_cleaned_templates())
        self.template_env = jinja2.Environment(
            loader=self.template_loader,
            lstrip_blocks=True,
            trim_blocks=True,
        )

    def render(self):
        raise NotImplementedError

    def get_template(self, template):
        return self.template_env.get_template(template)

    def get_cleaned_templates(self):
        return dict([(k, v.strip('\n')) for k, v in TEMPLATES.items()])


class MonitorReport(Report):
    template = 'MONITOR_REPORT'

    def __init__(self, monitor):
        super(MonitorReport, self).__init__()
        self.monitor = monitor

    def render(self):
        template = self.get_template(self.template)
        return template.render(
            rules_table=self._get_rules_table(),
            actions_table=self._get_actions_table(),
            monitor=self.monitor,
        )

    def _get_rules_table(self):
        data = [['RULE', 'TYPE', 'LEVEL']]
        data += [
            [
                d.name,
                d.type,
                d.level,
            ]
            for d in self.monitor.rules_manager.definitions
        ]
        return Table(data)

    def _get_actions_table(self):
        data = [['ACTION', 'RUNS']]
        data += [
            [
                d.name,
                d.state,
            ]
            for d in self.monitor.actions_manager.definitions
        ]
        return Table(data)


class MonitorResultsReport(Report):
    template = MONITOR_RESULT_REPORT

    def __init__(self, result):
        super(MonitorResultsReport, self).__init__()
        self.result = result

    def render(self):
        template = self.get_template('MONITOR_RESULT_REPORT')
        return template.render(
            checks_table=self._get_checks_table(),
            actions_table=self._get_actions_table(),
            result=self.result,
        )

    def _get_checks_table(self):
        data = [['RULE', 'TYPE', 'LEVEL', 'STATE']]
        data += [
            [
                c.definition.name,
                c.definition.type,
                c.definition.level,
                c.state
            ]
            for c in self.result.checks
        ]
        return Table(data)

    def _get_actions_table(self):
        data = [['ACTION', 'TRIGGER_STATE', 'STATE']]
        data += [
            [
                a.definition.name,
                a.definition.state,
                a.state,
            ]
            for a in self.result.actions
        ]
        return Table(data)

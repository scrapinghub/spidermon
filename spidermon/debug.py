import jinja2
from terminaltables import AsciiTable

MONITOR_RESULT_REPORT = """
====================================================
MONITOR REPORT: {{result.monitor.name}}
====================================================
_____________________ checks _______________________

{% if result.checks %}
{{ checks_table.table }}
  TOTAL: {{result.checks|length}}
 PASSED: {{result.passed_checks|length}}
 FAILED: {{result.failed_checks|length}}
 ERRORS: {{result.error_checks|length}}
    {% if result.error_checks %}

_________________ checks errors ____________________

        {% for check in result.error_checks %}
RULE: {{check.definition.name}}
TYPE: {{check.definition.type}}
ERROR: {{check.error_message}}
TRACEBACK: {{check.error_traceback}}
        {% endfor %}
    {% endif %}
{% else %}
No rules defined
{% endif %}

====================================================

"""
TEMPLATES = {
    'MONITOR_RESULT_REPORT': MONITOR_RESULT_REPORT,
}

#____________________ actions _______________________


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

    def get_template(self, template):
        return self.template_env.get_template(template)

    def get_cleaned_templates(self):
        return dict([(k, v.strip('\n')) for k, v in TEMPLATES.items()])


class MonitorResultsReport(Report):
    template = MONITOR_RESULT_REPORT

    def __init__(self, result):
        super(MonitorResultsReport, self).__init__()
        self.result = result

    def render(self):
        template = self.get_template('MONITOR_RESULT_REPORT')
        return template.render(
            checks_table=self._get_checks_table(),
            result=self.result,
        )

    def _get_checks_table(self):
        data = [['RULE', 'TYPE', 'LEVEL', 'STATE']]
        data += [
            [
                c.definition.name,
                c.definition.type,
                c.definition.level,
                c.result
            ]
            for c in self.result.checks
        ]
        return Table(data)

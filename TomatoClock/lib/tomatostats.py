# -*- coding: utf-8 -*-
# Created: 3/13/2018
# Project : TomatoClock
import datetime
import json
from operator import itemgetter

trans = {
    'TOMATO COLOCK': {'zh_CN': u'番茄时钟', 'en': u'Tomato Clock'},
    "'Minutes Studied'": {'zh_CN': u"'学习分钟数'", 'en': u"'Minutes Studied'"},
    "'Best Focus Hour'": {'zh_CN': u"'最佳学习时间'", 'en': u"'Best Focus Hour'"},
    "'Count of Tomatoes and Minutes'": {'zh_CN': u"'番茄和学习分钟'",
                                        'en': u"'Count of Tomatoes and Minutes'"},
    "'Tomato Count'": {'zh_CN': u"'番茄个数'", 'en': u"'Tomato Count'"},
    "'{a} <br/>{b} Clock: {c} ({d}%)'": {'zh_CN': u"'{a} <br/>{b} 点: {c} ({d}%)'",
                                         'en': u"'{a} <br/>{b} Clock: {c} ({d}%)'"},
}


def _(key):
    from anki.lang import currentLang
    lang = currentLang
    key = key.upper().strip()
    if lang != 'zh_CN' and lang != 'en' and lang != 'fr':
        lang = 'en'  # fallback

    def disp(s):
        return s.lower().capitalize()

    for k, v in trans.items():
        trans[k.upper()] = v

    if key not in trans or lang not in trans[key]:
        return disp(key)
    return trans[key][lang]


class TomatoStats:
    def __init__(self, db, debug=False):
        self.debug = debug
        if self.debug:
            from .db import TomatoDB
            assert isinstance(db, TomatoDB)
        self.db = db

    def reports(self):
        html = """
        %s
        <table>
            <tr width=100%%>
                    <td width=300px height=300px id=tomato_count></td>
                    <td width=300px height=300px id=tomato_hour></td>
            </tr>
        </table>
        %s
        """
        return html % (self._js_ref, u"""
        <script>
        {}
        </script>
        """.format(u"".join(
            [
                self._chart_tomato_hour(),
                self._chart_tomato_count()
            ]
        )))

    @property
    def _js_ref(self):
        return u"""
        <script src="http://echarts.baidu.com/examples/vendors/echarts/echarts.min.js"></script>
        """

    def _graph(self, id, conf):
        id = unicode(id, encoding="utf-8")
        html = u"""
        echarts.init(document.getElementById('%(id)s')).setOption(%(conf)s);
        """ % dict(id=id, conf=json.dumps(conf).replace("\"", ""))
        return html

    @property
    def report_days(self):
        return (datetime.datetime.now() + datetime.timedelta(days=-7)).date()

    def _chart_tomato_count(self, ):
        _list_data = self.db.execute(
            """
            SELECT
              strftime('%m/%d',ts.tomato_dt)                 TOMATO_DT,
              round(sum(ts.target_secs) / 60.0, 2)            MINS,
              count(ts.id) COUNT
            FROM tomato_session ts
            
            WHERE ended IS NOT NULL AND
                  round((strftime('%s', ts.ended) - strftime('%s', ts.started)), 2)
                  >= ts.target_secs
                  AND date(ts.tomato_dt) >= ?
                  AND ts.deck = ?
            GROUP BY strftime('%m/%d',ts.tomato_dt)
            """, self.report_days, self.db.deck['id']).fetchall()

        if not _list_data:
            return ''

        conf = dict(
            tooltip=dict(
                trigger="'item'",
            ),
            title={
                # "text": "'Count of Tomatoes and Minutes'",
                "subtext": _("'Count of Tomatoes and Minutes'")
            },
            # legend={"data": [u"'Tomato Count'", u"'Minutes Studied'"]},
            xAxis=
            dict(data=["'%s'" % i[0] for i in _list_data]),
            yAxis={},
            series=[
                dict(

                    name=_("'Tomato Count'"),
                    label=dict(normal=dict(
                        show=False,
                        position="'center'"),
                        emphasis=dict(show=True,
                                      textStyle=dict(
                                          fontSize="'30'",
                                          fontWeight="'bold'"))
                    ),
                    type=u"'bar'",
                    data=[i[2] for i in _list_data]  # cound of tomato
                )
                , dict(
                    name=_("'Minutes Studied'"),
                    label=dict(normal=dict(
                        show=False,
                        position="'center'"),
                        emphasis=dict(show=True,
                                      textStyle=dict(
                                          fontSize="'30'",
                                          fontWeight="'bold'"))
                    ),
                    type=u"'bar'",
                    data=[i[1] for i in _list_data]  # minutes
                )
            ]
        )
        # str([i[0] for i in _list_data]),
        # str([i[1] for i in _list_data]),
        # str([i[2] for i in _list_data]),

        return self._graph("tomato_count", conf)

    def _chart_tomato_hour(self, ):
        _list_data = self.db.execute(
            """
            SELECT
              strftime('%H',ts.started)                 HOUR,
             round( sum(ts.target_secs) / 60.0,2) MINS
            FROM tomato_session ts
            WHERE ended IS NOT NULL AND
                  round((strftime('%s', ts.ended) - strftime('%s', ts.started)), 2)
                  >= ts.target_secs
                  AND ts.tomato_dt >= ?
                  AND ts.deck = ?
            GROUP BY strftime('%H',ts.started)
            order by strftime('%H',ts.started)
            """, self.report_days, self.db.deck['id']).fetchall()

        if not _list_data:
            return ''

        if self.debug:
            _list_data = [
                [0, 33.1],
                [1, 22],
                [2, 14],
                [3, 0.5],
                [4, 22.7],
                [5, 19],
                [6, 43],
                [7, 59],
                [8, 20],
                [9, 11],
                [10, 0.9],
                [11, 0.9],
                [12, 0.9],
                [13, 0.9],
                [14, 0.9],
                [25, 0.9],
                [16, 0.9],
                [17, 0.9]
            ]
        _list_data = sorted(_list_data, key=itemgetter(1), reverse=True)[:6]

        conf = dict(
            tooltip=dict(
                trigger="'item'",
                formatter=_("'{a} <br/>{b} Clock: {c} ({d}%)'")
            ),
            title={
                # "text": "'Count of Tomatoes and Minutes'",
                "subtext": _("'Best Focus Hour'")
            },
            series=[
                dict(
                    name=_("'Minutes Studied'"),
                    type="'pie'",
                    roseType="'area'",
                    # center=["'45%'", "'45%'"],
                    radius=["'50%'", "'70%'"],
                    avoidLabelOverlap=True,
                    label=dict(
                        # normal=dict(
                        #     show=False,
                        #     position="'center'"),

                        emphasis=dict(show=True,
                                      textStyle=dict(
                                          # fontSize="'30'",
                                          fontWeight="'bold'"))
                    ),
                    labelLine=dict(
                        normal=dict(
                            show=True
                        )
                    ),
                    data=[
                        dict(value=row[1], name="'%s'" % int(row[0])) for row in _list_data
                    ]
                )
            ]
        )
        return self._graph("tomato_hour", conf)

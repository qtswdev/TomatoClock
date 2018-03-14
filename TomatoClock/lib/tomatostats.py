# -*- coding: utf-8 -*-
# Created: 3/13/2018
# Project : TomatoClock
import datetime
import json

trans = {
    'TOMATO COLOCK': {'zh_CN': u'番茄时钟', 'en': u'Tomato Clock'}
}


def _(key):
    from anki.lang import currentLang
    lang = currentLang
    key = key.upper().strip()
    if lang != 'zh_CN' and lang != 'en' and lang != 'fr':
        lang = 'en'  # fallback

    def disp(s):
        return s.lower().capitalize()

    if key not in trans or lang not in trans[key]:
        return disp(key)
    return trans[key][lang]


class TomatoStats:
    def __init__(self, db, debug=False):
        if debug:
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
                "subtext": "'Count of Tomatoes and Minutes'"
            },
            # legend={"data": [u"'Tomato Count'", u"'Minutes Studied'"]},
            xAxis=
            dict(data=["'%s'" % i[0] for i in _list_data]),
            yAxis={},
            series=[
                dict(

                    name=u"'Tomato Count'",
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
                    name=u"'Minutes Studied'",
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

        conf = dict(
            tooltip=dict(
                trigger="'item'",
            ),
            title={
                # "text": "'Count of Tomatoes and Minutes'",
                "subtext": "'Best Focus Hour'"
            },
            series=[
                dict(
                    name="'Minutes Studied'",
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

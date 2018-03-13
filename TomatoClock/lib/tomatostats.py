# -*- coding: utf-8 -*-
# Created: 3/13/2018
# Project : TomatoClock
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

    def _chart_tomato_count(self, ):
        _list_data = self.db.stat_tomato_count(-7)
        if not _list_data:
            return ''
        conf = dict(
            tooltip=dict(
                trigger="'item'",
            ),
            legend={"data": u"'Tomato Count'"},
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
                    data=[i[2] for i in _list_data]
                )
            ]
        )
        # str([i[0] for i in _list_data]),
        # str([i[1] for i in _list_data]),
        # str([i[2] for i in _list_data]),

        return self._graph("tomato_count", conf)

    def _chart_tomato_hour(self, ):
        _list_data = self.db.stat_tomato_hour(-7)

        if not _list_data:
            return ''

        conf = dict(
            tooltip=dict(
                trigger="'item'",
            ),

            series=[
                dict(
                    name="'Minutes Studied'",
                    type="'pie'",
                    roseType="'area'",
                    center=["'60%'", "'40%'"],
                    radius=[30, 110],
                    avoidLabelOverlap=False,
                    label=dict(normal=dict(
                        show=False,
                        position="'center'"),
                        emphasis=dict(show=True,
                                      textStyle=dict(
                                          fontSize="'30'",
                                          fontWeight="'bold'"))
                    ),
                    labelLine=dict(
                        normal=dict(
                            show=False
                        )
                    ),
                    data=[
                        dict(value=row[1], name="'%s'" % int(row[0])) for row in _list_data
                    ]
                )
            ]
        )
        return self._graph("tomato_hour", conf)

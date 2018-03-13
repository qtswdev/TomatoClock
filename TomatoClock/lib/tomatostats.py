# -*- coding: utf-8 -*-
# Created: 3/13/2018
# Project : TomatoClock
import json


class TomatoStats:
    def __init__(self, db, debug=False):
        if debug:
            from .db import TomatoDB
            assert isinstance(db, TomatoDB)
        self.db = db

    def reports(self):
        return self._js_ref + self._chart_tomato_hour() + self._chart_tomato_count()

    @property
    def _js_ref(self):
        return """
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/highcharts-more.js"></script>
            <script src="https://code.highcharts.com/modules/solid-gauge.js"></script>
            """

    def _chart_tomato_count(self):
        _list_data = self.db.stat_tomato_count(-7)
        if not _list_data:
            return ''
        txt = u"""
            <div id="over_view"></div>
              <script>
              Highcharts.chart('over_view', {
                chart: {
                    zoomType: 'xy'
                },
                title: {
                    text: ''
                },
                subtitle: {
                    text: ''
                },
                xAxis: [{
                    categories: %s,
                    crosshair: true
                }],
                yAxis: [{ // Primary yAxis
                    labels: {
                        format: '{value}',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    },
                    title: {
                        text: 'Tomato Count',
                        style: {
                            color: Highcharts.getOptions().colors[1]
                        }
                    }
                }, { // Secondary yAxis
                    title: {
                        text: 'Minutes',
                        style: {
                            color: Highcharts.getOptions().colors[0]
                        }
                    },
                    labels: {
                        format: '{value}',
                        style: {
                            color: Highcharts.getOptions().colors[0]
                        }
                    },
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                legend: {
                    layout: 'vertical',
                    align: 'left',
                    x: 120,
                    verticalAlign: 'top',
                    y: 100,
                    floating: true,
                    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
                },
                series: [
                {
                    name: 'Minutes',
                    type: 'column',
                    yAxis: 1,
                    data: %s,
                    tooltip: {
                        valueSuffix: ' min'
                    }

                }, {
                    name: 'Tomato',
                    type: 'spline',
                    data: %s,
                    tooltip: {
                        valueSuffix: ''
                    }
                }]
            });
            </script>
        """ % (
            str([i[0] for i in _list_data]),
            str([i[1] for i in _list_data]),
            str([i[2] for i in _list_data]),
        )
        return txt

    def _chart_tomato_hour(self):
        _list_data = self.db.stat_tomato_hour(-7)
        if not _list_data:
            return ''
        txt = """
                <div id="tomato_hour"></div>
                <script>
                Highcharts.chart('tomato_hour', {

                title: {
                    text: 'Tomato Hour'
                },

                xAxis: {
                    categories: %s
                },

                series: [
                {
                    name: 'Minutes studied',
                    type: 'pie',
                    allowPointSelect: true,
                    keys: ['name', 'y', 'selected', 'sliced'],
                    data: %s,
                    showInLegend: true
                }
                ]
            });
            </script>
            """ % (
            str([i[0] for i in _list_data]),
            json.dumps(_list_data)
        )
        return txt

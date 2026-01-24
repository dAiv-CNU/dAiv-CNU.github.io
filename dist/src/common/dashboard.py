from browser import document, window, aio, module_init
print, pyprint = module_init(__name__, "common.dashboard")
from datetime import datetime
from random import randrange


window.Apex = {
    'chart': {
        'foreColor': "#ccc",
        'toolbar': {
            'show': False
        },
    },
    'stroke': {
        'width': 3
    },
    'dataLabels': {
        'enabled': False
    },
    'tooltip': {
        'theme': "dark"
    },
    'grid': {
        'borderColor': "#535A6C",
        'xaxis': {
            'lines': {
                'show': True
            }
        }
    }
}


########################################################################################################################
# Timeline Animation
########################################################################################################################
def build_timeline_chart(timeline, colors=None):
    if colors is None:
        colors = ["#fd5f76", "#f3bb44", "#639bc6"]
    label = ["D-Day", "Period", "Result"]
    data = [0, 0, 0]
    name_labels = {label[0]: "대회 준비중...", label[1]: "D-Day", label[2]: "종료된 대회입니다"}
    default_label = 0

    now = datetime.now().date()
    appl, start, end, result = timeline

    before = (start - appl).days
    duration = (end - start).days + 1
    after = (result - end).days

    if now < appl:  # before application startup
        stat = (appl - now).days
        name_labels = {label[0]: f"참가신청 시작까지 D-{stat}", label[1]: "대회 준비중...", label[2]: "대회 준비중..."}
    elif now < start:  # after application startup
        stat = (start - now).days
        data = [(1-stat/before)*100, 0, 0]
        name_labels = {label[0]: f"대회 시작까지 D-{stat}", label[1]: "참가신청기간", label[2]: "참가신청기간"}
    elif now <= end:  # after d-day
        default_label = 1
        stat = (end - now).days
        data = [100, (1-stat/duration)*100, 0]
        name_labels = {label[0]: "참가신청마감됨",
                       label[1]: "D-Day" if now == start else f"Day {(now - start).days + 1} (D-{stat if stat else 'Day'})",
                       label[2]: f"결과 발표까지 D-{(result - now).days}"}
    elif now <= result:  # before result announcement
        default_label = 2
        stat = (result - now).days
        data = [100, 100, (1-stat/after)*100]
        name_labels = {label[0]: "참가신청마감됨", label[1]: "코드제출마감됨", label[2]: f"결과 발표까지 D-{stat if stat else 'Day'}"}
    else:  # after the contest finished
        default_label = 2
        data = [100, 100, 100]
        name_labels = {label[0]: "참가신청마감됨", label[1]: "코드제출마감됨", label[2]: "종료된 대회입니다"}

    width = window.innerWidth
    position = "left"
    vertical_margin = 0
    if width >= 1400:
        legend = 18
        offset = (130, 20)
    elif width >= 1200:
        legend = 15
        offset = (100, 12)
    elif width >= 992:
        legend = 11
        offset = (80, 2)
        vertical_margin = -2
    elif width >= 768:
        legend = 10
        offset = (78, 2)
        vertical_margin = -3
    elif width >= 576:
        legend = 18
        offset = (120, 18)
    else:
        legend = 12
        offset = (0, 6)
        position = "bottom"

    return {
        'chart': {
            'type': "radialBar",
            'redrawOnParentResize': True
        },
        'plotOptions': {
            'radialBar': {
                'size': None,
                'inverseOrder': False,
                'track': {
                    'show': False,
                },
                'startAngle': 0,
                'endAngle': 300,
                'dataLabels': {
                    'name': {
                        'fontSize': f"{legend}px",
                        'offsetY': 8,
                        'formatter': lambda series_name, is_total, opts: name_labels[series_name]
                    },
                    'value': {
                        'show': False
                    },
                    'total': {
                        'show': True,
                        'fontSize': f"{legend}px",
                        'color': colors[default_label],
                        'label': label[default_label]
                    }
                }
            },
        },
        'stroke': {
            'lineCap': "round"
        },
        'colors': colors,
        'series': data,
        'labels': label,
        'legend': {
            'show': True,
            'floating': True,
            'position': position,
            'offsetX': offset[0],
            'offsetY': offset[1],
            'fontSize': f"{legend}px",
            'itemMargin': {
                'vertical': vertical_margin
            },
            'markers': {
                'width': legend,
                'height': legend
            }
        },
        'responsive': [
            {
                'breakpoint': 576,
                'options': {
                    'legend': {
                        'position': "bottom",
                        'offsetX': 0,
                        'offsetY': 6,
                        'fontSize': "12px",
                        'itemMargin': {
                            'vertical': 0
                        },
                        'markers': {
                            'width': 12,
                            'height': 12
                        }
                    },
                    'plotOptions': {
                        'radialBar': {
                            'dataLabels': {
                                'name': {
                                    'fontSize': "12px"
                                },
                                'total': {
                                    'fontSize': "12px"
                                }
                            }
                        }
                    }
                }
            }
        ]
    }


########################################################################################################################
# Participation Animation
########################################################################################################################
def build_participation_status_chart(data_series, timeline, colors=None, padding=None):
    now = datetime.now().date()
    appl, start, _, _ = timeline

    before = (start - appl).days
    stat = (start - now).days - 1

    if len(data_series) < before:
        data_series.extend([0 for _ in range(before-len(data_series))])

    if padding is None:
        padding = {
            'top': 20,
            'bottom': 10,
            'left': 110
        }

    if colors is None:
        colors = ["#fff"]

    return {
        'chart': {
            'group': "sparks",
            'type': "line",
            'height': 80,
            'sparkline': {
                'enabled': True
            },
            'dropShadow': {
                'enabled': True,
                'top': 1,
                'left': 1,
                'blur': 4,
                'opacity': 0.2,
            }
        },
        'series': [{
            'data': data_series
        }],
        'stroke': {
            'curve': "smooth"
        },
        'markers': {
            'size': 0
        },
        'grid': {
            'padding': padding
        },
        'forecastDataPoints': {
            'count': stat
        },
        'colors': colors,
        'xaxis': {
            'crosshairs': {
                'width': 1
            },
        },
        'tooltip': {
            'x': {
                'show': False
            },
            'y': {
                'title': {
                    'formatter': lambda val, _: "+"
                }
            }
        }
    }


########################################################################################################################
# Leaderboard Animation
########################################################################################################################
def build_leaderboard_chart(values={}, teams=[], colors=None):
    if colors is None:
        colors = ["#fd5f76", "#639bc6", "#00b074"][:len(values)-1]
        colors.append("#f3bb44")

    width = window.innerWidth
    show_len = len(teams)
    if width < 768:  # show only first 5 datasets
        show_len = 5
        teams = teams[:show_len]

    series = [{'name': key, 'type': "line" if len(values)-1==i else "column", 'data': value[:show_len]} for i, (key, value) in enumerate(values.items())]

    return {
        'series': series,
        'chart': {
            'height': 400,
            'type': "bar",
            'stacked': False,
            'toolbar': {
                'show': False,
            }
        },
        'dataLabels': {
            'enabled': False
        },
        'stroke': {
            'show': True,
            'width': [4 if len(values)-1==i else 1 for i in range(len(values))],
            'curve': "smooth"
        },
        'fill': {
            'opacity': 1,
        },
        'colors': colors,
        'legend': {
            'show': True,
            'position': "top",
            'horizontalAlign': "right",
            'markers': {
                'width': 20,
                'height': 10,
                'radius': 2
            }
        },
        'plotOptions': {
            'bar': {
                'horizontal': False,
                'columnWidth': "50%",
                'barHeight': "10%",
                'distributed': False,
            },
        },
        'tooltip': {
            'shared': True,
            'intersect': False,
            'followCursor': True,
            'fixed': {
                'enabled': False,
            },
            'x': {
                'show': False,
            },
            'y': {
                'title': {
                    'formatter': lambda series_name, obj: series_name
                },
                'formatter': lambda value, array: value  # array = {series, seriesIndex, dataPointIndex, w}
            },
        },
        'xaxis': {
            'categories': teams,
            'axisBorder': {
                'show': False,
            },
            'axisTicks': {
                'show': False,
            },
            'crosshairs': {
                'width': 40,
            }
        },
        'yaxis': {
            'labels': {
                'formatter': lambda *args: round(args[0], 1)
            }
        }
    }


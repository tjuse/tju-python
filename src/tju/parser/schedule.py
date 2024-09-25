import re


def parse_schedule(html):
    """
    parse course table
    """
    arrangePairArray = []
    courses = []
    arrangeHtmls = re.findall(r"in TaskActivity([\s\S]+?)fillTable", html)[0].split(
        "var teachers"
    )
    for arrangeItem in arrangeHtmls[1:]:
        rawTeachers = re.findall("var actTeachers = ([^;]+);", arrangeItem)[0]
        teacherArray = re.findall('"([^"]+)"', rawTeachers)
        # 这节课的信息
        lineList = arrangeItem.split(";")
        # 课程相关
        courseLine = lineList[14].split(",")
        # classID
        classID = re.findall(r"\((\w+)\)", courseLine[4])[0]
        threePair = re.findall('"([^"]+)","[^"]*","([^"]*)","([01]+)"', arrangeItem)[0]
        location = threePair[1].strip()
        rawWeeks = threePair[2].strip()
        weekArray = []
        for i, b in enumerate(rawWeeks):
            if b == "1":
                weekArray.append(i)
        twoPair = re.findall(r"([0-9]+)\*unitCount\+([0-9]+)", arrangeItem)
        weekday = int(twoPair[0][0]) + 1
        unitArray = list(map(lambda x: int(x[1]) + 1, twoPair))
        arrangePairArray.append(
            (
                classID,
                {
                    "teacher": teacherArray,
                    "week": weekArray,
                    "unit": unitArray,
                    "weekday": weekday,
                    "location": location,
                },
            )
        )
    trs = re.findall(
        r"<tr([\s\S]+?)</tr>", re.findall(r"<tbody([\s\S]+?)</tbody>", html)[0]
    )
    for tr in trs:
        tds = re.findall(r"<td>([\s\S]+?)</td>", tr)
        if len(tds) <= 9:
            continue
        serial = re.findall(r">(\d*)</a>", tds[1])[0]
        no = tds[2]
        name = tds[3]
        if "style" in tds[3]:
            name = (
                re.findall("(.+?)<sup", tds[3])[0].strip()
                + " "
                + re.findall('">(.+?)</s', tds[3])[0].strip()
            )
        credit = float(tds[4])
        teachers = tds[5].split(",")
        weeks = tds[6].strip()
        campus = ""
        if re.findall("(.+?校区)", tds[9]):
            campus = re.findall("(.+?校区)", tds[9])[0].strip()
        courseData = {
            "class_id": serial,
            "course_id": no,
            "name": name,
            "credit": str(credit),
            "teacher": teachers,
            "weeks": weeks,
            "campus": campus,
        }
        courseData["arrange"] = list(
            map(lambda x: x[1], filter(lambda x: x[0] == serial, arrangePairArray))
        )
        courses.append(courseData)
    return courses

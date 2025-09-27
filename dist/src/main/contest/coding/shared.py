from browser import document, window, aio, module_init
print, pyprint = module_init(__name__, "contest.coding.shared")
from common.dashboard import build_timeline_chart, build_participation_status_chart, build_leaderboard_chart
from datetime import datetime
from random import choice
import traceback
import base64
import json


__WEB_CLIENT_TOKEN = "+e?65NZa@=[OY(iMX@t3q1O^lTCg7t/eI!rfqS/@&MaF~*3>[g"


def parse_timeline_data():
    date_format = "%Y년 %m월 %d일"
    date = lambda d: datetime.strptime(d, date_format).date()

    application_period = document['application_period'].textContent.split(": ")[1]
    contest_period = document['contest_period'].textContent.split(": ")[1]
    result_announcement = document['result_announcement'].textContent.split(": ")[1]

    appl = application_period.split(" (")[0]
    start, end, *_ = contest_period.split(" (")
    end = end.split("~ ")[1]
    result = result_announcement.split(" (")[0]
    timeline = date(appl), date(start), date(end), date(result)
    return timeline


########################################################################################################################
# AOS Animation
########################################################################################################################
window.AOS.init()


########################################################################################################################
# Timeline Animation
########################################################################################################################
try:
    window.ApexCharts.new(document.querySelector("#timeline_radial_bar_chart"),
                          build_timeline_chart(parse_timeline_data())
                          ).render()
except Exception as _:
    traceback.print_exc()


########################################################################################################################
# Participation Status Animation
########################################################################################################################
async def set_join_status():
    try:
        chart = document.querySelector("#participants_status_chart")
        if chart.attributes.data.value:
            dataset = list(map(int, chart.attributes.data.value.replace(' ', '').split(',')))
        else:
            result = await window.fetch(chart.attributes.api.value, {
                'method': "POST",
                'headers': {
                    'Authorization': f"Bearer {__WEB_CLIENT_TOKEN}"
                }
            })
            dataset_raw = await result.text()
            chart.attributes.data.value = dataset_raw.replace('[', '').replace(']', '')
            dataset = json.loads(dataset_raw)

        total_team = sum(dataset)
        count_desc = document.getElementById('participants_count_desc')
        count = document.getElementById('participants_count')
        if count_desc:
            count_desc.innerHTML = count_desc.innerHTML.replace("{participants}", f"{total_team}")
        if count:
            count.innerHTML = count.innerHTML.replace("{participants}", f"{total_team}")

        chart_wrapper = document.getElementById('participants_status_chart_wrapper')
        if chart_wrapper:
            chart_wrapper.classList.add(choice(['chart-wrapper-var0', 'chart-wrapper-var1']))

        window.ApexCharts.new(chart, build_participation_status_chart(dataset, parse_timeline_data())).render()
    except Exception as _:
        traceback.print_exc()

aio.run(set_join_status())


########################################################################################################################
# QnA
########################################################################################################################
async def set_iframe():
    pushoong = None  # prevent garbage collection
    try:
        pushoong = window.frames['pushoong'].document
    except Exception as _:
        return  # no qna iframe in the HTML
    psh_url = document.getElementsByName("pushoong")[0].attributes.data.value
    psh_req = await window.fetch(psh_url)
    psh_html = ((await psh_req.text()).replace("115px", "0px")
                .replace("//t1.daumcdn.net/kas/static/ba.min.js", "")
                .replace("Kakao.init('4cca00b63eedb801abfc9952db0ee7a3');", "")
                .replace("<head>", "<head>"
                                    "<base href=\"https://pushoong.com/\">"
                                    "<link href=\""+window.location.origin+"/dist/res/css/font.css\" rel=\"stylesheet\">"
                                    "<style>.increase_max_width {max-width: 1000px !important;}</style>")
                .replace("<body>", "<body style=\"background-color: #fff;\">")
                .replace("<div class=\"container\">", "<div class=\"container\" style=\"background-color: #fff;\">")
                .replace("<div id=\"fullscreen-overlay\">", "<div id=\"fullscreen-overlay-disabled\" style=\"display:none;\">")
                .replace("<div class=\"attach_border\" style=\"", "<div class=\"attach_border\" style=\"display:none;")
                .replace("input_border col", f"col mt-1 ml-1\" onclick=\"window.open('{psh_url}', '_blank');")
                .replace("id=\"ask_send\"", "id=\"ask_send_disabled\"")
                .replace("<div class = \"container\">", "<div class = \"increase_max_width container\">")
                .replace("ask_wrapper not_host", "increase_max_width ask_wrapper not_host")
                .replace("https://tag.poomang.com/js.reign/pushoong_web/pushoongw_pc_ask_in/t1", "")
                .replace("https://tag.poomang.com/js.reign/pushoong_web/pushoongw_mo_ask_in/t1", "")
                .replace("ask_title_zone", "increase_max_width ask_title_zone")
                .replace("ask_input_zone", "increase_max_width ask_input_zone"))

    if pushoong:
        pushoong.open()
        pushoong.write(psh_html)
        pushoong.close()
        while True:
            await aio.sleep(0.001)
            for wrapper in pushoong.getElementsByClassName('increase_max_width ask_wrapper'):
                wrapper.style.top = "0px"
            for wrapper in pushoong.getElementsByClassName('increase_max_width ask_title_zone'):
                wrapper.style.top = "0px"
            if pushoong.readyState == "complete":
                break

aio.run(set_iframe())


########################################################################################################################
# prompt
########################################################################################################################
def submit_prompt(url):
    def wrapped(e):
        e.preventDefault()

        prompt = document.getElementById('create_prompt')
        image_display_area = document.getElementById('generatedimage')

        try:
            async def Submit():
                form_data = window.FormData.new()
                form_data.append("prompt", prompt.value)

                try:
                    result = await window.fetch(url, {
                        'method': "POST",
                        'headers': {
                            'Accept': 'image/png'
                        },
                        'body': form_data
                    })

                    if result.status == 200:
                        image_blob = await result.blob()
                        
                        img_tag = document.createElement('img')
                        img_tag.src = window.URL.createObjectURL(image_blob)
                        img_tag.alt = "Generated Image"
                        img_tag.classList.add('img-fluid', 'mt-3')

                        if image_display_area:
                            image_display_area.innerHTML = '' 
                            image_display_area.appendChild(img_tag)

                    else:
                        if image_display_area:
                            image_display_area.innerHTML = '<div class="alert alert-danger" role="alert">이미지 생성 실패!</div>'

                except Exception as _:
                    if image_display_area:
                        image_display_area.innerHTML = '<div class="alert alert-danger" role="alert">이미지 로드 중 오류 발생!</div>'
                    traceback.print_exc()

            aio.run(Submit())

        except Exception as _:
            traceback.print_exc()
    return wrapped


########################################################################################################################
# Leaderboard settings
########################################################################################################################
def open_leaderboard(e):
    try:
        async def remove_show_button(btn):
            value = btn.offsetHeight
            while True:
                if value < 0:
                    break
                elif value < 15:
                    btn.innerHTML = ""
                    btn.style.padding = "1.5px"
                value -= 1
                btn.style.height = f"{value}px"
                await aio.sleep(0.005)

        async def remove_hider(obj):
            value = 1
            while True:
                if value < 0:
                    break
                value -= 0.01
                obj.style.opacity = f"{value}"
                await aio.sleep(0.01)
            obj.remove()

        aio.run(remove_show_button(e.currentTarget))
        hider = document.getElementById('leaderboard_hider')
        if hider:
            aio.run(remove_hider(hider))
    except Exception as _:
        traceback.print_exc()


def watch_form(data, validation, message=(lambda d: "", lambda d: "")):
    def watcher(_):
        if data and validation:
            try:
                validation.textContent = message[0](data)
                if not data.classList.contains('is-valid'):
                    data.classList.add('is-valid')
                if data.classList.contains('is-invalid'):
                    data.classList.remove('is-invalid')
                if validation.classList.contains('invalid-feedback'):
                    validation.classList.remove('invalid-feedback')
                if not validation.classList.contains('valid-feedback'):
                    validation.classList.add('valid-feedback')
            except ValueError:
                validation.textContent = message[1](data)
                if data.classList.contains('is-valid'):
                    data.classList.remove('is-valid')
                if not data.classList.contains('is-invalid'):
                    data.classList.add('is-invalid')
                if not validation.classList.contains('invalid-feedback'):
                    validation.classList.add('invalid-feedback')
                if validation.classList.contains('valid-feedback'):
                    validation.classList.remove('valid-feedback')
    return watcher


def submit_leaderboard(url, team_list):
    def wrapped(e):
        e.preventDefault()  # disable default form submission method

        modal_body = document.getElementById('leaderboard_modal_body_text')
        launcher = document.getElementById('leaderboard_modal_launcher')
        team_idx = document.getElementById('leaderboard_form_username')
        password = document.getElementById('leaderboard_form_password')
        file_input = document.getElementById('leaderboard_form_file')

        try:
            if not team_idx.value.isdigit() or not (0 <= int(team_idx.value) <= len(team_list)):
                team_idx.value = ""
                return
            team_name, pass_word = team_list[int(team_idx.value)], password.value

            modal_body.innerHTML = f"{team_name}팀의 결과를 제출 중 입니다.<br>창을 닫지 말고 잠시만 기다려주세요..."
            launcher.click()

            async def submit():
                file = file_input.files[0]
                form_data = window.FormData.new()
                form_data.append("csv_file", file, file.name)

                select_num = document.getElementById('target_select')

                if select_num:
                    select_num_submit = select_num.value
                    print(select_num_submit)
                    result = await window.fetch(url + team_name, {
                        'method': "POST",
                        'headers': {
                            'Authorization': f"Bearer {__WEB_CLIENT_TOKEN}",
                            'username': base64.b64encode(team_name.encode('utf-8')).decode('utf-8'),
                            'password': base64.b64encode(pass_word.encode('utf-8')).decode('utf-8'),
                            'target' : base64.b64encode(select_num_submit.encode('utf-8')).decode('utf-8'),
                        },
                        'body': form_data
                    })
                else:
                    result = await window.fetch(url + team_name, {
                        'method': "POST",
                        'headers': {
                            'Authorization': f"Bearer {__WEB_CLIENT_TOKEN}",
                            'username': base64.b64encode(team_name.encode('utf-8')).decode('utf-8'),
                            'password': base64.b64encode(pass_word.encode('utf-8')).decode('utf-8')
                        },
                        'body': form_data
                    })



                if result.status == 200:
                    fetched = await result.json()
                    print(fetched)
                    if fetched.status == "success":
                        modal_body.innerHTML = f"제출이 완료되었습니다.<br><br>축하합니다!<br>이번 제출의 채점 결과는 {fetched.message} 입니다."
                    else:
                        modal_body.innerHTML = f"제출에 실패했습니다. 다시 시도해주세요.<br>사유: {fetched.message}"
                elif result.status == 403:
                    error_data = await result.json()
                    modal_body.innerHTML = f"비밀번호가 올바르지 않거나 제출이 허가되지 않은 대회 입니다.<br>다시 시도해주세요.<br><br>코드: {result.status} {result.statusText}<br>메시지: {error_data.detail}"
                    password.value = ""
                    validation = document.getElementById('leaderboard_form_password_validation')
                    validation.textContent = "확인이 필요합니다."
                    if password.classList.contains('is-valid'):
                        password.classList.remove('is-valid')
                    if not password.classList.contains('is-invalid'):
                        password.classList.add('is-invalid')
                    if not validation.classList.contains('invalid-feedback'):
                        validation.classList.add('invalid-feedback')
                    if validation.classList.contains('valid-feedback'):
                        validation.classList.remove('valid-feedback')
                else:
                    error_data = await result.json()
                    modal_body.innerHTML = f"처리되지 못한 오류로 제출에 실패했습니다. 다시 시도해주세요.<br><br>코드: {result.status} {result.statusText}<br>메시지: {error_data.detail}"
            aio.run(submit())
        except Exception as _:
            traceback.print_exc()
    return wrapped


username_messages = lambda u: f"{int(u.value)+1}번째 팀을 선택하셨습니다.", lambda u: "팀 이름이 올바르지 않습니다."
password_messages = lambda p: "Looks good!" if p.value else (_ for _ in ()).throw(ValueError), lambda p: "비밀번호는 비어있을 수 없습니다."
file_input_messages = lambda f: f"{f.value}를 제출합니다." if f.value else (_ for _ in ()).throw(ValueError), lambda f: "제출할 파일이 선택되지 않았습니다."
target_messages = lambda t: f"{t.value}번째 타겟을 선택하셨습니다." if t.value else (_ for _ in ()).throw(ValueError), lambda t: "타겟이 선택되지 않았습니다."

async def fetch_score_async(event):
    print("get score")

    team_name_text = document.getElementById('teamSearch')
    team_name = document.getElementById('teamName')

    team_name.text = team_name_text.value

    url = "http://daivserver.duckdns.org:20261/leaderboard/" + f"{team_name_text.value}"

    result = await window.fetch(url , {
        'method': "GET",
        'headers': {
            'Authorization': f"Bearer {__WEB_CLIENT_TOKEN}"
        }
    })

    if result.ok:
        data = await result.json()

        score_text = document.getElementById('teamScore')
        rank_badge_text = document.getElementById('rankBadge')

        score_text.text = data["score"]
        rank_badge_text.text = data["rank"]

    else:
        score_text = document.getElementById('teamScore')
        score_text.text = "팀 없음"



def get_score_handler(event):
    event.preventDefault()
    aio.run(fetch_score_async(event))


def prompt_submit(event):
    print("prompt_submit called")

    async def submit():
        prompt_form = document['prompt_image_container']
        if prompt_form:
            prompt_text_area = document['create_prompt']

            prompt_text = prompt_text_area.value

            result = await window.fetch(prompt_form.action, {
                'method': "POST",
                'headers': {
                    'prompt': base64.b64encode(prompt_text.encode('utf-8')).decode('utf-8'),
                }
            })

            if result.ok:
                fetched = json.loads(await result.text())

                mime_type = fetched['mime_type']
                image_data = fetched['image_data']
                image_url = f"data:{mime_type};base64,{image_data}"

                file_path = fetched['file_path']
                prompt_text_area.value = file_path

                image_element = document['generatedimage']
                image_element.src = image_url
                image_element.style.display = "block"

                placeholder = document['imageplaceholder']
                placeholder.style.display = "none"

            else:
                window.alert("이미지 생성에 실패했습니다.")

    aio.run(submit())

async def set_leaderboard_data():
    dataset = dict(teams=[], values=dict())  # prevent garbage collection
    key_func = lambda x: x[0]  # do not define a function inside try-except block (Brython bug - undefined)
    force_open_hider = False
    try:
        leaderboard = document.querySelector("#leaderboard_chart")
        if leaderboard is None:
            return  # no leaderboard chart in the HTML

        if leaderboard.innerHTML:
            raw_data = leaderboard.innerHTML
            leaderboard.innerHTML = ""
            dataset = json.loads(raw_data, parse_float=lambda x: float(x))

            if len(dataset['teams']) == 0:  # Online Leaderboard Mode
                print("INFO: Trying to fetch leaderboard data from server...")
                form = document.getElementById('leaderboard_form')
                if form:
                    # fetch data
                    result = await window.fetch(form.action, {
                        'method': "POST",
                        'headers': {
                            'Authorization': f"Bearer {__WEB_CLIENT_TOKEN}"
                        }
                    })
                    fetched = json.loads(await result.text())

                    if not fetched:  # no team in the fetched dataset
                        print("INFO: No team data in the fetched dataset so hiding the leaderboard...")
                        document.querySelector("#leaderboard").classList.add('d-none')
                        return

                    # update dataset
                    dataset['teams'] = fetched['teams']
                    if sum(sum([float(str(v)) for v in values]) for values in fetched["values"].values()) == 0:  # no data in the fetched dataset
                        # apexchart cannot render if all values are zero, so put fake values
                        fake_total_values = [100.0 for _ in fetched['teams']]
                        # and there's no data in the leaderboard, don't need to hide the chart
                        force_open_hider = True
                    else:
                        fake_total_values = [0.0 for _ in fetched['teams']]
                    for key, data in zip(dataset['values'].keys(), [*fetched['values'].values(), fake_total_values]):
                        dataset['values'][key] = [float(str(d)) for d in data]
                else:
                    raise ValueError("Fetch URL Error - No data available for leaderboard!!")
            else:  # Offline Leaderboard Mode
                print("INFO: Using Offline leaderboard data...")
        else:
            raise ValueError("Please specify leaderboard format in the HTML")

        # parse team list
        team_list = [t for t in dataset['teams']]

        # arrange dataset
        # # select sorting criteria
        criteria = ""
        keys = list(dataset['values'].keys())
        keys.reverse()
        for key in keys:  # dict(reversed(a['values'].items())) not working properly in brython
            criteria = key
            if sum(dataset['values'][key]) > 0:
                break
        # # sort
        if criteria:
            zipped = zip(dataset['values'][criteria], zip(dataset['teams'], *dataset['values'].values()))
            reversed_zipped = sorted(zipped, key=key_func, reverse=True)
            sorted_zip = [value for key, value in reversed_zipped]
            unzipped = list(zip(*sorted_zip))
            dataset['teams'] = unzipped.pop(0)
            dataset['values'] = {key: dt for dt, key in zip(unzipped, dataset['values'].keys())}

        # render chart
        chart = window.ApexCharts.new(leaderboard, build_leaderboard_chart(**dataset))
        chart.render()
        [chart.toggleSeries(key) for key in keys if sum(dataset['values'][key]) <= 0]

        # set leaderboard opener
        opener = document.getElementById('btn_leaderboard')
        if opener:
            opener.bind('click', open_leaderboard)
            if force_open_hider:
                opener.click()

        _, start, end, _ = parse_timeline_data()
        print(f"Leaderboard available from {start} to {end}.")

        prompt_container = document.getElementById('image_prompt')

        if prompt_container and start <= datetime.now().date() <= end:
            prompt_container.classList.remove('d-none')

            search_form = document.getElementById('searchForm')
            prompt_btn = document.getElementById('create_image_btn')

            prompt_btn.bind('click', prompt_submit)
            print("prompt_btn binded")

            search_form.bind("submit",get_score_handler)



        # set the leaderboard submission form
        form_container = document.getElementById('leaderboard_form_container')

        if form_container and start <= datetime.now().date() <= end:
            form_container.classList.remove('d-none')
            form = document.getElementById('leaderboard_form')

            url = form.action
            if not url.endswith('/'):
                url = url + '/'

            # set the team list to the form
            team_selections = document.getElementById('leaderboard_form_username')
            for data in enumerate(team_list):
                option = document.createElement('option')
                option.value, option.text = data
                team_selections.appendChild(option)

            form.onsubmit = submit_leaderboard(url=url, team_list=team_list)
            target = document.getElementById('target_select')
            validation = document.getElementById('leaderboard_form_target_validation')
            if target and validation:
                target.bind('change', watch_form(target, validation, target_messages))
            username = document.getElementById('leaderboard_form_username')
            validation = document.getElementById('leaderboard_form_username_validation')
            if username and validation:
                username.bind('change', watch_form(username, validation, username_messages))
            password = document.getElementById('leaderboard_form_password')
            validation = document.getElementById('leaderboard_form_password_validation')
            if password and validation:
                password.bind('change', watch_form(password, validation, password_messages))
            file_input = document.getElementById('leaderboard_form_file')
            validation = document.getElementById('leaderboard_form_file_validation')
            if file_input and validation:
                file_input.bind('change', watch_form(file_input, validation, file_input_messages))
    except Exception as _:
        traceback.print_exc()


aio.run(set_leaderboard_data())


########################################################################################################################
# Winner Poduim settings
########################################################################################################################
def open_winnerpodium(e):
    try:
        result_panel = document['winnerpodium_result_panel']
        if result_panel:
            async def show_result(pan):
                value = 0
                while True:
                    if value > 1:
                        break
                    value += 0.01
                    pan.style.opacity = f"{value}"
                    await aio.sleep(0.01)

            aio.run(show_result(result_panel))

        async def remove_show_button(btn):
            value = 1
            while True:
                if value < 0:
                    break
                value -= 0.01
                btn.style.opacity = f"{value}"
                await aio.sleep(0.01)

        aio.run(remove_show_button(e.currentTarget))
    except Exception as _:
        traceback.print_exc()


try:
    opener = document['btn_open_winnerpodium']
    if opener:
        opener.bind('click', open_winnerpodium)
    panel = document['winnerpodium_result_panel']
    if panel:
        panel.style.opacity = "0"
except Exception as _:
    traceback.print_exc()

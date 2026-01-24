from browser import document, window, aio, module_init
print, pyprint = module_init(__name__, "index.index")


########################################################################################################################
# AOS Animation
########################################################################################################################
window.AOS.init()


########################################################################################################################
# Programs List
########################################################################################################################
def enable_isotope():
    if hasattr(window, "programs_isotope") and window.programs_isotope:
        window.programs_isotope.destroy()

    visible_sections = document.querySelectorAll('.container:not(.d-none)')
    for section in visible_sections:
        if section.id.startswith("programs_"):
            container = section.getElementsByClassName("programs-container")[0]
            if container:
                # Isotope 새로 초기화
                window.programs_isotope = window.Isotope.new(container, {
                    'itemSelector': ".programs-item",
                    'layoutMode': "masonry"
                })
                window.AOS.refresh()
                break


def flag_selected_tag(selected):
    for li in document.getElementById('programs_filter').getElementsByClassName('filter-active'):
        li.classList.remove('filter-active')
    selected.classList.add('filter-active')


def change_filter(event):
    programs_filter = document.getElementById('programs_filter').children
    filter_value = event.currentTarget.dataset.filter
    window.programs_isotope.arrange({'filter': filter_value})
    window.programs_isotope.on('arrangeComplete', lambda _: window.AOS.refresh())
    if 'program-type' in event.currentTarget.classList:
        for fil in programs_filter:
            if filter_value == fil.attributes['data-filter'].nodeValue:
                flag_selected_tag(fil)
                break
    else:
        flag_selected_tag(event.currentTarget)


def setup_programs_filter():
    visible_sections = document.querySelectorAll('.container:not(.d-none)')
    for section in visible_sections:
        if section.id.startswith("programs_"):
            filter_elem = section.getElementsByClassName("programs-filter")[0]
            if not filter_elem:
                return

            buttons = filter_elem.children
            for el in buttons + list(section.getElementsByClassName('program-type')):
                el.onclick = change_filter


########################################################################################################################
# Set Datas by Year
########################################################################################################################
from common.main import current_year, insert_element, scroll_to


def change_year_visibility(e):
    data_type, year = e.currentTarget.id.split("_selector_")
    for el in document.querySelectorAll(f'[id^="{data_type}_"]'):
        if "_selector_" in el.id:
            continue
        id_parts = el.id.split("_")
        if len(id_parts) != 2:
            continue
        if not id_parts[1].isdigit():
            continue
        el.classList.add('d-none')

    section = document.getElementById(f'{data_type}_{year}')
    section.classList.remove('d-none')

    adjust_selector_visibility(year, data_type)

    if data_type == "programs":
        container = section.getElementsByClassName("programs-container")[0]
        images = container.getElementsByTagName("img")
        total = len(images)

        async def wait_and_initialize():
            if total == 0:
                enable_isotope()
                setup_programs_filter()
                await aio.sleep(0.05)
                window.AOS.init()
                window.AOS.refresh()
                return

            futures = []
            for img in images:
                future = aio.Future()
                def resolve(_=None, fut=future):
                    fut.set_result(True)
                if img.complete:
                    resolve()
                else:
                    img.onload = resolve
                futures.append(future)

            await aio.gather(*futures)
            enable_isotope()
            setup_programs_filter()
            await aio.sleep(0.05)
            window.AOS.init()
            window.AOS.refresh()

        aio.run(wait_and_initialize())

    else:
        window.AOS.init()
        window.AOS.refresh()


def flip_year_visibility(e):
    target = e.currentTarget
    data_type, _ = target.id.split("_selector_")
    is_flipped = target.classList.contains('flipped')
    fade_ins, fade_outs = [], []
    for el in document.querySelectorAll(f'[id^="{data_type}_selector_"]'):
        if el.id == target.id:
            continue
        if not el.classList.contains('visible'):
            if is_flipped:
                fade_outs.append(el)
            else:
                fade_ins.append(el)
    aio.run(selector_animation(fade_outs, fade_ins))
    if is_flipped:
        target.classList.remove('flipped')
    else:
        target.classList.add('flipped')
    msg = target.textContent
    target.textContent = target.dataset.pressedStr
    target.dataset.pressedStr = msg


async def selector_animation(fade_outs, fade_ins):
    size_fade_ins = [[] for _ in range(len(fade_ins))]
    size_fade_outs = [[] for _ in range(len(fade_outs))]
    for el, sz in zip(fade_ins, size_fade_ins):
        sz.append(float(window.getComputedStyle(el).opacity))
        el.style.opacity = "0"
        el.classList.remove('d-none')
        sz.append(el.getBoundingClientRect().width)
        sz.append(el.getBoundingClientRect().height)
        sz.append(float(window.getComputedStyle(el).fontSize.split('px')[0]))
        el.style.width = "0"
        el.style.height = "0"
        el.style.fontSize = "0px"

    for el, sz in zip(fade_outs, size_fade_outs):
        sz.append(float(window.getComputedStyle(el).opacity))
        sz.append(el.getBoundingClientRect().width)
        sz.append(el.getBoundingClientRect().height)
        sz.append(float(window.getComputedStyle(el).fontSize.split('px')[0]))

    for progress in range(100):
        value = progress / 100
        de_value = 1 - value
        for el, sz in zip(fade_ins, size_fade_ins):
            el.style.opacity = f"{sz[0]*value}"
            el.style.width = f"{sz[1]*value}px"
            el.style.height = f"{sz[2]*value}px"
            el.style.fontSize = f"{sz[3]*value*value}px"
        for el, sz in zip(fade_outs, size_fade_outs):
            el.style.opacity = f"{sz[0]*de_value}"
            el.style.width = f"{sz[1]*de_value}px"
            el.style.height = f"{sz[2]*de_value}px"
            el.style.fontSize = f"{sz[3]*de_value*de_value}px"
        await aio.sleep(0.00001)

    for el, sz in zip(fade_outs, size_fade_outs):
        el.classList.add('d-none')
        el.style.opacity = f"{sz[0]}"
        el.style.width = f"{sz[1]}px"
        el.style.height = f"{sz[2]}px"
        el.style.fontSize = f"{sz[3]}px"
    
    for el, sz in zip(fade_ins, size_fade_ins):
        el.style.opacity = f"{sz[0]}"
        el.style.width = f"{sz[1]}px"
        el.style.height = f"{sz[2]}px"
        el.style.fontSize = f"{sz[3]}px"


def adjust_selector_visibility(selected_year, data_type):
    all_selector = document.getElementById(f'{data_type}_selector_all')
    selected_selector = document.getElementById(f'{data_type}_selector_{selected_year}')
    is_flipped = all_selector.classList.contains('flipped')
    selectors = all_selector.parentNode.children
    selected_idx = selectors.index(selected_selector)
    selector_count = len(selectors) - 2
    
    # disable all selectors
    de_selection_list = []
    for el in selectors:
        if el.id == f"{data_type}_selector_all":
            continue  # skip the "all" selector
        el.classList.remove('active')
        if el.classList.contains('visible'):
            if not is_flipped:
                de_selection_list.append(el)
            el.classList.remove('visible')

    # enable the selected selector
    if not is_flipped:
        selected_selector.classList.remove('d-none')
    selected_selector.classList.add('visible')
    selected_selector.classList.add('active')
    selection_list = []
    if selected_idx == 0:
        selection_list = [selectors[1], selectors[2]]
    elif selected_idx == selector_count:
        selection_list = [selectors[selected_idx-2], selectors[selected_idx-1]]
    else:
        selection_list = [selectors[selected_idx-1], selectors[selected_idx+1]]
    for el in selection_list:
        el.classList.add('visible')

    if not is_flipped:
        fade_outs = [el for el in de_selection_list if el not in selection_list and el != selected_selector]
        fade_ins = [el for el in selection_list if el not in de_selection_list and el != selected_selector]
        aio.run(selector_animation(fade_outs, fade_ins))


def register_selector(container, year, data_type, visible, enabled, active):
    selector = document.createElement("a")
    selector.id = f"{data_type}_selector_{year}"
    selector.href = f"#{data_type}"
    selector.className = "selector btn rounded-pill scrollto"
    if active:
        selector.classList.add('active')
    if visible:
        selector.classList.add('visible')
    else:
        selector.classList.add('d-none')
    if not enabled:
        selector.classList.add('disabled')
    selector.textContent = str(year)
    selector.onclick = change_year_visibility
    container.prepend(selector)


team = document.getElementById('team')
if team:
    async def add_team_history():
        enabled = False
        container = team.getElementsByClassName('container')[0]
        selector_container = team.getElementsByClassName('selector-container')[0]

        document.getElementById('team_selector_all').onclick = flip_year_visibility

        for idx, year in enumerate(range(current_year+1, 2021, -1)):
            result = await window.fetch(f"/dist/res/templates/years/{year}/team.html")
            exists = result.status == 200
            active = False

            if exists:
                insert_element(await result.text(), container, -1)

                if not enabled:  # show only the first queried year
                    enabled = True
                    active = True
                    document.getElementById('team_'+str(year)).classList.remove('d-none')
                    scroll_to(window.location.hash)
                    window.AOS.init()
                    window.AOS.refresh()

            register_selector(selector_container, year, "team", idx < 3, exists, active)

    aio.run(add_team_history())


programs = document.getElementById('programs')
if programs:
    async def add_programs_history():
        enabled = False
        container = programs.getElementsByClassName('container')[0]
        selector_container = programs.getElementsByClassName('selector-container')[0]

        document.getElementById('programs_selector_all').onclick = flip_year_visibility

        for idx, year in enumerate(range(current_year+1, 2021, -1)):
            result = await window.fetch(f"/dist/res/templates/years/{year}/programs.html")
            exists = result.status == 200
            active = False

            if exists:
                insert_element(await result.text(), container, -1)

                if not enabled:  # show only the first queried year
                    enabled = True
                    active = True
                    document.getElementById('programs_'+str(year)).classList.remove('d-none')
                    images = document.select('img')

                    for img in images:
                        if not img.complete:
                            images.append(img)
                        await aio.sleep(0.001)

                    scroll_to(window.location.hash)
                    window.AOS.init()
                    window.AOS.refresh()
                    setup_programs_filter()

            register_selector(selector_container, year, "programs", idx < 3, exists, active)
            #TODO: Fix the selector visibility

    aio.run(add_programs_history())
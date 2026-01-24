import browser
from browser import document, window, aio

from datetime import datetime

current_year = datetime.now().year


def module_init(_id, module_name):
    import sys
    sys.modules[module_name] = sys.modules[_id]
    return window.console.log, print


print, pyprint = module_init(__name__, "common.main")
browser.__dict__['module_init'] = module_init


async def insert_template(template_path: str, parent, index: int = -1, oncomplete=lambda: None):
    result = await window.fetch("/dist/res/templates/"+template_path)
    insert_element(await result.text(), parent, index)
    oncomplete()


def insert_element(htmlstr: str, parent, index: int = -1):
    if parent.childNodes.length < index:
        index = parent.childNodes.length
    parent.insertBefore(parse_html(htmlstr.replace("{CURRENT_YEAR}", f"{current_year}")), parent.childNodes[index])


def parse_html(htmlstr: str):
    template = document.createElement('template')
    template.innerHTML = htmlstr
    return template.content


########################################################################################################################
# Navigation Bar
########################################################################################################################
def scroll_to(section: str):
    offset = document.getElementById('header').offsetHeight
    if section:
        section_element = document.getElementById(section.split('#')[-1])
        if section_element:
            pos = document.getElementById(section.split('#')[-1]).offsetTop
            window.scrollTo({'top': pos - offset, 'behavior': "smooth"})

def enable_navigation():
    navigation = document.getElementsByClassName('nav-link')
    navigation_menus = {nav.attributes['href'].value.split('#')[-1]: nav for nav in navigation}
    header = document.getElementById('header')
    navbar = document.getElementById('navbar')
    mobile_toggles = document.getElementsByClassName('mobile-nav-toggle')

    def navbar_click(event):
        # fix default location error
        event.preventDefault()
        window.location.href = event.target.hash

        # set mobile
        if 'navbar-mobile' in navbar.classList:
            navbar.classList.remove('navbar-mobile')
            mobile_toggles[0].classList.toggle('hidden')
            mobile_toggles[1].classList.toggle('hidden')

        # do scroll
        scroll_to(event.target.hash)

    def toggle_menu_icon(_):
        navbar.classList.toggle('navbar-mobile')
        mobile_toggles[0].classList.toggle('hidden')
        mobile_toggles[1].classList.toggle('hidden')

    def enable_mobile_dropdown(event):
        if 'navbar-mobile' in navbar.classList:
            event.preventDefault()
            event.target.nextElementSibling.classList.toggle('dropdown-active')

    def trace_current_scroll(_):
        pos = window.scrollY
        if pos > 100:
            header.classList.add('header-scrolled')
        else:
            header.classList.remove('header-scrolled')
        sections = document.getElementsByTagName('section')
        for sec in sections:
            menu = navigation_menus.get(sec.id, None)
            if menu:
                if sec.offsetTop <= pos+200 <= sec.offsetTop+sec.offsetHeight:
                    if 'active' not in menu.classList:
                        menu.classList.add('active')
                else:
                    if 'active' in menu.classList:
                        menu.classList.remove('active')

    scroll_to(window.location.hash)
    if window.location.pathname in ("/", "/index.html"):
        navigation_menus['front'].classList.add('active')  # set active menu
        for scrll in document.getElementsByClassName('scrollto'):
            scrll.onclick = navbar_click
    else:
        if not document.getElementById('disable_inner_page_header'):
            header.classList.add('header-inner-pages')
    trace_current_scroll(None)
    window.addEventListener('scroll', trace_current_scroll)
    for toggle in mobile_toggles:
        toggle.onclick = toggle_menu_icon

    contest = navbar.getElementsByClassName('contest')[0]
    contest.getElementsByTagName('a')[0].onclick = enable_mobile_dropdown
    for dropdown in contest.getElementsByClassName('dropdown'):
        dropdown.getElementsByTagName('a')[0].onclick = enable_mobile_dropdown


########################################################################################################################
# Back to Top
########################################################################################################################
def enable_back_to_top():
    back_to_top = document.getElementById('btn-back-to-top')

    def show_back_to_top_button(_):
        if back_to_top:
            if window.scrollY > 100:
                back_to_top.classList.add('active')
            else:
                back_to_top.classList.remove('active')

    show_back_to_top_button(None)
    window.addEventListener('scroll', show_back_to_top_button)
    add_to_home()


########################################################################################################################

def add_to_home():
    if 'org-logo-to-main-page' in document:
        def event_handler(_):
            window.location.href = "/"
        document['org-logo-to-main-page'].addEventListener('click', event_handler)


# Insert Templates
aio.run(insert_template("header.html", document.body, 0, enable_navigation))
aio.run(insert_template("footer.html", document.body, -1, enable_back_to_top))

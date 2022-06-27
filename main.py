import threading

import requests, time, json
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
import logging
from telegram import __version__ as TG_VER, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import pytz

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler

TOKEN = '5408622232:AAH9vIF0OX7d9s-z-moGt9f5sDkwmStV9NY'
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
timezone = pytz.timezone('Asia/Almaty')
START_ROUTES, END_ROUTES = range(2)
accounts = []
allowed_accounts_ids = []
disallowed_accounts_ids = []

url = 'https://pacan.mobi'
url_lobby = f'{url}/index.php?r=fightclub/lobby'
url_to_light = f'{url}/index.php?r=site/layout&layout=light&layout=light'
url_to_profile = f'{url}/index.php?r=profile&layout=mobile'

influence_safety_gap = 1000


def delay():
    time.sleep(5)


def first_fighter(session, account_id):
    tk_url = url + '/index.php?r=fights/hit&type=strength&token='
    tk_url2 = url + '/index.php?r=fights/hit&type=dexterity&token='
    tk_url3 = url + '/index.php?r=fights/hit&type=critical&token='

    def change_enemy(session):
        time.sleep(0.4)
        session.get(url + '/index.php?r=fights/choose&force=1&club=official')

    def get_wfactor_analys(msila, esila, mlovk, elovk, mkrit, ekrit):
        if msila > esila:
            swin = 1
        else:
            swin = 0
        if mlovk > elovk:
            lwin = 3
        else:
            lwin = 0
        if mkrit > ekrit:
            kwin = 5
        else:
            kwin = 0
        wcount = swin + lwin + kwin

        wfactor = 0
        if wcount <= 3:
            wfactor = 0
        # Это поражение
        elif wcount == 5:
            wfactor = 0
        # Это поражение
        elif wcount == 4:
            # Ты сильнее его и ловчее
            wfactor = 1
        elif wcount == 6:
            # Ты сильнее и критичнее
            wfactor = 2
        elif wcount == 8:
            # Ты ловчее и критичнее
            wfactor = 3
        elif wcount == 9:
            wfactor = 4

        return wfactor

    def sila(session):
        try:
            time.sleep(0.4)
            rival = session.get(url + '/index.php?r=fights/rival')
            soup = bs(rival.content, "lxml")
            tok = soup.find('a', attrs={'class': 'square-btn-green'})['href']
            token = tok[-32:]
            session.get(tk_url + token)

        except:
            pass

    def lovk(session):
        try:
            time.sleep(0.4)
            rival = session.get(url + '/index.php?r=fights/rival')
            soup = bs(rival.content, "lxml")
            tok = soup.find('a', attrs={'class': 'square-btn-green'})['href']
            token = tok[-32:]
            session.get(tk_url2 + token)

        except:
            pass

    def krit(session):
        try:
            time.sleep(0.4)
            rival = session.get(url + '/index.php?r=fights/rival')
            soup = bs(rival.content, "lxml")
            tok = soup.find('a', attrs={'class': 'square-btn-green'})['href']
            token = tok[-32:]
            session.get(tk_url3 + token)

        except:
            pass

    def print_enemy_nick(soup):
        try:
            nik = soup.find('div', class_='fight-head-name _minor')
            print(nik.text.strip())
        except:
            pass
        try:
            nik = soup.find('div', class_='fight-head-name _middle')
            print(nik.text.strip())
        except:
            pass
        try:
            nik = soup.find('div', slass_='fight-head-name _danger')
            print(nik.text.strip())
        except:
            pass

    def run_fighter(session):
        while True:
            isAllow = get_is_allow_to_underground()
            if account_id in allowed_accounts_ids and isAllow:
                time.sleep(0.4)
                try:
                    nik_list = ['_minor', '_middle', '_danger']
                    time.sleep(0.4)
                    rival = session.get(url + '/index.php?r=fights/choose&club=official')
                    soup = bs(rival.content, "lxml")
                    fight_back = soup.find('div', class_='fight-back')
                    fight_stats = fight_back.find_all('div', class_='fight-stat')
                    esila = int(fight_stats[0].text.strip())
                    elovk = int(fight_stats[1].text.strip())
                    ekrit = int(fight_stats[2].text.strip())
                    fight_controls = soup.find('div', class_='fight-controlls')
                    fight_stats2 = fight_controls.find_all('div', class_='fight-stat')
                    sil = int(fight_stats2[0].text.strip())
                    msila = sil + 5
                    mlovk = int(fight_stats2[1].text.strip())
                    mkrit = int(fight_stats2[2].text.strip())
                    print_enemy_nick(soup)

                except Exception as e:
                    print("ошибка получения статов", e)
                    continue
                wfactor = get_wfactor_analys(msila=msila, esila=esila, ekrit=ekrit, mkrit=mkrit, elovk=elovk,
                                             mlovk=mlovk)
                try:
                    if wfactor == 0:
                        # print("Он круче, выберем другого")
                        change_enemy(session)
                        continue

                    elif wfactor == 1:
                        # print("Ты сильнее и ловчее")
                        for i in range(1):
                            sila(session)
                            lovk(session)

                        continue

                    elif wfactor == 2:
                        # print("Ты сильнее и критичнее")
                        for i in range(1):
                            sila(session)
                            krit(session)

                        continue

                    elif wfactor == 3:
                        # print("Ты ловчее и критичнее")
                        for i in range(1):
                            lovk(session)
                            krit(session)

                        continue

                    elif wfactor == 4:
                        for i in range(1):
                            lovk(session)
                            krit(session)

                        continue
                except:
                    continue
            else:
                print('Нельзя в бой', account_id)
                delay()

    print('First bot started!')
    run_fighter(session)


def second_fighter(session, account_id):
    profile_url = '/index.php?r=profile'
    safe_url = '/index.php?r=property/safe&top=safe&cat=safe'

    def get_profile_soup(session):
        profile_page = session.get(url + profile_url)
        soup = bs(profile_page.content, "lxml")
        return soup

    def parse_docents_count(soup):
        docents_count = soup.find('img', attrs={'src': 'https://static.hata.mobi/i/icons/docents.png'}).find_parent(
            'span').get_text().strip()

        return docents_count

    def safe_controller(soup, session):
        try:
            docents_count = int(parse_docents_count(soup))
            print(docents_count)
            toSafe = 20
            if docents_count > 100:

                if docents_count > 200:
                    toSafe = 110
                elif docents_count > 300:
                    toSafe = 210
                safe_page = session.get(url + safe_url)
                soup = bs(safe_page.content, "lxml")
                try:
                    token = soup.find('input', attrs={'name': 'token'})['value']
                    data = {
                        'token': str(token),
                        'currency': 'money_r',
                        'amount': toSafe,
                        'put': ' ',
                    }
                    session.post(url + '/index.php?r=property/safe', data=data)
                except:
                    print('Stack Overflow')
                    time.sleep(1)
                    pass
            else:
                pass
        except:
            print('Stack Overflow')
            time.sleep(1)
            pass

    def energy_controller(soup, session):
        try:
            energy = soup.find('a', class_='btn-energy').text.split('/')
            en = int(energy[0])
            print(energy[0])
            if en < 25:
                session.get(url + '/index.php?r=fights/potions&potion_id=stol')
        except Exception as e:
            print('Что-то не вышло', e)

    def controller(session):
        soup = get_profile_soup(session)
        safe_controller(soup, session)
        energy_controller(soup, session)

    def fight(session):
        controller(session)
        for i in range(3):
            try:
                lovk = session.get(url + '/?r=fightclub/fight/hit&weapon=dexterity')
                sila = session.get(url + '/?r=fightclub/fight/hit&weapon=strength')
            except Exception as e:
                print(e)

    while True:
        isAllow = get_is_allow_to_underground()
        if account_id in allowed_accounts_ids and isAllow:
            fight(session)
        else:
            print('Нельзя ничего делать без разрешения', account_id)
            delay()


def check_auth():
    isHaveCookiesAndHeaders = True
    for x in accounts:
        name = x['login_data']['username']
        try:
            if x['cookies'] and x['headers']:
                print(f'[{name}] Есть куки и хедеры')
            else:
                print(f'[{name}] Нету куков и хедеров')
                isHaveCookiesAndHeaders = False
        except:
            isHaveCookiesAndHeaders = False
    if not isHaveCookiesAndHeaders:
        init_auth()


def read_accounts():
    global accounts
    try:
        with open('accounts.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            accounts = data['data']
            check_auth()
    except Exception as e:
        print('Нет файлов с аккаунтами', e)


def write_accounts():
    try:
        with open('accounts.json', 'w', encoding='utf-8') as json_file:
            data = {
                "data": accounts
            }
            json.dump(data, json_file, indent=4, separators=(',', ': '), sort_keys=True)
    except Exception as e:
        print('Нет файлов с аккаунтами', e)


def get_cookies_with_headers(username, password):
    temp_session = requests.Session()
    ua = UserAgent()
    ua_fake = ua.chrome
    temp_session.headers = {
        'user-agent': ua_fake
    }
    login_data = {
        'login': username,
        'password': password
    }
    temp_session.post(url + '/index.php?r=site/auth/', data=login_data)
    print('Зашел на', username)

    return temp_session.cookies.get_dict(), temp_session.headers


def init_auth():
    global accounts
    accounts_with_auth = accounts
    for idx, acc in enumerate(accounts_with_auth):
        cookies, headers = get_cookies_with_headers(acc['login_data']['username'],
                                                    acc['login_data']['password'])
        accounts_with_auth[idx] = {
            **acc,
            "cookies": cookies,
            "headers": headers,
        }

    print('Готово. Теперь запишем!')
    accounts = accounts_with_auth
    write_accounts()


def get_soup(session, url_to_parse):
    page = session.get(url_to_parse)
    return bs(page.content, "lxml")


def make_session(account_id):
    user = requests.Session()
    for acc in accounts:
        if acc["account_id"] == account_id:
            user.headers.update(acc['headers'])
            user.cookies.update(acc['cookies'])
            return user
    return user


def make_session_light(account_id):
    user = requests.Session()
    for acc in accounts:
        if acc["account_id"] == account_id:
            user.headers.update(acc['headers'])
            cookies = {
                **acc['cookies'],
                "layout": "light"
            }

            user.cookies.update(cookies)
            return user
    return user


def get_current_hour():
    current_time = datetime.now(timezone)
    hour = current_time.hour
    print('hour is', hour)
    return hour


def get_is_allow_to_underground():
    hour = get_current_hour()
    allowed_hours = [13, 14, 19, 20, 23, 0]
    deep_sleep_hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    if hour in deep_sleep_hours:
        print('I will sleep 3600 sec')
        time.sleep(3600)
    if hour in allowed_hours:
        return True
    else:
        print('Не подпольское время')
        return False


def controller_underground(session, idx):
    while True:
        result = check_underground(session)
        # print('allowed accounts', allowed_accounts_ids)
        print(f'\n{result}\n')
        if idx in allowed_accounts_ids:
            print('Аккаунт разрешен к бою')
            # Аккаунт разрешен к бою
            # Проверить в подполе ли он
            # Если да то все оки доки
            # Если нет то завести

            is_in_underground = result['isInUnderground']
            url_to_enter = result['urlToEnter']
            if is_in_underground is False and url_to_enter:
                url_got = url + str(url_to_enter)
                print('Вошли в подпол по ссылке: ', url_got)
                session.get(url_got)
        else:
            print('Аккаунт запрещен к бою')
            # Аккаунт запрещен к бою
            # Проверить в подполе ли он
            # Если да то вывести из подпола
            # Если нет то все отлично!
            is_in_underground = result['isInUnderground']
            url_to_leave = result['urlToLeave']
            if is_in_underground:
                print('Попытка свалить')
                url_got = url + str(url_to_leave)
                print('Вышли из подпола по ссылке: ', url_got)
                session.get(url_got)
        time.sleep(5)


def controller_influence():
    cookies, headers = get_cookies_with_headers("коровавирус6", "7evilgrad7")
    influences_session = requests.session()
    influences_session.headers.update(headers)
    influences_session.cookies.update(cookies)
    while True:
        if get_is_allow_to_underground():
            soup = get_soup(influences_session, url_lobby)
            member_links = soup.find_all('a', class_='g_member_link')
            for link in member_links:
                idx_on_list = link['href'].split('id=')[1]
                place = int(link.find_parent('tr').find('td', attrs={"width": "10%"}).get_text().strip())
                # Мы узнали ID Всех участниклов и их места тепрерь если наш ник нейм в топе то выкинем его из подпола
                if idx_on_list in allowed_accounts_ids:
                    # Нужно проверить не вошел ли он в топ
                    if place <= 5:
                        # Наш дружок вошел в подпол!
                        for idx, val in enumerate(allowed_accounts_ids):
                            if val == idx_on_list:
                                allowed_accounts_ids.pop(idx)
                                print('Выключили из подпола.')
                else:
                    # Пройтись по аккаунтам которые выключены и посмотреть их место в топе уже от их лица.
                    for acc in accounts:
                        temp_session = make_session(acc['account_id'])
                        soup = get_soup(temp_session, url_lobby)
                        member_links = soup.find_all('a', class_='g_member_link')
                        last_member_influence = 0
                        for place_id, _link in enumerate(member_links):
                            is_current = bool(_link.find_parent('b'))
                            place = int(_link.find_parent('tr').find('td', attrs={"width": "10%"}).get_text().strip())
                            influence = int(
                                _link.find_parent('tr').find('td', attrs={"width": "25%"}).get_text().strip())
                            if place == 5:
                                last_member_influence = influence

                            if is_current:
                                if (last_member_influence - influence_safety_gap) >= influence:
                                    # Значит что нам нужно зайти обратно в подпол
                                    allowed_accounts_ids.append(acc['account_id'])
                        temp_session.close()
        else:
            print('Не подпольное время спим (проверка влияния)')
            delay()


def start_program():
    for acc in accounts:
        idx = acc['account_id']
        user = make_session(idx)
        user_light = make_session_light(idx)
        threading.Thread(target=controller_underground, args=(user, idx,)).start()
        threading.Thread(target=first_fighter, args=(user_light, idx,)).start()
        threading.Thread(target=second_fighter, args=(user, idx,)).start()

    threading.Thread(target=controller_influence)


def check_underground(session):
    result_data = {
        'isInUnderground': False,
        'urlToEnter': '',
        'urlToLeave': '',
    }
    exit_text = 'Свалить с подпольного ринга'
    soup = get_soup(session, url_lobby)
    vip_button = soup.find('a', class_='bttn vip')
    vip_button_locked = soup.find('span', class_='bttn vip locked')
    if vip_button_locked:
        # print('Есть кнопка подпола закрытого')
        result_data = {
            **result_data,
            'isInUnderground': False,
        }
        return result_data
    if vip_button:
        # print('Есть кнопка подпола')
        url_got = vip_button['href']
        print(url_got)
        result_data = {
            **result_data,
            'isInUnderground': False,
            'urlToEnter': url_got
        }
        return result_data
    else:
        red_buttons = soup.find_all('a', class_='bttn_red')
        for button in red_buttons:
            if button.get_text() == exit_text:
                print('Мы в подполе')
                url_got = button['href']
                result_data = {
                    **result_data,
                    'isInUnderground': True,
                    'urlToLeave': url_got
                }
                return result_data


def get_nick_by_account_id(account_id):
    user = make_session(account_id)
    soup = get_soup(user, url_to_profile)
    nick_raw = soup.find('div', class_='content_profile_title')
    if nick_raw:
        nick = nick_raw.get_text().strip().split('ур.')[0]
        return nick
    else:
        return account_id


async def on_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    PLUS = '+'
    command = update.message.text
    answer_text = '🚀'
    on_commands = [PLUS]
    off_commands = ['-']
    if command in on_commands:
        allowed_accounts_ids.clear()
        for x in accounts:
            acc_id = x['account_id']
            if acc_id not in disallowed_accounts_ids:
                allowed_accounts_ids.append(acc_id)
        answer_text += 'Все аккаунты [кроме выключенных] включены.'
    if command in off_commands:
        allowed_accounts_ids.clear()
        answer_text += 'Все аккаунты выключены.'

    if command[0] == PLUS and len(command) > 1:
        try:
            account_numbers = int(command[1])
            # Включить N значение аккаунтов
            allowed_accounts_ids.clear()
            for idx, value in enumerate(accounts):
                if idx + 1 >= account_numbers:
                    break
                else:
                    allowed_accounts_ids.append(value['account_id'])
            answer_text += f'{account_numbers} - акк включены в бой.'
        except Exception as e:
            answer_text += f'{e}'

    await update.message.reply_text(answer_text)


def telegram_bot_init():
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_html(
            rf"Привет. Я Йор. Контролирую движения в подполе!",
            reply_markup=ForceReply(selective=True),
        )

    def ban(account_id):
        for x in disallowed_accounts_ids:
            if x == account_id:
                return False
        disallowed_accounts_ids.append(account_id)
        allowed_accounts_ids.clear()
        for x in accounts:
            acc_id = x['account_id']
            if acc_id not in disallowed_accounts_ids:
                allowed_accounts_ids.append(acc_id)
        return True

    async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        accounts_list = []
        for acc in accounts:
            acc_id = acc["account_id"]
            username = acc["login_data"]["username"]
            badge = ''
            if acc_id in allowed_accounts_ids:
                badge += '🟢'
            else:
                badge += '🔴'
            if acc_id in disallowed_accounts_ids:
                badge += '☠'

            accounts_list.append(f'{username} {badge}')
        accounts_list_one_string = '\n'.join(map(str, accounts_list))
        print(accounts_list_one_string)
        await update.message.reply_text(f"Информация по аккаунтам: \n{accounts_list_one_string}\n")

    async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Returns `ConversationHandler.END`, which tells the
        ConversationHandler that the conversation is over.
        """
        query = update.callback_query
        await query.answer()
        isBanned = ban(query.data)
        if isBanned:
            await query.edit_message_text(text=f"Вырубаем {query.data}!")
        else:
            await query.edit_message_text(text=f"Уже вырублен {query.data}!")
        return ConversationHandler.END

    async def off_some_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.message.from_user
        logger.info("User %s started the conversation off_some_one.", user.first_name)
        keyboard = [
        ]
        for x in accounts:
            nick = get_nick_by_account_id(x['account_id'])
            keyboard.append(InlineKeyboardButton(nick, callback_data=x['account_id']))
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выбирай, Кого вырубаем?", reply_markup=reply_markup)
        return START_ROUTES

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("list", off_some_one)],
        fallbacks=[CommandHandler("list", off_some_one)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(end),
            ],
        },
    )

    application = Application.builder().token(TOKEN).build()
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", get_info))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_off))
    application.run_polling()


def main():
    read_accounts()
    start_program()
    telegram_bot_init()


if __name__ == '__main__':
    main()

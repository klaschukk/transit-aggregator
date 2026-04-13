"""
Simple i18n system for Prevozni.

Usage in templates:  {{ _('nav.all_routes') }}
Usage in Python:     from app.i18n import get_text; get_text('nav.all_routes', 'en')

Supported languages: sr (default), en, ru
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Navigation ──
    'nav.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },
    'nav.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'nav.search': {
        'sr': 'Pretraga',
        'en': 'Search',
        'ru': 'Поиск',
    },
    'nav.menu': {
        'sr': 'Meni',
        'en': 'Menu',
        'ru': 'Меню',
    },

    # ── Footer ──
    'footer.desc': {
        'sr': 'Red vožnje autobusa, tramvaja i vozova u Srbiji. Besplatno, bez registracije.',
        'en': 'Bus, tram and train schedules in Serbia. Free, no registration.',
        'ru': 'Расписание автобусов, трамваев и поездов в Сербии. Бесплатно, без регистрации.',
    },
    'footer.navigation': {
        'sr': 'Navigacija',
        'en': 'Navigation',
        'ru': 'Навигация',
    },
    'footer.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
    },
    'footer.cities': {
        'sr': 'Gradovi',
        'en': 'Cities',
        'ru': 'Города',
    },
    'footer.carriers': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'footer.stations': {
        'sr': 'Stanice',
        'en': 'Stations',
        'ru': 'Станции',
    },
    'footer.about': {
        'sr': 'O nama',
        'en': 'About us',
        'ru': 'О нас',
    },
    'footer.contact': {
        'sr': 'Kontakt',
        'en': 'Contact',
        'ru': 'Контакт',
    },
    'footer.copyright': {
        'sr': 'Sva prava zadržana.',
        'en': 'All rights reserved.',
        'ru': 'Все права защищены.',
    },
    'footer.privacy': {
        'sr': 'Privatnost',
        'en': 'Privacy',
        'ru': 'Конфиденциальность',
    },
    'privacy.title': {
        'sr': 'Politika privatnosti',
        'en': 'Privacy Policy',
        'ru': 'Политика конфиденциальности',
    },
    'privacy.intro': {
        'sr': 'Prevozni poštuje vašu privatnost. Ova stranica objašnjava koje podatke prikupljamo i kako ih koristimo.',
        'en': 'Prevozni respects your privacy. This page explains what data we collect and how we use it.',
        'ru': 'Prevozni уважает вашу конфиденциальность. Здесь описано, какие данные мы собираем и как используем.',
    },
    'privacy.cookies_h': {
        'sr': 'Kolačići',
        'en': 'Cookies',
        'ru': 'Cookies',
    },
    'privacy.cookies_body': {
        'sr': 'Koristimo samo neophodne kolačiće (npr. CSRF token). Ne koristimo reklamne niti praćeće kolačiće trećih strana.',
        'en': 'We use only essential cookies (e.g. CSRF token). No third-party advertising or tracking cookies.',
        'ru': 'Мы используем только необходимые cookies (например, CSRF-токен). Никаких рекламных или трекинговых cookies третьих сторон.',
    },
    'privacy.analytics_h': {
        'sr': 'Analitika',
        'en': 'Analytics',
        'ru': 'Аналитика',
    },
    'privacy.analytics_body': {
        'sr': 'Koristimo Umami analitiku — anonimne, agregirane statistike poseta bez kolačića i bez praćenja pojedinaca.',
        'en': 'We use Umami analytics — anonymous, aggregated page view statistics with no cookies and no individual tracking.',
        'ru': 'Мы используем Umami — анонимную агрегированную статистику посещений без cookies и отслеживания пользователей.',
    },
    'privacy.contact_h': {
        'sr': 'Kontakt forma',
        'en': 'Contact form',
        'ru': 'Контактная форма',
    },
    'privacy.contact_body': {
        'sr': 'Poruke iz kontakt forme se šalju preko Telegram bota i čuvaju u logovima radi odgovora. Ne delimo ih sa trećim stranama.',
        'en': 'Messages from the contact form are sent via a Telegram bot and stored in logs so we can reply. They are not shared with third parties.',
        'ru': 'Сообщения из контактной формы отправляются через Telegram-бот и сохраняются в логах для ответа. Третьим лицам не передаются.',
    },
    'privacy.rights_h': {
        'sr': 'Vaša prava (GDPR)',
        'en': 'Your rights (GDPR)',
        'ru': 'Ваши права (GDPR)',
    },
    'privacy.rights_body': {
        'sr': 'Imate pravo pristupa, ispravke i brisanja podataka. Za zahteve pišite na info@prevozni.com.',
        'en': 'You have the right to access, rectify and erase your data. Email info@prevozni.com for requests.',
        'ru': 'Вы имеете право на доступ, исправление и удаление данных. Запросы — на info@prevozni.com.',
    },
    'footer.disclaimer': {
        'sr': 'Podaci su informativnog karaktera i preuzeti iz javno dostupnih izvora. Prevozni ne garantuje tačnost podataka — uvek proverite red vožnje direktno kod prevoznika. Ovaj sajt ne prodaje karte niti posreduje u prodaji prevoznih usluga.',
        'en': 'Data is for informational purposes and sourced from publicly available sources. Prevozni does not guarantee data accuracy — always check the schedule directly with the carrier. This site does not sell tickets.',
        'ru': 'Данные носят информационный характер и получены из открытых источников. Prevozni не гарантирует точность данных — всегда проверяйте расписание у перевозчика. Сайт не продает билеты.',
    },

    # ── Homepage ──
    'home.title': {
        'sr': 'Prevozni — red vožnje autobusa, vozova i gradskog prevoza',
        'en': 'Prevozni — bus, train and city transport schedules in Serbia',
        'ru': 'Prevozni — расписание автобусов, поездов и городского транспорта в Сербии',
    },
    'home.hero_title': {
        'sr': 'Red vožnje u Srbiji',
        'en': 'Transport schedules in Serbia',
        'ru': 'Расписание транспорта в Сербии',
    },
    'home.hero_subtitle': {
        'sr': 'Pronađite autobus, voz ili gradski prevoz na jednom mestu',
        'en': 'Find bus, train or city transport in one place',
        'ru': 'Найдите автобус, поезд или городской транспорт в одном месте',
    },
    'home.search_from': {
        'sr': 'Odakle?',
        'en': 'From?',
        'ru': 'Откуда?',
    },
    'home.search_to': {
        'sr': 'Dokle?',
        'en': 'To?',
        'ru': 'Куда?',
    },
    'home.search_btn': {
        'sr': 'Pretraži',
        'en': 'Search',
        'ru': 'Найти',
    },
    'home.popular_routes': {
        'sr': 'Popularne rute',
        'en': 'Popular routes',
        'ru': 'Популярные маршруты',
    },
    'home.city_transport': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'home.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },

    # ── Common ──
    'common.departure': {
        'sr': 'Polazak',
        'en': 'Departure',
        'ru': 'Отправление',
    },
    'common.arrival': {
        'sr': 'Dolazak',
        'en': 'Arrival',
        'ru': 'Прибытие',
    },
    'common.duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Время в пути',
    },
    'common.price': {
        'sr': 'Cena',
        'en': 'Price',
        'ru': 'Цена',
    },
    'common.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
    },
    'common.daily': {
        'sr': 'dnevno',
        'en': 'daily',
        'ru': 'ежедневно',
    },
    'common.lines': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'common.stops': {
        'sr': 'stajališta',
        'en': 'stops',
        'ru': 'остановок',
    },
    'common.routes': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'common.show_more': {
        'sr': 'Prikaži još',
        'en': 'Show more',
        'ru': 'Показать ещё',
    },
    'common.now': {
        'sr': 'sada',
        'en': 'now',
        'ru': 'сейчас',
    },
    'common.min': {
        'sr': 'min',
        'en': 'min',
        'ru': 'мин',
    },
    'common.map_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
    },

    # ── Routes page ──
    'routes.title': {
        'sr': 'Sve autobuske i vozne rute u Srbiji',
        'en': 'All bus and train routes in Serbia',
        'ru': 'Все автобусные и железнодорожные маршруты Сербии',
    },
    'routes.departures': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'рейсов',
    },

    # ── City transport ──
    'city.schedule': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
    },
    'city.stop': {
        'sr': 'Stajalište',
        'en': 'Stop',
        'ru': 'Остановка',
    },
    'city.line': {
        'sr': 'Linija',
        'en': 'Line',
        'ru': 'Линия',
    },
    'city.next_departures': {
        'sr': 'Sledeći polasci',
        'en': 'Next departures',
        'ru': 'Ближайшие отправления',
    },
    'city.no_data': {
        'sr': 'Nema podataka o linijama',
        'en': 'No line data available',
        'ru': 'Нет данных о линиях',
    },

    # ── How it works ──
    'how.title': {
        'sr': 'Kako radi?',
        'en': 'How it works',
        'ru': 'Как это работает',
    },
    'how.step1': {
        'sr': 'Pretražite',
        'en': 'Search',
        'ru': 'Найдите',
    },
    'how.step1_desc': {
        'sr': 'Unesite odakle i kuda putujete',
        'en': 'Enter your origin and destination',
        'ru': 'Введите откуда и куда едете',
    },
    'how.step2': {
        'sr': 'Uporedite',
        'en': 'Compare',
        'ru': 'Сравните',
    },
    'how.step2_desc': {
        'sr': 'Vreme polaska, cene i prevoznici',
        'en': 'Departure times, prices and carriers',
        'ru': 'Время отправления, цены и перевозчики',
    },
    'how.step3': {
        'sr': 'Putujte',
        'en': 'Travel',
        'ru': 'Путешествуйте',
    },
    'how.step3_desc': {
        'sr': 'Tačan red vožnje, bez registracije',
        'en': 'Accurate schedules, no registration',
        'ru': 'Точное расписание, без регистрации',
    },

    # ── Benefits section ──
    'benefits.free': {
        'sr': '100% besplatno',
        'en': '100% free',
        'ru': '100% бесплатно',
    },
    'benefits.free_desc': {
        'sr': 'Bez registracije, bez skrivenih troškova',
        'en': 'No registration, no hidden fees',
        'ru': 'Без регистрации, без скрытых платежей',
    },
    'benefits.mobile': {
        'sr': 'Mobilni pristup',
        'en': 'Mobile friendly',
        'ru': 'Для мобильных',
    },
    'benefits.mobile_desc': {
        'sr': 'Optimizovano za telefon i tablet',
        'en': 'Optimized for phone and tablet',
        'ru': 'Оптимизировано для телефона и планшета',
    },
    'benefits.realtime': {
        'sr': 'Aktuelni podaci',
        'en': 'Up-to-date data',
        'ru': 'Актуальные данные',
    },
    'benefits.realtime_desc': {
        'sr': 'Redovno ažurirani redovi vožnje',
        'en': 'Regularly updated schedules',
        'ru': 'Регулярно обновляемое расписание',
    },
    'benefits.allinone': {
        'sr': 'Sve na jednom mestu',
        'en': 'All in one place',
        'ru': 'Всё в одном месте',
    },
    'benefits.allinone_desc': {
        'sr': 'Autobus, voz, tramvaj — cela Srbija',
        'en': 'Bus, train, tram — all of Serbia',
        'ru': 'Автобус, поезд, трамвай — вся Сербия',
    },

    # ── City transport page ──
    'city.title': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'city.lines_count': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'city.stops_on_map': {
        'sr': 'stajališta na mapi',
        'en': 'stops on map',
        'ru': 'остановок на карте',
    },
    'city.popular_stops': {
        'sr': 'Popularna stajališta',
        'en': 'Popular stops',
        'ru': 'Популярные остановки',
    },
    'city.intercity': {
        'sr': 'Međugradski prevoz',
        'en': 'Intercity transport',
        'ru': 'Междугородний транспорт',
    },
    'city.all_intercity': {
        'sr': 'Sve međugradske rute',
        'en': 'All intercity routes',
        'ru': 'Все междугородние маршруты',
    },
    'city.bus_train_from': {
        'sr': 'Autobus i voz iz',
        'en': 'Bus and train from',
        'ru': 'Автобус и поезд из',
    },
    'city.departures_from': {
        'sr': 'Polasci iz',
        'en': 'Departures from',
        'ru': 'Отправления из',
    },
    'city.search_dest': {
        'sr': 'Pretraži destinacije',
        'en': 'Search destinations',
        'ru': 'Поиск направлений',
    },
    'city.eta_note': {
        'sr': 'Vreme dolaska na mapi je procena prema rasporedu. Moguća su odstupanja.',
        'en': 'Arrival times on the map are estimates based on the schedule. Deviations are possible.',
        'ru': 'Время прибытия на карте — оценка по расписанию. Возможны отклонения.',
    },
    'city.search_line': {
        'sr': 'Broj linije ili naziv...',
        'en': 'Line number or name...',
        'ru': 'Номер линии или название...',
    },
    'city.all': {
        'sr': 'Sve',
        'en': 'All',
        'ru': 'Все',
    },
    'city.tram': {
        'sr': 'Tramvaj',
        'en': 'Tram',
        'ru': 'Трамвай',
    },
    'city.trolleybus': {
        'sr': 'Trolejbus',
        'en': 'Trolleybus',
        'ru': 'Троллейбус',
    },
    'city.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
    },
    'city.night': {
        'sr': 'Noćne linije',
        'en': 'Night lines',
        'ru': 'Ночные линии',
    },

    # ── Breadcrumbs ──
    'breadcrumb.home': {
        'sr': 'Početna',
        'en': 'Home',
        'ru': 'Главная',
    },

    # ── Contact page ──
    'contact.title': {'sr': 'Kontakt', 'en': 'Contact', 'ru': 'Контакт'},
    'contact.subtitle': {
        'sr': 'Imate pitanje, sugestiju ili ste primetili grešku?',
        'en': 'Have a question, suggestion, or found an error?',
        'ru': 'Есть вопрос, предложение или нашли ошибку?',
    },
    'contact.name': {'sr': 'Ime', 'en': 'Name', 'ru': 'Имя'},
    'contact.name_ph': {'sr': 'Vaše ime', 'en': 'Your name', 'ru': 'Ваше имя'},
    'contact.email': {'sr': 'Email', 'en': 'Email', 'ru': 'Email'},
    'contact.message': {'sr': 'Poruka', 'en': 'Message', 'ru': 'Сообщение'},
    'contact.message_ph': {
        'sr': 'Opišite vaše pitanje ili sugestiju...',
        'en': 'Describe your question or suggestion...',
        'ru': 'Опишите ваш вопрос или предложение...',
    },
    'contact.send': {'sr': 'Pošalji', 'en': 'Send', 'ru': 'Отправить'},
    'contact.response_time': {
        'sr': 'Odgovaramo u roku od',
        'en': 'We respond within',
        'ru': 'Отвечаем в течение',
    },
    'contact.hours': {'sr': '24 sata', 'en': '24 hours', 'ru': '24 часов'},
    'contact.sent_ok': {
        'sr': 'Poruka je poslata. Hvala!',
        'en': 'Message sent. Thanks!',
        'ru': 'Сообщение отправлено. Спасибо!',
    },
    'contact.error.required': {
        'sr': 'Molimo popunite sva polja.',
        'en': 'Please fill in all fields.',
        'ru': 'Пожалуйста, заполните все поля.',
    },
    'contact.error.name_too_long': {
        'sr': 'Ime je predugačko (maksimum 100 karaktera).',
        'en': 'Name is too long (max 100 characters).',
        'ru': 'Имя слишком длинное (максимум 100 символов).',
    },
    'contact.error.email_invalid': {
        'sr': 'Email adresa nije ispravna.',
        'en': 'Email address is not valid.',
        'ru': 'Некорректный email адрес.',
    },
    'contact.error.message_too_long': {
        'sr': 'Poruka je predugačka (maksimum 500 karaktera).',
        'en': 'Message is too long (max 500 characters).',
        'ru': 'Сообщение слишком длинное (максимум 500 символов).',
    },

    # ── About page ──
    'about.title': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас'},
    'about.mission': {
        'sr': 'Prevozni prikuplja i objedinjuje podatke iz različitih izvora kako bi vam uštedeo vreme pri planiranju putovanja kroz Srbiju.',
        'en': 'Prevozni collects and aggregates data from various sources to save you time when planning travel through Serbia.',
        'ru': 'Prevozni собирает и объединяет данные из различных источников, чтобы сэкономить ваше время при планировании поездок по Сербии.',
    },
    'about.disclaimer_title': {'sr': 'Napomena', 'en': 'Disclaimer', 'ru': 'Примечание'},
    'about.disclaimer': {
        'sr': 'Ovaj sajt prikuplja podatke iz javno dostupnih izvora i ne garantuje njihovu tačnost. Pre putovanja obavezno proverite red vožnje direktno kod prevoznika pre putovanja. Prevozni ne prodaje karte niti posreduje u prodaji prevoznih usluga.',
        'en': 'This site collects data from publicly available sources and does not guarantee its accuracy. Always check the schedule directly with the carrier before traveling. Prevozni does not sell tickets.',
        'ru': 'Сайт собирает данные из открытых источников и не гарантирует их точность. Перед поездкой обязательно проверяйте расписание у перевозчика. Prevozni не продает билеты.',
    },

    # ── See also / shared sections ──
    'see_also.title': {'sr': 'Pogledajte još', 'en': 'See also', 'ru': 'Смотрите также'},
    'see_also.all_routes': {'sr': 'Sve međugradske rute', 'en': 'All intercity routes', 'ru': 'Все междугородние маршруты'},
    'see_also.all_routes_desc': {
        'sr': 'Autobus i voz između gradova Srbije',
        'en': 'Bus and train between Serbian cities',
        'ru': 'Автобус и поезд между городами Сербии',
    },
    'see_also.city_beograd': {'sr': 'Gradski prevoz Beograd', 'en': 'Belgrade city transport', 'ru': 'Городской транспорт Белград'},
    'see_also.city_desc': {'sr': 'Linije, stajališta, mapa', 'en': 'Lines, stops, map', 'ru': 'Линии, остановки, карта'},
    'see_also.about': {'sr': 'O nama', 'en': 'About us', 'ru': 'О нас'},
    'see_also.about_desc': {'sr': 'Misija i izvori podataka', 'en': 'Mission and data sources', 'ru': 'Миссия и источники данных'},

    # ── Route pages ──
    'route.schedule': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание'},
    'route.reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See the reverse direction',
        'ru': 'Смотрите обратное направление',
    },

    # ── Search results ──
    'search.title': {'sr': 'Pretraga', 'en': 'Search', 'ru': 'Поиск'},
    'search.results_for': {'sr': 'Rezultati pretrage', 'en': 'Search results', 'ru': 'Результаты поиска'},
    'search.no_results': {'sr': 'Nema rezultata', 'en': 'No results', 'ru': 'Нет результатов'},

    # ── Error pages ──
    'error.404_title': {'sr': 'Stranica nije pronađena', 'en': 'Page not found', 'ru': 'Страница не найдена'},
    'error.404_text': {
        'sr': 'Stranica koju tražite ne postoji ili je uklonjena.',
        'en': 'The page you are looking for does not exist or has been removed.',
        'ru': 'Страница, которую вы ищете, не существует или была удалена.',
    },
    'error.500_title': {'sr': 'Došlo je do greške', 'en': 'Something went wrong', 'ru': 'Произошла ошибка'},
    'error.500_text': {
        'sr': 'Pokušajte ponovo ili se vratite na početnu',
        'en': 'Try again or go back to the homepage',
        'ru': 'Попробуйте снова или вернитесь на главную',
    },

    # ── Carriers page ──
    'carriers.title': {'sr': 'Prevoznici u Srbiji', 'en': 'Carriers in Serbia', 'ru': 'Перевозчики Сербии'},
    'carriers.bus': {'sr': 'Autobuski prevoznici', 'en': 'Bus carriers', 'ru': 'Автобусные перевозчики'},
    'carriers.train': {'sr': 'Železnički prevoznici', 'en': 'Train carriers', 'ru': 'Железнодорожные перевозчики'},

    # ── Stations page ──
    'stations.title': {'sr': 'Autobuske i železničke stanice', 'en': 'Bus and train stations', 'ru': 'Автобусные и ж/д станции'},

    # ── Line detail ──
    'line.stops': {'sr': 'stajališta', 'en': 'stops', 'ru': 'остановок'},
    'line.direction_a': {'sr': 'Smer A', 'en': 'Direction A', 'ru': 'Направление А'},
    'line.direction_b': {'sr': 'Smer B', 'en': 'Direction B', 'ru': 'Направление Б'},
    'line.first_departure': {'sr': 'Prvi polazak', 'en': 'First departure', 'ru': 'Первый рейс'},
    'line.last_departure': {'sr': 'Poslednji polazak', 'en': 'Last departure', 'ru': 'Последний рейс'},

    # ── Stop detail ──
    'stop.lines_here': {'sr': 'Linije na ovom stajalištu', 'en': 'Lines at this stop', 'ru': 'Линии на этой остановке'},
    'stop.next_arrivals': {'sr': 'Sledeći polasci', 'en': 'Next departures', 'ru': 'Ближайшие отправления'},

    # ── Route detail / search ──
    'route.daily_departures': {'sr': 'polazaka dnevno', 'en': 'departures daily', 'ru': 'рейсов в день'},
    'route.per_day': {'sr': 'polazaka/dan', 'en': 'departures/day', 'ru': 'рейсов/день'},
    'route.shown_of': {'sr': 'Prikazano', 'en': 'Shown', 'ru': 'Показано'},
    'route.of': {'sr': 'od', 'en': 'of', 'ru': 'из'},
    'route.km': {'sr': 'km', 'en': 'km', 'ru': 'км'},
    'route.from_price': {'sr': 'od', 'en': 'from', 'ru': 'от'},
    'route.see_reverse': {
        'sr': 'Pogledajte i obrnuti smer',
        'en': 'See also the reverse direction',
        'ru': 'Смотрите также обратное направление',
    },
    'route.all_routes': {'sr': 'Sve rute', 'en': 'All routes', 'ru': 'Все маршруты'},
    'route.filter_all': {'sr': 'Svi polasci', 'en': 'All departures', 'ru': 'Все рейсы'},
    'route.workday': {'sr': 'Radnim danom', 'en': 'Weekdays', 'ru': 'Будни'},
    'route.weekend': {'sr': 'Vikend', 'en': 'Weekend', 'ru': 'Выходные'},

    # ── Search page ──
    'search.departures_found': {'sr': 'polazaka', 'en': 'departures', 'ru': 'рейсов'},
    'search.no_results_text': {
        'sr': 'Nismo pronašli direktne polaske za ovaj pravac.',
        'en': 'No direct departures found for this route.',
        'ru': 'Прямых рейсов по этому маршруту не найдено.',
    },

    # ── Line detail ──
    'line.timeline': {'sr': 'Trasa linije', 'en': 'Line route', 'ru': 'Маршрут линии'},
    'line.schedule_title': {'sr': 'Red vožnje', 'en': 'Schedule', 'ru': 'Расписание'},
    'line.departures_from': {'sr': 'Polasci od', 'en': 'Departures from', 'ru': 'Отправление от'},

    # ── Stop detail ──
    'stop.title': {'sr': 'Stajalište', 'en': 'Stop', 'ru': 'Остановка'},
    'stop.on_map': {'sr': 'na mapi', 'en': 'on map', 'ru': 'на карте'},
    'stop.nearby': {'sr': 'Obližnja stajališta', 'en': 'Nearby stops', 'ru': 'Ближайшие остановки'},

    # ── City index ──
    'city_index.title': {
        'sr': 'Gradski prevoz u Srbiji',
        'en': 'City transport in Serbia',
        'ru': 'Городской транспорт Сербии',
    },

    # ── Carriers / Stations ──
    'carriers.routes_count': {'sr': 'ruta', 'en': 'routes', 'ru': 'маршрутов'},
    'carriers.website': {'sr': 'Sajt', 'en': 'Website', 'ru': 'Сайт'},
    'stations.train': {'sr': 'Železničke stanice', 'en': 'Train stations', 'ru': 'Ж/д станции'},

    # ── Buy ticket ──
    'buy.title': {
        'sr': 'Kupite kartu online',
        'en': 'Buy ticket online',
        'ru': 'Купить билет онлайн',
    },
    'buy.note': {
        'sr': 'Kupovina se obavlja na sajtovima partnera. Prevozni ne prodaje karte.',
        'en': 'Purchase is made on partner websites. Prevozni does not sell tickets.',
        'ru': 'Покупка на сайтах партнёров. Prevozni не продаёт билеты.',
    },

    # ── Day labels ──
    'day.today': {'sr': 'Danas', 'en': 'Today', 'ru': 'Сегодня'},
    'day.tomorrow': {'sr': 'Sutra', 'en': 'Tomorrow', 'ru': 'Завтра'},
    'day.day_after': {'sr': 'Prekosutra', 'en': 'Day after', 'ru': 'Послезавтра'},

    'route.similar': {'sr': 'Slične rute iz', 'en': 'Similar routes from', 'ru': 'Похожие маршруты из'},
    'route.about': {'sr': 'O ruti', 'en': 'About route', 'ru': 'О маршруте'},

    # ── Destinations page ──
    'dest.title': {
        'sr': 'Top destinacije na Balkanu',
        'en': 'Top Balkan destinations',
        'ru': 'Лучшие направления на Балканах',
    },
    'dest.subtitle': {
        'sr': 'Najpopularnija mesta za putovanje autobusom i vozom',
        'en': 'Most popular places to travel by bus and train',
        'ru': 'Самые популярные места для поездок на автобусе и поезде',
    },
    'dest.meta': {
        'sr': 'Top destinacije na Balkanu — Srbija, Crna Gora, Bosna, Hrvatska, Mađarska. Autobuske i vozne veze. Prevozni.com',
        'en': 'Top Balkan destinations — Serbia, Montenegro, Bosnia, Croatia, Hungary. Bus and train connections. Prevozni.com',
        'ru': 'Лучшие направления на Балканах — Сербия, Черногория, Босния, Хорватия, Венгрия. Автобусное и ж/д сообщение.',
    },
    'dest.serbia': {'sr': 'Srbija', 'en': 'Serbia', 'ru': 'Сербия'},
    'dest.montenegro': {'sr': 'Crna Gora', 'en': 'Montenegro', 'ru': 'Черногория'},
    'dest.bosnia': {'sr': 'Bosna i Hercegovina', 'en': 'Bosnia & Herzegovina', 'ru': 'Босния и Герцеговина'},
    'dest.croatia': {'sr': 'Hrvatska', 'en': 'Croatia', 'ru': 'Хорватия'},
    'dest.hungary': {'sr': 'Mađarska', 'en': 'Hungary', 'ru': 'Венгрия'},
    'dest.greece': {'sr': 'Grčka', 'en': 'Greece', 'ru': 'Греция'},
    'dest.north_macedonia': {'sr': 'Severna Makedonija', 'en': 'North Macedonia', 'ru': 'Северная Македония'},
    'dest.austria': {'sr': 'Austrija', 'en': 'Austria', 'ru': 'Австрия'},
    'dest.beograd': {
        'sr': 'Glavni grad Srbije. Kalemegdan, Knez Mihailova, Skadarlija, noćni život i bogata istorija.',
        'en': 'Capital of Serbia. Kalemegdan fortress, Knez Mihailova street, Skadarlija, vibrant nightlife.',
        'ru': 'Столица Сербии. Крепость Калемегдан, улица Кнез Михайлова, Скадарлия, ночная жизнь.',
    },
    'dest.budva': {
        'sr': 'Biser crnogorskog primorja. Stari grad, plaže Mogren i Slovenska, žurke do zore.',
        'en': 'Pearl of the Montenegrin coast. Old town, Mogren beach, Slovenska beach, parties till dawn.',
        'ru': 'Жемчужина черногорского побережья. Старый город, пляжи Могрен и Словенска.',
    },
    'dest.herceg_novi': {
        'sr': 'Grad na ulazu u Boku Kotorsku. Tvrđave, botanički vrtovi, kristalno čisto more.',
        'en': 'City at the entrance to Bay of Kotor. Fortresses, botanical gardens, crystal clear sea.',
        'ru': 'Город у входа в Которский залив. Крепости, ботанические сады, кристально чистое море.',
    },
    'dest.kotor': {
        'sr': 'UNESCO grad u srcu Boke. Srednjovekovni zidovi, katedrale i pogled sa tvrđave Sv. Jovana.',
        'en': 'UNESCO city in the heart of Boka. Medieval walls, cathedrals and views from St. John fortress.',
        'ru': 'Город ЮНЕСКО в сердце Боки. Средневековые стены, соборы и вид с крепости Св. Иоанна.',
    },
    'dest.novi_sad': {
        'sr': 'Drugi grad Srbije. Petrovaradinska tvrđava, EXIT festival, Fruška gora, Dunav.',
        'en': 'Second city of Serbia. Petrovaradin fortress, EXIT festival, Fruška Gora, Danube.',
        'ru': 'Второй город Сербии. Петроварадинская крепость, фестиваль EXIT, Фрушка Гора, Дунай.',
    },
    'dest.nis': {
        'sr': 'Treći grad Srbije. Niška tvrđava, Ćele-kula, Medijana, Nišava i Niška Banja.',
        'en': 'Third city of Serbia. Niš fortress, Skull Tower, Mediana, Nišava river and Niška Banja spa.',
        'ru': 'Третий город Сербии. Нишская крепость, Челе-Кула, Медиана, река Нишава и курорт Нишка Баня.',
    },
    'dest.sarajevo': {
        'sr': 'Glavni grad BiH. Baščaršija, Latinska ćuprija, Tunnel of Hope, mešavina kultura.',
        'en': 'Capital of Bosnia. Baščaršija bazaar, Latin Bridge, Tunnel of Hope, cultural melting pot.',
        'ru': 'Столица Боснии. Базар Башчаршия, Латинский мост, Тоннель надежды, смешение культур.',
    },
    'dest.dubrovnik': {
        'sr': 'Biser Jadrana. Gradske zidine, Stari grad, Game of Thrones lokacije.',
        'en': 'Pearl of the Adriatic. City walls, Old Town, Game of Thrones filming locations.',
        'ru': 'Жемчужина Адриатики. Городские стены, Старый город, локации «Игры престолов».',
    },
    'dest.budapest': {
        'sr': 'Glavni grad Mađarske. Termalni bazeni, Budimski zamak, Parlament, Dunav noću.',
        'en': 'Capital of Hungary. Thermal baths, Buda Castle, Parliament, Danube by night.',
        'ru': 'Столица Венгрии. Термальные купальни, Будайская крепость, Парламент, Дунай ночью.',
    },
    'dest.thessaloniki': {
        'sr': 'Drugi grad Grčke. Bela kula, rimski forum, fantastična hrana i živahna obala.',
        'en': 'Second city of Greece. White Tower, Roman forum, amazing food and vibrant waterfront.',
        'ru': 'Второй город Греции. Белая башня, римский форум, потрясающая еда и набережная.',
    },
    'dest.skopje': {
        'sr': 'Glavni grad S. Makedonije. Stari bazar, Kameni most, Kale tvrđava, Matka kanjon.',
        'en': 'Capital of North Macedonia. Old Bazaar, Stone Bridge, Kale Fortress, Matka Canyon.',
        'ru': 'Столица С. Македонии. Старый базар, Каменный мост, крепость Кале, каньон Матка.',
    },
    'dest.vienna': {
        'sr': 'Austrijski glavni grad. Šenbrunn, Ringštrasse, Prater, kafane i klasična muzika.',
        'en': 'Austrian capital. Schönbrunn, Ringstraße, Prater, coffee houses and classical music.',
        'ru': 'Столица Австрии. Шёнбрунн, Рингштрассе, Пратер, кофейни и классическая музика.',
    },

    'nav.destinations': {'sr': 'Destinacije', 'en': 'Destinations', 'ru': 'Направления'},

    'dest.turkey': {'sr': 'Turska', 'en': 'Turkey', 'ru': 'Турция'},
    'dest.istanbul': {
        'sr': 'Najveći grad Turske. Aja Sofija, Plava džamija, Grand bazar, Bosfor i dva kontinenta.',
        'en': 'Largest city in Turkey. Hagia Sophia, Blue Mosque, Grand Bazaar, Bosphorus and two continents.',
        'ru': 'Крупнейший город Турции. Айя-София, Голубая мечеть, Гранд-базар, Босфор и два континента.',
    },

    # ── Language names ──
    'lang.sr': {'sr': 'Srpski', 'en': 'Serbian', 'ru': 'Сербский'},
    'lang.en': {'sr': 'English', 'en': 'English', 'ru': 'English'},
    'lang.ru': {'sr': 'Русский', 'en': 'Russian', 'ru': 'Русский'},
}

SUPPORTED_LANGS = ('sr', 'en', 'ru')
DEFAULT_LANG = 'sr'


def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """Get translated string. Falls back to Serbian, then to key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key

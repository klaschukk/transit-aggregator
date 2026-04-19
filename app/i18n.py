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

    'search_results.sort_duration': {
        'sr': 'Trajanje',
        'en': 'Duration',
        'ru': 'Длительность',
    },

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
    'buy.cta': {
        'sr': 'Kupi',
        'en': 'Buy',
        'ru': 'Купить',
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

    # ── Accessibility labels ──
    'a11y.skip_to_content': {
        'sr': 'Preskoči na sadržaj',
        'en': 'Skip to content',
        'ru': 'Перейти к содержимому',
    },
    'a11y.language_switcher': {
        'sr': 'Izbor jezika',
        'en': 'Language selector',
        'ru': 'Выбор языка',
    },
    'a11y.currency_switcher': {
        'sr': 'Izbor valute',
        'en': 'Currency selector',
        'ru': 'Выбор валюты',
    },
    'a11y.search_form': {
        'sr': 'Pretraga polazaka',
        'en': 'Journey search',
        'ru': 'Поиск поездок',
    },
    'a11y.swap_cities': {
        'sr': 'Zameni polazište i odredište',
        'en': 'Swap origin and destination',
        'ru': 'Поменять местами пункты',
    },
    'a11y.trip_date': {
        'sr': 'Datum putovanja',
        'en': 'Trip date',
        'ru': 'Дата поездки',
    },
    'a11y.filters': {
        'sr': 'Filteri polazaka',
        'en': 'Journey filters',
        'ru': 'Фильтры поездок',
    },
    'a11y.city_map': {
        'sr': 'Interaktivna mapa gradskih stajališta',
        'en': 'Interactive city stops map',
        'ru': 'Интерактивная карта городских остановок',
    },
    'a11y.line_map': {
        'sr': 'Interaktivna mapa linije',
        'en': 'Interactive line map',
        'ru': 'Интерактивная карта линии',
    },
    'a11y.stop_map': {
        'sr': 'Mapa lokacije stajališta',
        'en': 'Stop location map',
        'ru': 'Карта местоположения остановки',
    },
    'a11y.breadcrumb': {
        'sr': 'Putanja',
        'en': 'Breadcrumb',
        'ru': 'Хлебные крошки',
    },
    'a11y.pagination': {
        'sr': 'Paginacija',
        'en': 'Pagination',
        'ru': 'Пагинация',
    },

    # ── Default meta (base.html) ──
    'meta.default_title': {
        'sr': 'Prevozni — red vožnje u Srbiji',
        'en': 'Prevozni — transport schedules in Serbia',
        'ru': 'Prevozni — расписание транспорта в Сербии',
    },
    'meta.default_description': {
        'sr': 'Red vožnje autobusa, vozova i gradskog prevoza u Srbiji. Pronađite polazak, uporedite cene i prevoznike. Besplatno, bez registracije.',
        'en': 'Bus, train and city transport schedules in Serbia. Find departures, compare prices and carriers. Free, no registration.',
        'ru': 'Расписание автобусов, поездов и городского транспорта в Сербии. Ищите отправления, сравнивайте цены и перевозчиков. Бесплатно, без регистрации.',
    },
    'meta.og_image_alt': {
        'sr': 'Prevozni — red vožnje Srbija',
        'en': 'Prevozni — Serbia transport schedules',
        'ru': 'Prevozni — расписание транспорта Сербии',
    },
    'meta.city_not_found': {
        'sr': 'Grad nije pronađen',
        'en': 'City not found',
        'ru': 'Город не найден',
    },

    # ── Error pages ──
    'error.404_title': {
        'sr': '404 — Stranica nije pronađena',
        'en': '404 — Page not found',
        'ru': '404 — Страница не найдена',
    },

    # ── route_index.html ──
    'route_index.title': {
        'sr': 'Sve autobuske i vozne rute u Srbiji',
        'en': 'All bus and train routes in Serbia',
        'ru': 'Все автобусные и железнодорожные маршруты в Сербии',
    },
    'route_index.meta': {
        'sr': 'međugradskih autobuskih i voznih ruta u Srbiji. Red vožnje, cene karata i prevoznici — Beograd, Novi Sad, Niš i drugi gradovi.',
        'en': 'intercity bus and train routes in Serbia. Schedules, ticket prices and carriers — Belgrade, Novi Sad, Niš and other cities.',
        'ru': 'междугородних автобусных и железнодорожных маршрутов в Сербии. Расписание, цены билетов и перевозчики — Белград, Нови-Сад, Ниш и другие города.',
    },
    'route_index.h1': {
        'sr': 'Međugradske rute',
        'en': 'Intercity routes',
        'ru': 'Междугородние маршруты',
    },
    'route_index.subtitle': {
        'sr': 'ruta · autobus i voz',
        'en': 'routes · bus and train',
        'ru': 'маршрутов · автобус и поезд',
    },
    'route_index.filter_placeholder': {
        'sr': 'Pretraži po gradu...',
        'en': 'Filter by city...',
        'ru': 'Поиск по городу...',
    },
    'route_index.results_suffix': {
        'sr': 'rezultata',
        'en': 'results',
        'ru': 'результатов',
    },
    'route_index.show_more': {
        'sr': 'Prikaži još',
        'en': 'Show more',
        'ru': 'Показать ещё',
    },
    'route_index.show_more_suffix': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'route_index.no_results': {
        'sr': 'Nema rezultata za ovaj upit',
        'en': 'No results for this query',
        'ru': 'Нет результатов по запросу',
    },
    'route_index.no_routes': {
        'sr': 'Nema dostupnih ruta',
        'en': 'No routes available',
        'ru': 'Нет доступных маршрутов',
    },
    'route_index.data_updating': {
        'sr': 'Podaci se ažuriraju',
        'en': 'Data is being updated',
        'ru': 'Данные обновляются',
    },
    'route_index.from_price': {
        'sr': 'od',
        'en': 'from',
        'ru': 'от',
    },
    'breadcrumb.all_routes': {
        'sr': 'Sve rute',
        'en': 'All routes',
        'ru': 'Все маршруты',
    },

    # ── carriers_index.html ──
    'carriers.title': {
        'sr': 'Prevoznici u Srbiji',
        'en': 'Carriers in Serbia',
        'ru': 'Перевозчики в Сербии',
    },
    'carriers.meta': {
        'sr': 'Lista autobuskih i železničkih prevoznika u Srbiji. Lasta, Niš-Ekspres, Srbija Voz i drugi.',
        'en': 'List of bus and train carriers in Serbia. Lasta, Niš-Ekspres, Srbija Voz and others.',
        'ru': 'Список автобусных и железнодорожных перевозчиков в Сербии. Lasta, Niš-Ekspres, Srbija Voz и другие.',
    },
    'carriers.h1': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'carriers.website': {
        'sr': 'Sajt',
        'en': 'Website',
        'ru': 'Сайт',
    },
    'carriers.cities_label': {
        'sr': 'Gradovi:',
        'en': 'Cities:',
        'ru': 'Города:',
    },
    'carriers.no_routes': {
        'sr': 'Nema ruta u bazi za ovog prevoznika.',
        'en': 'No routes in the database for this carrier.',
        'ru': 'Нет маршрутов в базе для этого перевозчика.',
    },
    'carriers.next_page': {
        'sr': 'Sledeća →',
        'en': 'Next →',
        'ru': 'Следующая →',
    },
    'carriers.count_suffix': {
        'sr': 'prevoznika',
        'en': 'carriers',
        'ru': 'перевозчиков',
    },
    'carriers.in_base_suffix': {
        'sr': 'prevoznika u bazi',
        'en': 'carriers in database',
        'ru': 'перевозчиков в базе',
    },
    'carriers.page_of': {
        'sr': 'strana',
        'en': 'page',
        'ru': 'страница',
    },
    'carriers.routes_count': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'carriers.empty_loading': {
        'sr': 'Podaci se učitavaju',
        'en': 'Data is loading',
        'ru': 'Данные загружаются',
    },
    'carriers.prev_page': {
        'sr': '← Prethodna',
        'en': '← Previous',
        'ru': '← Предыдущая',
    },
    'carriers.page_info': {
        'sr': 'Strana',
        'en': 'Page',
        'ru': 'Страница',
    },

    # ── stations_index.html ──
    'stations.title': {
        'sr': 'Autobuske i železničke stanice u Srbiji',
        'en': 'Bus and railway stations in Serbia',
        'ru': 'Автобусные и железнодорожные станции в Сербии',
    },
    'stations.meta': {
        'sr': 'Lista autobuskih i železničkih stanica u Srbiji.',
        'en': 'List of bus and railway stations in Serbia.',
        'ru': 'Список автобусных и железнодорожных станций в Сербии.',
    },
    'stations.h1': {
        'sr': 'Autobuske i železničke stanice',
        'en': 'Bus and railway stations',
        'ru': 'Автобусные и железнодорожные станции',
    },
    'stations.count_suffix': {
        'sr': 'stanica',
        'en': 'stations',
        'ru': 'станций',
    },
    'stations.routes_count': {
        'sr': 'ruta',
        'en': 'routes',
        'ru': 'маршрутов',
    },
    'stations.in_base_suffix': {
        'sr': 'stanica u bazi',
        'en': 'stations in database',
        'ru': 'станций в базе',
    },
    'stations.type_train': {
        'sr': 'Železnička stanica',
        'en': 'Railway station',
        'ru': 'Железнодорожная станция',
    },
    'stations.type_bus': {
        'sr': 'Autobuska stanica',
        'en': 'Bus station',
        'ru': 'Автобусная станция',
    },
    'stations.type_generic': {
        'sr': 'Stanica',
        'en': 'Station',
        'ru': 'Станция',
    },
    'stations.empty_loading': {
        'sr': 'Podaci se učitavaju',
        'en': 'Data is loading',
        'ru': 'Данные загружаются',
    },
    'stations.breadcrumb': {
        'sr': 'Stanice',
        'en': 'Stations',
        'ru': 'Станции',
    },

    # ── city_index.html ──
    'city_index.subtitle': {
        'sr': 'Linije, stajališta i red vožnje',
        'en': 'Lines, stops and schedules',
        'ru': 'Линии, остановки и расписание',
    },
    'city_index.lines_suffix': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'city_index.breadcrumb': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },

    # ── city_pair.html ──
    'city_pair.title_suffix': {
        'sr': 'autobus i voz',
        'en': 'bus and train',
        'ru': 'автобус и поезд',
    },
    'city_pair.meta_prefix': {
        'sr': 'Kako doći od',
        'en': 'How to travel from',
        'ru': 'Как добраться из',
    },
    'city_pair.meta_mid': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },
    'city_pair.meta_suffix': {
        'sr': 'Red vožnje, cene karata i prevoznici.',
        'en': 'Schedule, ticket prices and carriers.',
        'ru': 'Расписание, цены билетов и перевозчики.',
    },
    'city_pair.see_all_departures': {
        'sr': 'Pogledaj sve polaske →',
        'en': 'See all departures →',
        'ru': 'Все отправления →',
    },
    'city_pair.carriers_heading': {
        'sr': 'Prevoznici',
        'en': 'Carriers',
        'ru': 'Перевозчики',
    },
    'city_pair.carriers_hint': {
        'sr': 'Proverite kod prevoznika za aktuelne linije.',
        'en': 'Check with carriers for current lines.',
        'ru': 'Уточняйте актуальные рейсы у перевозчиков.',
    },
    'city_pair.prices_heading': {
        'sr': 'Cene',
        'en': 'Prices',
        'ru': 'Цены',
    },
    'city_pair.prices_hint': {
        'sr': 'Cene variraju po prevoznicima. Kupite karte na blagajni.',
        'en': 'Prices vary by carrier. Buy tickets at the ticket office.',
        'ru': 'Цены у разных перевозчиков отличаются. Билеты продаются в кассе.',
    },
    'city_pair.tips_heading': {
        'sr': 'Saveti',
        'en': 'Tips',
        'ru': 'Советы',
    },
    'city_pair.tip_buy_early': {
        'sr': 'Kupite kartu unapred u sezoni i za vikende.',
        'en': 'Buy tickets in advance during the season and weekends.',
        'ru': 'Покупайте билеты заранее в сезон и на выходные.',
    },
    'city_pair.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Часто задаваемые вопросы',
    },
    'city_pair.other_routes_from': {
        'sr': 'Druge rute iz grada',
        'en': 'Other routes from',
        'ru': 'Другие маршруты из',
    },
    'city_pair.departures_word': {
        'sr': 'polazaka',
        'en': 'departures',
        'ru': 'отправлений',
    },
    'city_pair.no_direct': {
        'sr': 'Direktna veza nije u bazi',
        'en': 'No direct route in database',
        'ru': 'Прямой маршрут отсутствует в базе',
    },

    # ── route_detail.html ──
    'route_detail.title_suffix': {
        'sr': 'red vožnje',
        'en': 'schedule',
        'ru': 'расписание',
    },
    'route_detail.meta_schedule': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
    },
    'route_detail.meta_daily': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
    },
    'route_detail.meta_carriers': {
        'sr': 'prevoznici',
        'en': 'carriers',
        'ru': 'перевозчики',
    },
    'route_detail.meta_and_more': {
        'sr': 'i dr',
        'en': 'and more',
        'ru': 'и др',
    },
    'route_detail.meta_from': {
        'sr': 'Od',
        'en': 'From',
        'ru': 'От',
    },
    # CTR-optimized snippets: title/meta rewrites (2026+)
    'route_detail.title_departures': {
        'sr': 'polazaka dnevno',
        'en': 'departures daily',
        'ru': 'отправлений в день',
    },
    'route_detail.meta_compare_cta': {
        'sr': 'Uporedi prevoznike i cene besplatno.',
        'en': 'Compare carriers and prices for free.',
        'ru': 'Сравните перевозчиков и цены бесплатно.',
    },
    'city_pair.title_travel': {
        'sr': 'autobus, voz, cene',
        'en': 'bus, train, prices',
        'ru': 'автобус, поезд, цены',
    },
    'city_pair.meta_cta': {
        'sr': 'Uporedi polaske, cene i vreme putovanja. Besplatno.',
        'en': 'Compare departures, prices and travel time. Free.',
        'ru': 'Сравните отправления, цены и время в пути. Бесплатно.',
    },
    'line_detail.title_line_city': {
        'sr': 'stanice i red vožnje',
        'en': 'stops and schedule',
        'ru': 'остановки и расписание',
    },
    'line_detail.meta_eta': {
        'sr': 'Karta linije, sve stanice i uživo dolasci.',
        'en': 'Line map, all stops and live arrivals.',
        'ru': 'Карта линии, все остановки и прибытия онлайн.',
    },
    'stop_detail.title_stop_city': {
        'sr': 'linije i polasci',
        'en': 'lines and departures',
        'ru': 'линии и отправления',
    },
    'stop_detail.meta_eta': {
        'sr': 'Sve linije, prvi i poslednji polazak, uživo ETA na karti.',
        'en': 'All lines, first and last departure, live ETA on the map.',
        'ru': 'Все линии, первый и последний рейс, онлайн-ETA на карте.',
    },

    # ── search_results.html ──
    'search_results.meta_from': {
        'sr': 'Red vožnje od',
        'en': 'Schedule from',
        'ru': 'Расписание от',
    },
    'search_results.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },
    'search_results.meta_desc': {
        'sr': 'svi polasci, cene karata i prevoznici na jednom mestu.',
        'en': 'all departures, ticket prices and carriers in one place.',
        'ru': 'все отправления, цены билетов и перевозчики в одном месте.',
    },
    'search_results.meta_default': {
        'sr': 'Pretražite red vožnje autobusa i vozova između gradova Srbije. Uporedite polaske, cene i prevoznike. Besplatno.',
        'en': 'Search bus and train schedules between cities in Serbia. Compare departures, prices and carriers. Free.',
        'ru': 'Ищите расписание автобусов и поездов между городами Сербии. Сравнивайте отправления, цены и перевозчиков. Бесплатно.',
    },
    'search_results.h1': {
        'sr': 'Pronađite prevoz',
        'en': 'Find transport',
        'ru': 'Найдите транспорт',
    },
    'search_results.hero_sub': {
        'sr': 'Autobus ili voz između gradova Srbije',
        'en': 'Bus or train between cities in Serbia',
        'ru': 'Автобус или поезд между городами Сербии',
    },
    'search_results.sort_label': {
        'sr': 'Sortiraj:',
        'en': 'Sort:',
        'ru': 'Сортировка:',
    },
    'search_results.sort_time': {
        'sr': 'Po vremenu',
        'en': 'By time',
        'ru': 'По времени',
    },
    'search_results.sort_price': {
        'sr': 'Po ceni',
        'en': 'By price',
        'ru': 'По цене',
    },

    # ── city_transport.html ──
    'city_transport.title_prefix': {
        'sr': 'Gradski prevoz',
        'en': 'City transport',
        'ru': 'Городской транспорт',
    },
    'city_transport.title_suffix': {
        'sr': 'linije i stajališta',
        'en': 'lines and stops',
        'ru': 'линии и остановки',
    },
    'city_transport.meta_prefix': {
        'sr': 'Red vožnje gradskog prevoza u',
        'en': 'City transport schedule in',
        'ru': 'Расписание городского транспорта в',
    },
    'city_transport.meta_lines': {
        'sr': 'linija, stajališta i polasci.',
        'en': 'lines, stops and departures.',
        'ru': 'линий, остановок и отправлений.',
    },
    'city_transport.stop_popup_more': {
        'sr': 'Polasci →',
        'en': 'Departures →',
        'ru': 'Отправления →',
    },

    # ── line_detail.html ──
    'line_detail.schedule_heading': {
        'sr': 'Red vožnje',
        'en': 'Schedule',
        'ru': 'Расписание',
    },
    'line_detail.line_prefix': {
        'sr': 'Linija',
        'en': 'Line',
        'ru': 'Линия',
    },
    'line_detail.meta_schedule': {
        'sr': 'Red vožnje linije',
        'en': 'Schedule for line',
        'ru': 'Расписание линии',
    },
    'line_detail.meta_in': {
        'sr': 'u',
        'en': 'in',
        'ru': 'в',
    },
    'line_detail.meta_stops': {
        'sr': 'stajališta.',
        'en': 'stops.',
        'ru': 'остановок.',
    },
    'line_detail.meta_departures': {
        'sr': 'Polasci od',
        'en': 'Departures from',
        'ru': 'Отправления с',
    },
    'line_detail.meta_to': {
        'sr': 'do',
        'en': 'to',
        'ru': 'до',
    },

    # ── stop_detail.html ──
    'stop_detail.stop_prefix': {
        'sr': 'Stajalište',
        'en': 'Stop',
        'ru': 'Остановка',
    },
    'stop_detail.meta_schedule': {
        'sr': 'red vožnje i polasci.',
        'en': 'schedule and departures.',
        'ru': 'расписание и отправления.',
    },
    'stop_detail.meta_lines_suffix': {
        'sr': 'linija',
        'en': 'lines',
        'ru': 'линий',
    },
    'stop_detail.meta_and_more': {
        'sr': 'i dr.',
        'en': 'and more',
        'ru': 'и др.',
    },

    # ── filter panel ──
    'filter.heading': {
        'sr': 'Filteri',
        'en': 'Filters',
        'ru': 'Фильтры',
    },
    'filter.close': {
        'sr': 'Zatvori',
        'en': 'Close',
        'ru': 'Закрыть',
    },
    'filter.transport_type': {
        'sr': 'Tip prevoza',
        'en': 'Transport type',
        'ru': 'Тип транспорта',
    },
    'filter.bus': {
        'sr': 'Autobus',
        'en': 'Bus',
        'ru': 'Автобус',
    },
    'filter.train': {
        'sr': 'Voz',
        'en': 'Train',
        'ru': 'Поезд',
    },
    'filter.carrier': {
        'sr': 'Prevoznik',
        'en': 'Carrier',
        'ru': 'Перевозчик',
    },

    # ── Search form ──
    'search_form.swap': {
        'sr': 'Zameni',
        'en': 'Swap',
        'ru': 'Поменять',
    },

    # ── city_pair FAQ (interpolated) ──
    'city_pair.faq.q_duration': {
        'sr': 'Koliko traje putovanje {from_city} — {to_city}?',
        'en': 'How long does the {from_city} — {to_city} trip take?',
        'ru': 'Сколько длится поездка {from_city} — {to_city}?',
    },
    'city_pair.faq.q_price': {
        'sr': 'Koja je cena karte {from_city} — {to_city}?',
        'en': 'What is the ticket price for {from_city} — {to_city}?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
    },
    'city_pair.faq.q_departures': {
        'sr': 'Koliko polazaka dnevno ima {from_city} — {to_city}?',
        'en': 'How many daily departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько ежедневных рейсов {from_city} — {to_city}?',
    },
    'city_pair.faq.q_operators': {
        'sr': 'Koji prevoznici voze {from_city} — {to_city}?',
        'en': 'Which carriers operate {from_city} — {to_city}?',
        'ru': 'Какие перевозчики обслуживают {from_city} — {to_city}?',
    },
    'city_pair.faq.a_duration_range': {
        'sr': 'Putovanje od {from_city} do {to_city} traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip from {from_city} to {to_city} takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка из {from_city} в {to_city} занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.a_duration_distance_suffix': {
        'sr': ' Rastojanje je {km} km.',
        'en': ' The distance is {km} km.',
        'ru': ' Расстояние — {km} км.',
    },
    'city_pair.faq.a_duration_distance_only': {
        'sr': 'Rastojanje je oko {km} km. Tačno trajanje zavisi od prevoznika.',
        'en': 'The distance is about {km} km. Exact duration depends on the carrier.',
        'ru': 'Расстояние около {km} км. Точное время зависит от перевозчика.',
    },
    'city_pair.faq.a_duration_unknown': {
        'sr': 'Trajanje zavisi od prevoznika i tipa prevoza.',
        'en': 'Duration depends on the carrier and transport type.',
        'ru': 'Время в пути зависит от перевозчика и вида транспорта.',
    },
    'city_pair.faq.a_price_range': {
        'sr': 'Cene karata kreću se od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'Ticket prices range from {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'Цены билетов варьируются от {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.a_price_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator}.',
        'en': ' The cheapest carrier is {operator}.',
        'ru': ' Самый дешёвый перевозчик — {operator}.',
    },
    'city_pair.faq.a_price_from': {
        'sr': 'Cene karata počinju od {min} RSD (oko {eur}€).',
        'en': 'Ticket prices start from {min} RSD (about {eur}€).',
        'ru': 'Цены билетов начинаются от {min} RSD (около {eur}€).',
    },
    'city_pair.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika.',
        'en': 'Prices vary depending on the carrier.',
        'ru': 'Цены зависят от перевозчика.',
    },
    'city_pair.faq.a_departures_full': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno. Prvi polazak je u {first}, poslednji u {last}.',
        'en': 'This route has {count} daily departures. First at {first}, last at {last}.',
        'ru': 'На этом маршруте {count} рейсов в день. Первый в {first}, последний в {last}.',
    },
    'city_pair.faq.a_departures_operators_suffix': {
        'sr': ' Voze: {operators}.',
        'en': ' Operated by: {operators}.',
        'ru': ' Обслуживают: {operators}.',
    },
    'city_pair.faq.a_departures_count_only': {
        'sr': 'Na ovoj ruti ima {count} polazaka dnevno.',
        'en': 'This route has {count} daily departures.',
        'ru': 'На этом маршруте {count} рейсов в день.',
    },
    'city_pair.faq.a_departures_unknown': {
        'sr': 'Broj polazaka varira. Proverite aktuelni red vožnje.',
        'en': 'The number of departures varies. Check the current schedule.',
        'ru': 'Количество рейсов меняется. Проверьте актуальное расписание.',
    },
    'city_pair.faq.a_operators_list': {
        'sr': 'Na liniji {from_city} — {to_city} voze {n} prevoznika: {operators}.',
        'en': 'On the {from_city} — {to_city} route there are {n} carriers: {operators}.',
        'ru': 'На маршруте {from_city} — {to_city} работают {n} перевозчиков: {operators}.',
    },
    'city_pair.faq.a_operators_cheapest_suffix': {
        'sr': ' Najjeftiniji prevoznik je {operator} sa cenama od {min} RSD.',
        'en': ' The cheapest carrier is {operator} with prices from {min} RSD.',
        'ru': ' Самый дешёвый перевозчик — {operator}, цены от {min} RSD.',
    },
    # JSON-LD short variants
    'city_pair.faq.ld_duration_range': {
        'sr': 'Putovanje traje od {h_min}h {m_min}min do {h_max}h {m_max}min.',
        'en': 'The trip takes from {h_min}h {m_min}min up to {h_max}h {m_max}min.',
        'ru': 'Поездка занимает от {h_min}ч {m_min}мин до {h_max}ч {m_max}мин.',
    },
    'city_pair.faq.ld_price_range': {
        'sr': 'Od {min} do {max} RSD ({eur_min}–{eur_max}€).',
        'en': 'From {min} to {max} RSD ({eur_min}–{eur_max}€).',
        'ru': 'От {min} до {max} RSD ({eur_min}–{eur_max}€).',
    },
    'city_pair.faq.ld_price_cheapest_suffix': {
        'sr': ' Najjeftiniji: {operator}.',
        'en': ' Cheapest: {operator}.',
        'ru': ' Самый дешёвый: {operator}.',
    },
    'city_pair.faq.ld_price_from': {
        'sr': 'Od {min} RSD ({eur}€).',
        'en': 'From {min} RSD ({eur}€).',
        'ru': 'От {min} RSD ({eur}€).',
    },
    'city_pair.faq.ld_price_unknown': {
        'sr': 'Cene variraju.',
        'en': 'Prices vary.',
        'ru': 'Цены варьируются.',
    },
    'city_pair.faq.ld_departures_full': {
        'sr': '{count} polazaka dnevno. Prvi u {first}, poslednji u {last}.',
        'en': '{count} departures daily. First at {first}, last at {last}.',
        'ru': '{count} рейсов в день. Первый в {first}, последний в {last}.',
    },
    'city_pair.faq.ld_departures_count_only': {
        'sr': '{count} polazaka dnevno.',
        'en': '{count} departures daily.',
        'ru': '{count} рейсов в день.',
    },
    'city_pair.faq.ld_departures_unknown': {
        'sr': 'Broj polazaka varira.',
        'en': 'The number of departures varies.',
        'ru': 'Количество рейсов меняется.',
    },
    'city_pair.faq.ld_operators_list': {
        'sr': 'Voze {n} prevoznika: {operators}.',
        'en': '{n} carriers operate: {operators}.',
        'ru': '{n} перевозчиков: {operators}.',
    },

    # ── route_detail FAQ JSON-LD ──
    'route_detail.faq.q_departures': {
        'sr': 'Koliko polazaka ima od {from_city} do {to_city}?',
        'en': 'How many departures are there from {from_city} to {to_city}?',
        'ru': 'Сколько рейсов из {from_city} в {to_city}?',
    },
    'route_detail.faq.a_departures': {
        'sr': 'Dnevno ima {count} polazaka od {from_city} do {to_city}.',
        'en': 'There are {count} daily departures from {from_city} to {to_city}.',
        'ru': 'Ежедневно выполняется {count} рейсов из {from_city} в {to_city}.',
    },
    'route_detail.faq.q_price': {
        'sr': 'Koliko košta karta {from_city} — {to_city}?',
        'en': 'How much is a {from_city} — {to_city} ticket?',
        'ru': 'Сколько стоит билет {from_city} — {to_city}?',
    },
    'route_detail.faq.a_price_from': {
        'sr': 'Cena karte počinje od {min} RSD.',
        'en': 'Ticket price starts from {min} RSD.',
        'ru': 'Цена билета начинается от {min} RSD.',
    },
    'route_detail.faq.a_price_unknown': {
        'sr': 'Cene variraju u zavisnosti od prevoznika; proverite aktuelne cene na stranici.',
        'en': 'Prices vary by carrier; check current prices on the page.',
        'ru': 'Цены зависят от перевозчика; проверьте актуальные цены на странице.',
    },
    'route_detail.faq.q_operators': {
        'sr': 'Koji prevoznici voze liniju {from_city} — {to_city}?',
        'en': 'Which carriers operate the {from_city} — {to_city} route?',
        'ru': 'Какие перевозчики обслуживают маршрут {from_city} — {to_city}?',
    },
    'route_detail.faq.a_operators_list': {
        'sr': 'Na ovoj liniji voze: {operators}.',
        'en': 'This route is operated by: {operators}.',
        'ru': 'Этот маршрут обслуживают: {operators}.',
    },
    'route_detail.faq.a_operators_unknown': {
        'sr': 'Proverite listu polazaka za aktuelne prevoznike.',
        'en': 'Check the departures list for current carriers.',
        'ru': 'Проверьте список рейсов для актуальных перевозчиков.',
    },

    # ── line_detail FAQ JSON-LD ──
    'line_detail.faq.q_stops': {
        'sr': 'Koliko stajališta ima linija {number}?',
        'en': 'How many stops does line {number} have?',
        'ru': 'Сколько остановок у линии {number}?',
    },
    'line_detail.faq.a_stops': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta, od {first} do {last}.',
        'en': 'Line {number} ({name}) in {city} has {count} stops, from {first} to {last}.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок, от {first} до {last}.',
    },
    'line_detail.faq.a_stops_no_endpoints': {
        'sr': 'Linija {number} ({name}) u {city}u ima {count} stajališta.',
        'en': 'Line {number} ({name}) in {city} has {count} stops.',
        'ru': 'Линия {number} ({name}) в городе {city} имеет {count} остановок.',
    },
    'line_detail.faq.q_when': {
        'sr': 'Kada saobraća linija {number}?',
        'en': 'When does line {number} run?',
        'ru': 'Когда работает линия {number}?',
    },
    'line_detail.faq.a_when_range': {
        'sr': 'Linija {number} saobraća od {first} do {last} radnim danom prema GTFS redu vožnje.',
        'en': 'Line {number} runs from {first} to {last} on weekdays according to the GTFS schedule.',
        'ru': 'Линия {number} работает с {first} до {last} по будням согласно расписанию GTFS.',
    },
    'line_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje linije {number} proverite na stajalištima ili kod gradskog prevoznika.',
        'en': 'Check the exact schedule for line {number} at the stops or with the city carrier.',
        'ru': 'Точное расписание линии {number} уточняйте на остановках или у городского перевозчика.',
    },
    'line_detail.faq.q_type': {
        'sr': 'Koji je tip linije {number}?',
        'en': 'What type is line {number}?',
        'ru': 'Какой тип у линии {number}?',
    },
    'line_detail.faq.a_type': {
        'sr': 'Linija {number} je {type} u sistemu gradskog prevoza grada {city}.',
        'en': 'Line {number} is a {type} in the {city} city transport system.',
        'ru': 'Линия {number} — это {type} в системе городского транспорта города {city}.',
    },

    # ── stop_detail FAQ JSON-LD ──
    'stop_detail.faq.q_lines': {
        'sr': 'Koje linije staju na stajalištu {stop}?',
        'en': 'Which lines stop at {stop}?',
        'ru': 'Какие линии останавливаются на остановке {stop}?',
    },
    'stop_detail.faq.a_lines': {
        'sr': 'Na stajalištu {stop} u {city}u staje {count} linija gradskog prevoza ({types}).',
        'en': 'At stop {stop} in {city}, {count} city transport lines stop ({types}).',
        'ru': 'На остановке {stop} в городе {city} останавливается {count} линий городского транспорта ({types}).',
    },
    'stop_detail.faq.q_when': {
        'sr': 'Kada polaze autobusi sa stajališta {stop}?',
        'en': 'When do buses depart from {stop}?',
        'ru': 'Когда отправляются автобусы с остановки {stop}?',
    },
    'stop_detail.faq.a_when_range': {
        'sr': 'Prvi polazak sa stajališta {stop} je u {first}, a poslednji u {last} radnim danom.',
        'en': 'The first departure from {stop} is at {first}, the last at {last} on weekdays.',
        'ru': 'Первый рейс с остановки {stop} в {first}, последний в {last} по будням.',
    },
    'stop_detail.faq.a_when_unknown': {
        'sr': 'Tačan red vožnje proverite na samom stajalištu ili preko mobilne aplikacije gradskog prevoznika.',
        'en': 'Check the exact schedule at the stop itself or via the city carrier mobile app.',
        'ru': 'Точное расписание уточняйте на самой остановке или в мобильном приложении городского перевозчика.',
    },
    'stop_detail.faq.q_where': {
        'sr': 'Gde se nalazi stajalište {stop}?',
        'en': 'Where is stop {stop} located?',
        'ru': 'Где находится остановка {stop}?',
    },
    'stop_detail.faq.a_where': {
        'sr': 'Stajalište {stop} se nalazi u gradu {city}.',
        'en': 'Stop {stop} is located in the city of {city}.',
        'ru': 'Остановка {stop} находится в городе {city}.',
    },
    'stop_detail.faq.a_where_coords_suffix': {
        'sr': ' Koordinate: {lat}, {lon}.',
        'en': ' Coordinates: {lat}, {lon}.',
        'ru': ' Координаты: {lat}, {lon}.',
    },
    'stop_detail.faq.a_where_outro': {
        'sr': ' Detaljna mapa i lista linija dostupni su besplatno na Prevozni.com.',
        'en': ' A detailed map and list of lines are available for free on Prevozni.com.',
        'ru': ' Подробная карта и список линий доступны бесплатно на Prevozni.com.',
    },

    # ── Hub SEO intros & FAQ: route_index (/rute/) ──
    'route_index.intro_h': {
        'sr': 'Međugradski autobusi i vozovi u Srbiji',
        'en': 'Intercity buses and trains in Serbia',
        'ru': 'Междугородние автобусы и поезда в Сербии',
    },
    'route_index.intro_p1': {
        'sr': 'Prevozni.com objedinjuje red vožnje za <strong>autobuske i železničke rute</strong> širom Srbije i regiona. '
              'Kataloške stranice pokrivaju preko 270 pravaca sa direktnim polascima između <a href="{prefix}/gradski/beograd/">Beograda</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Novog Sada</a>, <a href="{prefix}/gradski/nis/">Niša</a>, <a href="{prefix}/gradski/kragujevac/">Kragujevca</a> '
              'i desetina manjih gradova, kao i međunarodne linije ka Crnoj Gori, Bosni i Hercegovini, Hrvatskoj, Severnoj Makedoniji, Sloveniji, Mađarskoj i Turskoj. '
              'Za svaku rutu prikazujemo broj dnevnih polazaka, trajanje putovanja, minimalnu cenu karte i listu prevoznika koji saobraćaju na toj relaciji, '
              'uključujući <a href="{prefix}/prevoznici/">Lastu, Niš-Ekspres, OZLEM, Srbija Voz</a> i druge operatere.',
        'en': 'Prevozni.com aggregates timetables for <strong>intercity buses and trains</strong> across Serbia and the Balkans. '
              'The catalog covers 270+ routes with direct departures between <a href="{prefix}/gradski/beograd/">Belgrade</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Novi Sad</a>, <a href="{prefix}/gradski/nis/">Niš</a>, <a href="{prefix}/gradski/kragujevac/">Kragujevac</a> '
              'and dozens of smaller towns, plus international lines to Montenegro, Bosnia and Herzegovina, Croatia, North Macedonia, Slovenia, Hungary and Turkey. '
              'For every route we show the number of daily departures, journey time, minimum ticket price and the list of operators running the line, '
              'including <a href="{prefix}/prevoznici/">Lasta, Niš-Ekspres, OZLEM, Srbija Voz</a> and others.',
        'ru': 'Prevozni.com объединяет расписание <strong>междугородних автобусов и поездов</strong> по Сербии и Балканам. '
              'Каталог охватывает более 270 направлений с прямыми рейсами между <a href="{prefix}/gradski/beograd/">Белградом</a>, '
              '<a href="{prefix}/gradski/novi-sad/">Нови-Садом</a>, <a href="{prefix}/gradski/nis/">Нишем</a>, <a href="{prefix}/gradski/kragujevac/">Крагуевацем</a> '
              'и десятками небольших городов, а также международные рейсы в Черногорию, Боснию и Герцеговину, Хорватию, Северную Македонию, Словению, Венгрию и Турцию. '
              'По каждому маршруту мы показываем количество ежедневных рейсов, длительность поездки, минимальную цену билета и список перевозчиков, '
              'включая <a href="{prefix}/prevoznici/">Lasta, Niš-Ekspres, OZLEM, Srbija Voz</a> и других.',
    },
    'route_index.intro_p2': {
        'sr': 'Pretraga u vrhu stranice filtrira rute u realnom vremenu prema imenu polaznog ili ciljnog grada. '
              'Klikom na bilo koju rutu otvarate detaljnu stranicu sa spiskom polazaka po satu, cenama po prevozniku i filterima po delu dana '
              '(jutro 06–12, popodne 12–18, veče 18–22, noć 22–06). Svaka ruta ima i SEO parnu stranicu tipa '
              '<code>/voznja/grad1-do-grad2/</code> sa prosečnim trajanjem, rasponom cena i najjeftinijim prevoznikom — '
              'korisno kad biramo najpovoljniji termin putovanja. Red vožnje se automatski osvežava svakih 24 sata iz zvaničnih izvora '
              '(busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). Karte se kupuju na blagajni autobuske stanice, u vozilu kod vozača ili online preko partnerskih sajtova.',
        'en': 'The search bar at the top filters routes live by origin or destination city. '
              'Clicking any route opens a detail page with hour-by-hour departures, prices per operator and time-of-day filters '
              '(morning 06–12, afternoon 12–18, evening 18–22, night 22–06). Every route also has an SEO city-pair page at '
              '<code>/voznja/city1-do-city2/</code> with average duration, price range and the cheapest operator — useful for picking the best-value departure. '
              'Timetables refresh every 24 hours from official sources (busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). '
              'Tickets are sold at bus-station counters, on-board from the driver, or online through partner sites.',
        'ru': 'Строка поиска сверху фильтрует маршруты в реальном времени по названию города отправления или прибытия. '
              'При клике на маршрут открывается детальная страница с рейсами по часам, ценами по перевозчикам и фильтрами по времени суток '
              '(утро 06–12, день 12–18, вечер 18–22, ночь 22–06). У каждого маршрута также есть SEO-страница пары городов по адресу '
              '<code>/voznja/gorod1-do-gorod2/</code> со средней длительностью, диапазоном цен и самым дешёвым перевозчиком — полезно при выборе оптимального рейса. '
              'Расписание обновляется каждые 24 часа из официальных источников (busticket4.me, polazak.rs, bgprevoz, gspns, srbijavoz). '
              'Билеты продаются в кассах автовокзала, у водителя в автобусе или онлайн через партнёрские сайты.',
    },
    'route_index.faq_heading': {
        'sr': 'Česta pitanja o autobuskim rutama',
        'en': 'Frequently asked questions about bus routes',
        'ru': 'Частые вопросы об автобусных маршрутах',
    },
    'route_index.faq_q1': {
        'sr': 'Koliko međugradskih ruta pokriva Prevozni.com?',
        'en': 'How many intercity routes does Prevozni.com cover?',
        'ru': 'Сколько междугородних маршрутов охватывает Prevozni.com?',
    },
    'route_index.faq_a1': {
        'sr': 'U bazi imamo {n} domaćih i međunarodnih linija sa preko 2800 polazaka dnevno. Katalog uključuje sve velike prevoznike u Srbiji (Lasta, Niš-Ekspres, Srbija Voz) '
              'i regionalne operatere za linije ka Crnoj Gori, BiH, Hrvatskoj, Mađarskoj, Severnoj Makedoniji i Turskoj. Svakog dana se podaci ažuriraju iz zvaničnih izvora.',
        'en': 'The database holds {n} domestic and international routes with 2,800+ daily departures. The catalog includes all major Serbian carriers (Lasta, Niš-Ekspres, Srbija Voz) '
              'plus regional operators for lines to Montenegro, Bosnia, Croatia, Hungary, North Macedonia and Turkey. Data is refreshed daily from official sources.',
        'ru': 'В базе {n} внутренних и международных маршрутов с более чем 2800 рейсами в сутки. Каталог включает всех крупных сербских перевозчиков (Lasta, Niš-Ekspres, Srbija Voz) '
              'и региональных операторов на линиях в Черногорию, Боснию, Хорватию, Венгрию, Северную Македонию и Турцию. Данные обновляются ежедневно.',
    },
    'route_index.faq_q2': {
        'sr': 'Kako da nađem najjeftiniju autobusku kartu?',
        'en': 'How do I find the cheapest bus ticket?',
        'ru': 'Как найти самый дешёвый автобусный билет?',
    },
    'route_index.faq_a2': {
        'sr': 'Otvorite detaljnu stranicu rute i pogledajte kolonu cene — svaki polazak prikazuje cenu u RSD i EUR. '
              'Na SEO parnoj stranici /voznja/grad1-do-grad2/ prikazan je raspon cena i najjeftiniji prevoznik. '
              'Generalno, rani jutarnji (06–08) i noćni (22–06) polasci često imaju niže cene, a kupovina karte unapred može doneti dodatni popust kod nekih operatera.',
        'en': 'Open the route detail page and check the price column — each departure shows the price in RSD and EUR. '
              'The SEO city-pair page at /voznja/city1-do-city2/ displays the price range and the cheapest operator. '
              'In general, early morning (06–08) and overnight (22–06) departures often have lower fares, and buying in advance can unlock additional discounts with some operators.',
        'ru': 'Откройте детальную страницу маршрута и посмотрите колонку цены — у каждого рейса указана цена в RSD и EUR. '
              'На SEO-странице пары /voznja/gorod1-do-gorod2/ показан диапазон цен и самый дешёвый перевозчик. '
              'Обычно ранние утренние (06–08) и ночные (22–06) рейсы дешевле, а покупка билета заранее иногда даёт дополнительную скидку.',
    },
    'route_index.faq_q3': {
        'sr': 'Mogu li da kupim kartu direktno preko Prevozni.com?',
        'en': 'Can I buy a ticket directly through Prevozni.com?',
        'ru': 'Можно ли купить билет прямо через Prevozni.com?',
    },
    'route_index.faq_a3': {
        'sr': 'Prevozni.com je informativni servis — red vožnje je besplatan i bez registracije. '
              'Na svakoj stranici rute nalazi se dugme „Kupi kartu" koje vodi na partnerski sistem (Bookaway) gde se kupovina obavlja online. '
              'Karte se takođe kupuju na blagajni autobuske stanice ili kod vozača u autobusu.',
        'en': 'Prevozni.com is an information service — timetables are free and require no registration. '
              'Each route page has a "Buy ticket" button that opens our partner (Bookaway) for online booking. '
              'Tickets are also sold at the bus station counter or on-board from the driver.',
        'ru': 'Prevozni.com — информационный сервис: расписание бесплатно и без регистрации. '
              'На каждой странице маршрута есть кнопка «Купить билет», которая ведёт к партнёру (Bookaway) для онлайн-покупки. '
              'Билеты также продаются в кассе автовокзала или у водителя.',
    },
    'route_index.faq_q4': {
        'sr': 'Koliko često se ažurira red vožnje?',
        'en': 'How often are timetables updated?',
        'ru': 'Как часто обновляется расписание?',
    },
    'route_index.faq_a4': {
        'sr': 'Osnovni podaci (rute, prevoznici, cene) ažuriraju se svakodnevno u 3:00 ujutru iz zvaničnih izvora. '
              'Za GTFS podatke o gradskom prevozu Beograda i Novog Sada, ažuriranje se vrši nedeljno. '
              'Ukoliko primetite netačan podatak, možete nas kontaktirati preko <a href="{prefix}/kontakt/">kontakt stranice</a>.',
        'en': 'Route-level data (routes, operators, prices) refresh nightly at 3:00 AM from official sources. '
              'GTFS city-transit data for Belgrade and Novi Sad is updated weekly. '
              'If you spot an error, please let us know via the <a href="{prefix}/kontakt/">contact page</a>.',
        'ru': 'Основные данные (маршруты, перевозчики, цены) обновляются ночью в 3:00 из официальных источников. '
              'GTFS-данные по городскому транспорту Белграда и Нови-Сада обновляются еженедельно. '
              'Если заметили неточность, напишите нам через <a href="{prefix}/kontakt/">страницу контактов</a>.',
    },
    'route_index.popular_heading': {
        'sr': 'Najpopularnije rute',
        'en': 'Most popular routes',
        'ru': 'Самые популярные маршруты',
    },

    # ── Hub SEO intros & FAQ: city_index (/gradski/) ──
    'city_index.intro_h': {
        'sr': 'Gradski prevoz u Srbiji: linije, stajališta, mape',
        'en': 'City public transit in Serbia: lines, stops, maps',
        'ru': 'Городской транспорт Сербии: линии, остановки, карты',
    },
    'city_index.intro_p1': {
        'sr': 'Četiri najveća grada Srbije imaju razvijenu mrežu javnog gradskog prevoza. '
              '<strong><a href="{prefix}/gradski/beograd/">Beograd</a></strong> operiše sa preko 500 linija autobusa, tramvaja i trolejbusa '
              'u okviru GSP Beograd, sa potpunim GTFS rasporedom od preko 87.000 dnevnih polazaka. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Novi Sad</a></strong> ima 60+ linija JGSP Novi Sad sa rasporedom od 6.500 polazaka. '
              '<strong><a href="{prefix}/gradski/nis/">Niš</a></strong> opslužuje JGP Niš-Ekspres sa 50+ linija, '
              'a <strong><a href="{prefix}/gradski/kragujevac/">Kragujevac</a></strong> 23 linije lokalnog prevoznika. '
              'Ukupno je u bazi 610 linija i preko 3700 stajališta sa GPS koordinatama — praktično sve stajalište u glavnim gradovima možete pronaći na interaktivnoj mapi.',
        'en': 'Serbia\'s four largest cities run full-fledged public transit networks. '
              '<strong><a href="{prefix}/gradski/beograd/">Belgrade</a></strong> operates 500+ bus, tram and trolleybus lines under GSP Beograd, '
              'with a complete GTFS schedule of 87,000+ daily departures. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Novi Sad</a></strong> has 60+ JGSP Novi Sad lines with a 6,500-departure schedule. '
              '<strong><a href="{prefix}/gradski/nis/">Niš</a></strong> is served by JGP Niš-Ekspres with 50+ lines, '
              'and <strong><a href="{prefix}/gradski/kragujevac/">Kragujevac</a></strong> by 23 local carrier lines. '
              'In total the database holds 610 lines and over 3,700 stops with GPS coordinates — you can find practically any stop in the main cities on the interactive map.',
        'ru': 'Четыре крупнейших города Сербии имеют развитую сеть городского транспорта. '
              '<strong><a href="{prefix}/gradski/beograd/">Белград</a></strong> — 500+ линий автобусов, трамваев и троллейбусов под управлением GSP Beograd, '
              'с полным GTFS-расписанием на 87 000+ рейсов в сутки. '
              '<strong><a href="{prefix}/gradski/novi-sad/">Нови-Сад</a></strong> — 60+ линий JGSP Novi Sad с расписанием на 6 500 рейсов. '
              '<strong><a href="{prefix}/gradski/nis/">Ниш</a></strong> обслуживается JGP Niš-Ekspres с 50+ линиями, '
              '<strong><a href="{prefix}/gradski/kragujevac/">Крагуевац</a></strong> — 23 линии местного перевозчика. '
              'Всего в базе 610 линий и более 3700 остановок с GPS-координатами — практически любую остановку крупных городов можно найти на интерактивной карте.',
    },
    'city_index.intro_p2': {
        'sr': 'Za svaku liniju prikazujemo trasu, spisak stajališta, tip prevoza (autobus / tramvaj / trolejbus / noćna linija) i, gde postoji GTFS feed, '
              'tačan raspored polazaka za radni dan, subotu i nedelju. Klikom na stajalište otvarate stranicu sa spiskom linija koje tu staju, '
              'procenom vremena dolaska narednog vozila (ETA) i najbližim stajalištima. '
              'Karte za gradski prevoz u Srbiji kupuju se preko BusPlus kartice (Beograd), AP karte (Novi Sad) ili na kioscima i kod vozača. '
              'Prevozni.com ne prodaje karte za gradski prevoz — naš cilj je da ponudi besplatan i brz pregled linija, stajališta i polazaka '
              'u svim većim gradovima, korisno putnicima, turistima i studentima koji se tek upoznaju sa mrežom.',
        'en': 'For every line we show the route path, stop list, transport type (bus / tram / trolleybus / night line) and, where a GTFS feed is available, '
              'the exact departure schedule for weekdays, Saturdays and Sundays. Clicking a stop opens a page with the lines serving it, '
              'an ETA estimate for the next arriving vehicle and nearby stops. '
              'Tickets for city transit in Serbia are purchased with the BusPlus card (Belgrade), AP card (Novi Sad) or at kiosks and from the driver. '
              'Prevozni.com does not sell city-transit tickets — our goal is to provide a free, fast overview of lines, stops and departures '
              'in every major city, useful for commuters, tourists and students learning the network.',
        'ru': 'Для каждой линии показываем трассу, список остановок, тип транспорта (автобус / трамвай / троллейбус / ночная линия) и, где есть GTFS, '
              'точное расписание на будни, субботу и воскресенье. При клике на остановку открывается страница со списком линий, '
              'прогнозом времени прибытия следующего транспорта (ETA) и ближайшими остановками. '
              'Билеты на городской транспорт покупаются по карте BusPlus (Белград), AP (Нови-Сад), в киосках или у водителя. '
              'Prevozni.com не продаёт билеты на городской транспорт — наша цель дать бесплатный и быстрый обзор линий, остановок и рейсов '
              'во всех крупных городах, что полезно местным жителям, туристам и студентам.',
    },
    'city_index.faq_heading': {
        'sr': 'Česta pitanja o gradskom prevozu',
        'en': 'Frequently asked questions about city transit',
        'ru': 'Частые вопросы о городском транспорте',
    },
    'city_index.faq_q1': {
        'sr': 'Koji gradovi imaju kompletne podatke na Prevozni.com?',
        'en': 'Which cities have complete data on Prevozni.com?',
        'ru': 'В каких городах есть полные данные на Prevozni.com?',
    },
    'city_index.faq_a1': {
        'sr': 'Trenutno pokrivamo Beograd (GSP, 514 linija, pun GTFS raspored), Novi Sad (JGSP, 61 linija, GTFS), '
              'Niš (JGP Niš-Ekspres, 53 linije) i Kragujevac (23 linije). Za Beograd i Novi Sad imamo tačne vremena polazaka; '
              'za Niš i Kragujevac prikazujemo trase i stajališta ali bez detaljnog GTFS rasporeda.',
        'en': 'We currently cover Belgrade (GSP, 514 lines, full GTFS schedule), Novi Sad (JGSP, 61 lines, GTFS), '
              'Niš (JGP Niš-Ekspres, 53 lines) and Kragujevac (23 lines). Belgrade and Novi Sad have precise departure times; '
              'Niš and Kragujevac show routes and stops but without detailed GTFS schedules.',
        'ru': 'Сейчас охвачены Белград (GSP, 514 линий, полный GTFS), Нови-Сад (JGSP, 61 линия, GTFS), '
              'Ниш (JGP Niš-Ekspres, 53 линии) и Крагуевац (23 линии). У Белграда и Нови-Сада точное время рейсов; '
              'у Ниша и Крагуеваца — только трассы и остановки без подробного GTFS-расписания.',
    },
    'city_index.faq_q2': {
        'sr': 'Kako da nađem stajalište najbliže mojoj adresi?',
        'en': 'How do I find the stop closest to my address?',
        'ru': 'Как найти остановку, ближайшую к моему адресу?',
    },
    'city_index.faq_a2': {
        'sr': 'Otvorite stranicu grada (npr. /gradski/beograd/) i koristite interaktivnu mapu. '
              'Mapa prikazuje sva stajališta sa GPS koordinatama — zumirajte do željenog dela grada i kliknite na marker '
              'da vidite koje linije tu staju. Na stranici svakog stajališta prikazujemo i obližnja stajališta u radijusu od 500 metara.',
        'en': 'Open the city page (e.g. /gradski/beograd/) and use the interactive map. '
              'The map shows every stop with GPS coordinates — zoom to your area and click a marker to see which lines stop there. '
              'Each stop\'s detail page also lists nearby stops within ~500 metres.',
        'ru': 'Откройте страницу города (например /gradski/beograd/) и воспользуйтесь интерактивной картой. '
              'На карте отмечены все остановки с GPS — приблизьте нужный район и кликните по маркеру, чтобы увидеть линии. '
              'На странице каждой остановки также есть список ближайших остановок в радиусе ~500 м.',
    },
    'city_index.faq_q3': {
        'sr': 'Da li je raspored tačan u realnom vremenu?',
        'en': 'Is the schedule real-time?',
        'ru': 'Показывается ли расписание в реальном времени?',
    },
    'city_index.faq_a3': {
        'sr': 'Prikazujemo planirani red vožnje iz GTFS feeda (ne GPS lokaciju vozila). ETA na stranici stajališta se računa iz rasporeda — '
              'za stvarni GPS položaj vozila koristite zvanične aplikacije gradskih prevoznika (BusPlus, Moj Grad Beograd, Beograd+). '
              'U praksi su polasci u Beogradu tačni unutar 5 minuta tokom radnog dana.',
        'en': 'We show the scheduled timetable from GTFS feeds, not live vehicle GPS. The ETA on a stop page is computed from the schedule — '
              'for real-time vehicle positions, use the official city-carrier apps (BusPlus, Moj Grad Beograd, Beograd+). '
              'In practice Belgrade departures are accurate within ~5 minutes on weekdays.',
        'ru': 'Показываем плановое расписание из GTFS (не GPS-позицию транспорта). ETA на странице остановки считается из расписания — '
              'для реального положения транспорта используйте официальные приложения (BusPlus, Moj Grad Beograd, Beograd+). '
              'На практике в Белграде рейсы по будням точны в пределах ~5 минут.',
    },

    # ── Hub SEO intros & FAQ: city_transport (/gradski/{city}/) ──
    'city_transport.intro_h': {
        'sr': 'O gradskom prevozu: {city}',
        'en': 'About public transit in {city}',
        'ru': 'О городском транспорте: {city}',
    },
    'city_transport.intro_beograd_p1': {
        'sr': '<strong>GSP Beograd</strong> upravlja najvećom mrežom javnog prevoza u Srbiji: autobusi, tramvaji i trolejbusi čine više od 500 linija, '
              'sa preko 87.000 dnevnih polazaka. Sistem pokriva 17 beogradskih opština, od Zemuna i Novog Beograda preko Vračara i Voždovca do Rakovice i Grocke. '
              'Noćne linije (oznaka „N") saobraćaju sedam dana u nedelji, svakih 30–60 minuta, povezujući centar sa glavnim perifernim kvartovima. '
              'Tramvajska mreža ima 12 dnevnih linija oko centra i Novog Beograda, trolejbuski sistem obuhvata 8 linija ka Zvezdari, Voždovcu i Paliluli. '
              'Pored ovoga, BG:Voz — prigradski železnički sistem — povezuje Beograd sa Batajnicom, Ovčom i Resnikom.',
        'en': '<strong>GSP Beograd</strong> operates the largest public-transit network in Serbia: buses, trams and trolleybuses form 500+ lines '
              'with 87,000+ daily departures. The system covers all 17 Belgrade municipalities, from Zemun and Novi Beograd through Vračar and Voždovac to Rakovica and Grocka. '
              'Night lines (prefix "N") run seven days a week every 30–60 minutes, linking the centre to major outer districts. '
              'The tram network has 12 daytime lines around the centre and Novi Beograd; 8 trolleybus lines connect Zvezdara, Voždovac and Palilula. '
              'BG:Voz suburban rail also links Belgrade with Batajnica, Ovča and Resnik.',
        'ru': '<strong>GSP Beograd</strong> управляет крупнейшей сетью общественного транспорта Сербии: автобусы, трамваи и троллейбусы — это 500+ линий '
              'и более 87 000 рейсов в сутки. Система охватывает все 17 белградских общин, от Земуна и Нового Белграда до Врачара, Вождовца, Раковицы и Гроцки. '
              'Ночные линии (префикс «N») работают 7 дней в неделю каждые 30–60 минут, соединяя центр с основными окраинами. '
              'Трамвайная сеть — 12 дневных линий в центре и Новом Белграде; 8 троллейбусных линий — Звездара, Вождовац и Палилула. '
              'BG:Voz — пригородная железная дорога до Батайницы, Овчи и Ресника.',
    },
    'city_transport.intro_beograd_p2': {
        'sr': 'Karte se kupuju preko <strong>BusPlus kartice</strong>, koja se puni na kioscima ili u GSP-ovim prodajnim mestima. '
              'Cena jednokratne vožnje u zoni I iznosi oko 50 RSD, a dnevna karta košta 290 RSD. Studenti, penzioneri i đaci imaju popust uz potvrdu statusa. '
              'BG:Voz koristi drugačiji tarifni sistem — karte se kupuju na stanicama Srbija Voza. '
              'Za putovanja van Beograda koristi se mreža <a href="{prefix}/rute/">međugradskih autobusa i vozova</a>, sa polazcima sa Autobuske stanice BAS, '
              'Centralnog železničkog stajališta Prokop i Lasta stanice.',
        'en': 'Tickets are purchased with the <strong>BusPlus card</strong>, rechargeable at kiosks and GSP points. '
              'A single ride in Zone I costs around 50 RSD, a day pass 290 RSD. Students, pensioners and pupils get discounts with proof of status. '
              'BG:Voz uses a separate Srbija Voz ticket system. '
              'For travel outside Belgrade, use the <a href="{prefix}/rute/">intercity bus and train network</a>, with departures from BAS Bus Station, '
              'Prokop Central Station and the Lasta terminal.',
        'ru': 'Билеты покупаются по карте <strong>BusPlus</strong>, которую пополняют в киосках и точках GSP. '
              'Одна поездка в зоне I — около 50 RSD, проездной на день — 290 RSD. Студенты, пенсионеры и школьники — по скидке при наличии документа. '
              'У BG:Voz отдельная тарифная система — билеты Srbija Voz. '
              'Для поездок за пределами Белграда — сеть <a href="{prefix}/rute/">междугородних автобусов и поездов</a> с отправлением с автостанции BAS, '
              'центрального ж/д вокзала Прокоп и терминала Lasta.',
    },
    'city_transport.intro_novi_sad_p1': {
        'sr': '<strong>JGSP Novi Sad</strong> upravlja javnim gradskim prevozom u drugom najvećem gradu Srbije. '
              'Mreža se sastoji od 60+ autobuskih linija koje povezuju centralno gradsko jezgro sa prigradskim naseljima (Petrovaradin, Sremska Kamenica, Futog, Veternik, Rumenka, Kać). '
              'Gradski prevoz u Novom Sadu je prvenstveno autobuski — tramvaja i trolejbusa u gradu nema. '
              'GTFS raspored za Novi Sad je dostupan u našoj bazi, tako da je moguće prikazati tačne polaske po satu za radni dan, subotu i nedelju.',
        'en': '<strong>JGSP Novi Sad</strong> runs city transit in Serbia\'s second-largest city. '
              'The network consists of 60+ bus lines connecting the city core with suburban settlements (Petrovaradin, Sremska Kamenica, Futog, Veternik, Rumenka, Kać). '
              'Novi Sad has no trams or trolleybuses — transit is bus-only. '
              'A GTFS schedule for Novi Sad is in our database, so exact departure times for weekdays, Saturdays and Sundays are available.',
        'ru': '<strong>JGSP Novi Sad</strong> управляет городским транспортом второго по величине города Сербии. '
              'Сеть — 60+ автобусных линий, соединяющих центр с пригородами (Петроварадин, Сремска-Каменица, Футог, Ветерник, Руменка, Кач). '
              'В Нови-Саде нет трамваев и троллейбусов — только автобусы. '
              'GTFS-расписание Нови-Сада есть в нашей базе, поэтому доступно точное время рейсов на будни, субботу и воскресенье.',
    },
    'city_transport.intro_novi_sad_p2': {
        'sr': 'Karte se kupuju preko <strong>AP kartice JGSP Novi Sad</strong>, pametne kartice koja se puni u AP kioscima ili aplikaciji Moj JGSP. '
              'Cena jednokratne vožnje iznosi oko 65 RSD, mesečna karta za đake košta od 1000 RSD. Pojedinačnu kartu moguće je kupiti i kod vozača po nešto višoj ceni. '
              'Za <a href="{prefix}/rute/">međugradske linije</a> koristi se Autobuska stanica Novi Sad — povezuje Novi Sad sa Beogradom, Suboticom, Nišom, Zrenjaninom i desetinama drugih gradova.',
        'en': 'Tickets use the <strong>JGSP Novi Sad AP card</strong>, a smart card rechargeable at AP kiosks or the Moj JGSP app. '
              'A single ride costs around 65 RSD, a monthly student pass starts at 1,000 RSD. Single tickets can also be purchased from the driver at a slightly higher price. '
              'For <a href="{prefix}/rute/">intercity routes</a> use Novi Sad Bus Station — connecting Novi Sad with Belgrade, Subotica, Niš, Zrenjanin and dozens of other cities.',
        'ru': 'Билеты — по смарт-карте <strong>JGSP Novi Sad (AP)</strong>, которую пополняют в киосках AP или приложении Moj JGSP. '
              'Одна поездка — около 65 RSD, ученический проездной — от 1000 RSD. Разовый билет можно купить и у водителя по чуть более высокой цене. '
              '<a href="{prefix}/rute/">Междугородние рейсы</a> — с автовокзала Нови-Сада: Белград, Суботица, Ниш, Зренянин и десятки других городов.',
    },
    'city_transport.intro_nis_p1': {
        'sr': '<strong>JGP Niš-Ekspres</strong> operiše gradskim prevozom u Nišu i okolini. '
              'Mreža obuhvata oko 50 autobuskih linija koje pokrivaju Niš i prigradska naselja — od Medoševca i Bubnja na zapadu do Donjeg Međurova i Crvenog Krsta na istoku. '
              'Ne postoji tramvajski ili trolejbuski sistem. GTFS raspored za Niš nije javno dostupan, zato prikazujemo trase i spiskove stajališta, '
              'a za tačno vreme polazaka preporučujemo proveru u vozilu ili na kioscima Niš-Ekspresa.',
        'en': '<strong>JGP Niš-Ekspres</strong> runs city transit in Niš and its surroundings. '
              'The network comprises some 50 bus lines covering Niš and suburban settlements — from Medoševac and Bubanj in the west to Donje Međurovo and Crveni Krst in the east. '
              'There are no trams or trolleybuses. A public GTFS schedule for Niš is not available, so we show routes and stop lists — '
              'for exact departure times, check on-board or at Niš-Ekspres kiosks.',
        'ru': '<strong>JGP Niš-Ekspres</strong> — городской перевозчик Ниша и окрестностей. '
              'Сеть — около 50 автобусных линий по Нишу и пригородам: от Медошеваца и Бубни на западе до Донего-Мэдюрова и Црвеного-Крста на востоке. '
              'Трамваев и троллейбусов нет. Публичного GTFS-расписания для Ниша нет, поэтому показываем трассы и списки остановок — '
              'точное время уточняйте в автобусе или в киосках Niš-Ekspres.',
    },
    'city_transport.intro_nis_p2': {
        'sr': 'Karte se kupuju u vozilu kod vozača (jednokratna vožnja oko 50 RSD) ili na mesečnim karticama Niš-Ekspresa za đake, studente i penzionere. '
              'Niš je i važno čvorište za <a href="{prefix}/rute/">međugradske i međunarodne autobuske linije</a> ka Skoplju, Sofiji, Istanbulu i drugim evropskim gradovima — '
              'polaze sa Autobuske stanice Niš. Železnica Srbije (Srbija Voz) takođe opslužuje Niš preko linija ka Beogradu, Preševu (granica sa Severnom Makedonijom) i Pirotu.',
        'en': 'Tickets are bought on-board from the driver (single ride ~50 RSD) or via monthly Niš-Ekspres cards for pupils, students and pensioners. '
              'Niš is also a hub for <a href="{prefix}/rute/">intercity and international bus lines</a> to Skopje, Sofia, Istanbul and other European cities — '
              'departing from Niš Bus Station. Serbian Railways (Srbija Voz) also serves Niš via lines to Belgrade, Preševo (North Macedonia border) and Pirot.',
        'ru': 'Билеты — у водителя (одна поездка ~50 RSD) или по месячным картам Niš-Ekspres для школьников, студентов и пенсионеров. '
              'Ниш — важный узел <a href="{prefix}/rute/">междугородних и международных автобусных линий</a>: Скопье, София, Стамбул и др. — с автовокзала Ниша. '
              'Железные дороги Сербии (Srbija Voz) — линии на Белград, Прешево (граница с С. Македонией) и Пирот.',
    },
    'city_transport.intro_kragujevac_p1': {
        'sr': '<strong>Kragujevac</strong>, četvrti po veličini grad Srbije i istorijska prestonica (1818–1841), '
              'ima kompaktnu autobusku mrežu od 23 linije koja pokriva centar i okolna naselja (Stanovo, Aerodrom, Pivara, Belošavac, Bubanj). '
              'Za Kragujevac prikazujemo trase i spiskove stajališta dobijene iz OSM/Overpass podataka; '
              'tačan GTFS raspored nije javno dostupan, pa za vreme polazaka preporučujemo proveru na stajalištima ili kod prevoznika.',
        'en': '<strong>Kragujevac</strong>, Serbia\'s fourth-largest city and former capital (1818–1841), '
              'has a compact 23-line bus network covering the centre and surrounding settlements (Stanovo, Aerodrom, Pivara, Belošavac, Bubanj). '
              'For Kragujevac we show routes and stop lists built from OSM/Overpass data; '
              'a public GTFS schedule is not available, so check departure times at the stops or with the carrier.',
        'ru': '<strong>Крагуевац</strong> — четвёртый по величине город Сербии и бывшая столица (1818–1841) — '
              'имеет компактную сеть из 23 автобусных линий: центр и пригороды (Станово, Аэродром, Пивара, Белошавац, Бубань). '
              'Показываем трассы и списки остановок по данным OSM/Overpass; '
              'публичного GTFS-расписания нет — время рейсов уточняйте на остановках или у перевозчика.',
    },
    'city_transport.intro_kragujevac_p2': {
        'sr': 'Karte se kupuju u autobusu kod vozača, a za đake i studente postoje povlašćene mesečne karte. '
              'Kragujevac je odlično povezan sa Beogradom (preko 20 polazaka dnevno) i Kraljevom; '
              'pretraga <a href="{prefix}/rute/">svih međugradskih linija</a> vam pomaže da nađete najbolji polazak za svaki dan. '
              'Autobuska stanica Kragujevac nalazi se u centru grada, blizu železničke stanice koja je takođe povezana sa Beogradom i Lapovom.',
        'en': 'Tickets are bought on-board from the driver, with discounted monthly cards for pupils and students. '
              'Kragujevac is well-connected with Belgrade (20+ daily departures) and Kraljevo; '
              'search <a href="{prefix}/rute/">all intercity routes</a> to find the best departure for any day. '
              'Kragujevac Bus Station is in the city centre, near the railway station linked to Belgrade and Lapovo.',
        'ru': 'Билеты — у водителя, для учеников и студентов — скидочные месячные проездные. '
              'Крагуевац хорошо связан с Белградом (20+ рейсов в день) и Кралево; '
              'ищите <a href="{prefix}/rute/">все междугородние маршруты</a> для подбора оптимального рейса. '
              'Автовокзал в центре города, рядом с ж/д станцией, которая связана с Белградом и Лапово.',
    },
    'city_transport.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'city_transport.faq_q1': {
        'sr': 'Kako da kupim kartu za gradski prevoz u {city}u?',
        'en': 'How do I buy a transit ticket in {city}?',
        'ru': 'Как купить билет на городской транспорт в {city}?',
    },
    'city_transport.faq_q2': {
        'sr': 'Koliko linija opslužuje {city}?',
        'en': 'How many lines serve {city}?',
        'ru': 'Сколько линий обслуживает {city}?',
    },
    'city_transport.faq_a2': {
        'sr': 'U mreži ima {n} aktivnih linija, sa ukupno {stops} stajališta mapiranih u našoj bazi. '
              'Brojevi linija prikazuju se sa filterom po tipu (autobus, tramvaj, trolejbus, noćna) u vrhu stranice.',
        'en': '{n} active lines serve the city, with {stops} stops mapped in our database. '
              'Lines are filterable by type (bus, tram, trolleybus, night) at the top of the page.',
        'ru': 'Сеть включает {n} активных линий и {stops} остановок в нашей базе. '
              'Линии можно фильтровать по типу (автобус, трамвай, троллейбус, ночная) вверху страницы.',
    },
    'city_transport.faq_q3': {
        'sr': 'Radi li gradski prevoz nedeljom i praznikom?',
        'en': 'Does transit run on Sundays and holidays?',
        'ru': 'Работает ли транспорт по воскресеньям и праздникам?',
    },
    'city_transport.faq_a3': {
        'sr': 'Da, većina linija saobraća sedam dana u nedelji, sa smanjenom frekvencijom subotom i nedeljom. '
              'Raspored vidite u rubrici „Subota" i „Nedelja" na stranici svake linije. Državnim praznicima obično se primenjuje nedeljni raspored.',
        'en': 'Yes, most lines run seven days a week with reduced weekend frequency. '
              'The schedule is split into Saturday and Sunday tabs on each line page. On public holidays the Sunday schedule typically applies.',
        'ru': 'Да, большинство линий работают 7 дней в неделю с сокращённой частотой по выходным. '
              'Расписание в табах «Субота» и «Недеља» на странице каждой линии. В госпраздники обычно действует воскресное расписание.',
    },
    'city_transport.faq_q4': {
        'sr': 'Kako stižem iz {city}a u druge gradove Srbije?',
        'en': 'How do I get from {city} to other cities in Serbia?',
        'ru': 'Как добраться из {city} в другие города Сербии?',
    },
    'city_transport.faq_a4': {
        'sr': 'Za međugradski prevoz koristite našu stranicu <a href="{prefix}/rute/">svih ruta</a> ili direktno tražite polazak preko '
              '<a href="{prefix}/pretraga/?od={city}">polazaka iz {city}a</a>. Prikazujemo autobuske i železničke rute sa cenom, trajanjem i brojem polazaka.',
        'en': 'For intercity travel use the <a href="{prefix}/rute/">all-routes page</a> or search directly via '
              '<a href="{prefix}/pretraga/?od={city}">departures from {city}</a>. We show bus and train routes with price, duration and departure count.',
        'ru': 'Для междугородних поездок используйте <a href="{prefix}/rute/">страницу всех маршрутов</a> или ищите напрямую через '
              '<a href="{prefix}/pretraga/?od={city}">рейсы из {city}</a>. Показываем автобусные и ж/д маршруты с ценой, временем и количеством рейсов.',
    },

    # ── Hub SEO intros & FAQ: carriers_index (/prevoznici/) ──
    'carriers.intro_h': {
        'sr': 'Autobuski i železnički prevoznici u Srbiji',
        'en': 'Bus and rail carriers in Serbia',
        'ru': 'Автобусные и железнодорожные перевозчики Сербии',
    },
    'carriers.intro_p1': {
        'sr': 'U Srbiji posluje više desetina autobuskih i železničkih prevoznika, od velikih nacionalnih operatera kao što su '
              '<strong>Lasta</strong> (najveći operater u zemlji sa bazom u Beogradu), '
              '<strong>Niš-Ekspres</strong> (lider na jugu Srbije), '
              '<strong>Srbija Voz</strong> (državna železnica) do malih lokalnih firmi koje povezuju udaljena mesta sa najbližim gradskim čvorištima. '
              'Međunarodni prevoznici poput <strong>OZLEM</strong>, <strong>GEA Tours</strong> i <strong>FUDEKS</strong> '
              'opslužuju linije ka Turskoj, Bugarskoj, Severnoj Makedoniji, Austriji, Nemačkoj, Mađarskoj i Crnoj Gori. '
              'Na Prevozni.com imamo preko 66 operatera sa 517 aktivnih linija — za svakog prikazujemo listu ruta, povezanih gradova i, kada je dostupno, zvanični sajt.',
        'en': 'Serbia is served by dozens of bus and rail carriers — from large national operators such as '
              '<strong>Lasta</strong> (the biggest carrier, based in Belgrade), '
              '<strong>Niš-Ekspres</strong> (leading in southern Serbia), '
              '<strong>Srbija Voz</strong> (state railway) — down to small local companies linking outlying towns to the nearest city hub. '
              'International carriers like <strong>OZLEM</strong>, <strong>GEA Tours</strong> and <strong>FUDEKS</strong> '
              'serve lines to Turkey, Bulgaria, North Macedonia, Austria, Germany, Hungary and Montenegro. '
              'Prevozni.com lists 66+ operators with 517 active lines — for each one we show the route list, cities served and, when available, the official site.',
        'ru': 'В Сербии работают десятки автобусных и ж/д перевозчиков — от крупных национальных операторов, таких как '
              '<strong>Lasta</strong> (крупнейший перевозчик, база в Белграде), '
              '<strong>Niš-Ekspres</strong> (лидер на юге Сербии), '
              '<strong>Srbija Voz</strong> (гос. ж/д), до мелких местных компаний, соединяющих отдалённые города с ближайшими узлами. '
              'Международные перевозчики <strong>OZLEM</strong>, <strong>GEA Tours</strong>, <strong>FUDEKS</strong> — '
              'линии в Турцию, Болгарию, С. Македонию, Австрию, Германию, Венгрию и Черногорию. '
              'На Prevozni.com — 66+ операторов и 517 активных линий; по каждому — список маршрутов, города обслуживания и, где доступно, официальный сайт.',
    },
    'carriers.intro_p2': {
        'sr': 'Prevoznici su sortirani po broju linija koje opslužuju, tako da su na vrhu stranice najveći operateri. '
              'Klikom na ime prevoznika dobijate listu svih njegovih ruta sa direktnim linkovima na stranice pojedinačnih linija '
              '(npr. <a href="{prefix}/rute/">pregled svih ruta</a>). '
              'Ukoliko ne znate pouzdano koji prevoznik vam odgovara, preporučujemo da krenete od odredišta: izaberite rutu (npr. '
              '<a href="{prefix}/voznja/beograd-do-budva/">Beograd — Budva</a>) i pogledajte polaske sortirane po ceni i vremenu — '
              'tu ćete videti koji operater nudi najbolju opciju za vaš termin. Za gradski prevoz svakog grada (GSP, JGSP, Niš-Ekspres) '
              'posetite <a href="{prefix}/gradski/">stranicu gradskog prevoza</a>.',
        'en': 'Carriers are sorted by number of routes served, so the biggest operators appear first. '
              'Clicking a carrier name opens a list of its routes with direct links to individual line pages '
              '(for example <a href="{prefix}/rute/">all routes</a>). '
              'If you\'re not sure which carrier suits you, start from the destination: pick a route (e.g. '
              '<a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva</a>) and sort departures by price and time — '
              'you\'ll see which operator offers the best option for your schedule. For city transit (GSP, JGSP, Niš-Ekspres) '
              'visit the <a href="{prefix}/gradski/">city transit page</a>.',
        'ru': 'Перевозчики отсортированы по числу маршрутов, так что крупнейшие — сверху. '
              'При клике на имя перевозчика открывается список его маршрутов с прямыми ссылками на страницы линий '
              '(например <a href="{prefix}/rute/">все маршруты</a>). '
              'Если не уверены, какой перевозчик подходит, начните с направления: выберите маршрут (например '
              '<a href="{prefix}/voznja/beograd-do-budva/">Белград — Будва</a>), отсортируйте рейсы по цене и времени — '
              'увидите лучший вариант. Для городского транспорта (GSP, JGSP, Niš-Ekspres) — '
              '<a href="{prefix}/gradski/">страница городского транспорта</a>.',
    },
    'carriers.faq_heading': {
        'sr': 'Česta pitanja o prevoznicima',
        'en': 'Frequently asked questions about carriers',
        'ru': 'Частые вопросы о перевозчиках',
    },
    'carriers.faq_q1': {
        'sr': 'Koji je najveći autobuski prevoznik u Srbiji?',
        'en': 'Which is the largest bus carrier in Serbia?',
        'ru': 'Кто крупнейший автобусный перевозчик Сербии?',
    },
    'carriers.faq_a1': {
        'sr': 'Najveći operater je Lasta sa bazom u Beogradu — opslužuje preko 200 domaćih i međunarodnih linija. '
              'Niš-Ekspres dominira na jugu zemlje, dok je Srbija Voz jedini železnički operater. '
              'Kompletna lista prevoznika sa brojem linija i povezanim gradovima dostupna je na ovoj stranici.',
        'en': 'The largest operator is Lasta, based in Belgrade — serving 200+ domestic and international routes. '
              'Niš-Ekspres dominates the south, while Srbija Voz is the sole rail operator. '
              'A complete list of carriers with route counts and cities served is on this page.',
        'ru': 'Крупнейший оператор — Lasta (база в Белграде) — более 200 внутренних и международных маршрутов. '
              'Niš-Ekspres лидирует на юге, а Srbija Voz — единственный ж/д оператор. '
              'Полный список с числом маршрутов и городами — на этой странице.',
    },
    'carriers.faq_q2': {
        'sr': 'Kako da uporedim cene između različitih prevoznika?',
        'en': 'How do I compare prices between carriers?',
        'ru': 'Как сравнить цены между перевозчиками?',
    },
    'carriers.faq_a2': {
        'sr': 'Otvorite stranicu rute (npr. <a href="{prefix}/rute/">katalog ruta</a>) i pogledajte kolonu cene za svaki polazak — '
              'pored cene je naveden i prevoznik, tako da je lako uporediti. SEO parne stranice /voznja/grad1-do-grad2/ dodatno prikazuju raspon cena i najjeftinijeg operatera.',
        'en': 'Open a route page (e.g. the <a href="{prefix}/rute/">route catalog</a>) and check the price column — '
              'each departure shows the operator alongside the price. SEO city-pair pages at /voznja/city1-do-city2/ additionally show the price range and the cheapest operator.',
        'ru': 'Откройте страницу маршрута (например <a href="{prefix}/rute/">каталог маршрутов</a>) и смотрите столбец цены — '
              'рядом с ценой указан перевозчик. SEO-страницы пар /voznja/gorod1-do-gorod2/ также показывают диапазон цен и самого дешёвого оператора.',
    },
    'carriers.faq_q3': {
        'sr': 'Da li su podaci o prevoznicima zvanični?',
        'en': 'Is the carrier data official?',
        'ru': 'Официальные ли данные о перевозчиках?',
    },
    'carriers.faq_a3': {
        'sr': 'Podaci se dobijaju automatski iz javnih izvora (busticket4.me, polazak.rs, srbijavoz.rs) i agregiraju nekoliko puta dnevno. '
              'Nismo zvanični partner prevoznika — za rezervaciju mesta ili specifične uslove prevoza savetujemo posetu zvaničnog sajta operatera (link je na svakoj kartici).',
        'en': 'Data is pulled automatically from public sources (busticket4.me, polazak.rs, srbijavoz.rs) and aggregated several times a day. '
              'We are not an official carrier partner — for reservations or specific travel conditions please visit the carrier\'s official site (link on each card).',
        'ru': 'Данные автоматически собираются из публичных источников (busticket4.me, polazak.rs, srbijavoz.rs) и агрегируются несколько раз в день. '
              'Мы не являемся официальным партнёром перевозчиков — для бронирования или уточнения условий посетите официальный сайт оператора (ссылка на каждой карточке).',
    },

    # ── Hub SEO intros & FAQ: stations_index (/autobuske-stanice/) ──
    'stations.intro_h': {
        'sr': 'Autobuske i železničke stanice u Srbiji',
        'en': 'Bus and train stations in Serbia',
        'ru': 'Автобусные и железнодорожные станции Сербии',
    },
    'stations.intro_p1': {
        'sr': 'Glavne čvorne stanice Srbije — autobuske i železničke — povezuju preko 100 gradova i 66 prevoznika u jedinstvenu mrežu. '
              '<strong>Beogradska autobuska stanica (BAS)</strong> na Novom Beogradu je najveće čvorište u zemlji, sa preko 2000 dnevnih polazaka ka svim delovima Srbije i Evrope. '
              '<strong>Centralna železnička stanica Beograd Centar (Prokop)</strong> je glavni železnički čvor od 2018. — polazak za Novi Sad, Subotice, Niš i međunarodne pravce. '
              'Tu su i druga važna čvorišta: <strong>Autobuska stanica Novi Sad</strong>, <strong>Autobuska stanica Niš</strong>, '
              '<strong>Autobuska stanica Subotica</strong> (granica sa Mađarskom), <strong>Prijepolje</strong> i <strong>Užice</strong> za linije ka Crnoj Gori i BiH.',
        'en': 'Serbia\'s main hub stations — bus and rail — connect 100+ cities and 66 carriers into a single network. '
              '<strong>Belgrade Bus Station (BAS)</strong> in Novi Beograd is the country\'s largest hub, with 2,000+ daily departures across Serbia and Europe. '
              '<strong>Belgrade Centar (Prokop)</strong> is the country\'s main railway hub since 2018 — departures to Novi Sad, Subotica, Niš and international destinations. '
              'Other key hubs: <strong>Novi Sad Bus Station</strong>, <strong>Niš Bus Station</strong>, '
              '<strong>Subotica Bus Station</strong> (Hungarian border), and <strong>Prijepolje</strong> / <strong>Užice</strong> for lines to Montenegro and Bosnia.',
        'ru': 'Главные узловые станции Сербии — автобусные и ж/д — связывают 100+ городов и 66 перевозчиков в единую сеть. '
              '<strong>Белградский автовокзал (BAS)</strong> в Новом Белграде — крупнейший узел страны, 2000+ рейсов в сутки по всей Сербии и Европе. '
              '<strong>Белград Центар (Прокоп)</strong> — главный ж/д узел с 2018 года: рейсы в Нови-Сад, Суботицу, Ниш и международные направления. '
              'Другие важные узлы: <strong>автовокзал Нови-Сада</strong>, <strong>автовокзал Ниша</strong>, '
              '<strong>автовокзал Суботицы</strong> (граница с Венгрией), <strong>Приеполе</strong> и <strong>Ужице</strong> — линии в Черногорию и БиГ.',
    },
    'stations.intro_p2': {
        'sr': 'Za svaku stanicu prikazujemo grad, tip (autobuska / železnička) i broj ruta koje polaze sa nje. '
              'Ukupno u bazi imamo desetke stanica grupisanih po gradovima — pogledajte <a href="{prefix}/rute/">katalog međugradskih ruta</a> '
              'ili direktno otvorite stranicu nekog od ključnih gradova, npr. <a href="{prefix}/voznja/beograd-do-novi-sad/">Beograd — Novi Sad</a> '
              'ili <a href="{prefix}/voznja/beograd-do-budva/">Beograd — Budva</a>. '
              'Na stanicama se karte kupuju na blagajnama ili kod vozača u vozilu; u Beogradu i Novom Sadu su blagajne otvorene od 05:00 do 23:00, '
              'sa radom tokom noći na glavnim međunarodnim polazcima. Stanice u manjim mestima često nemaju noćnu smenu — preporučujemo kupovinu karte unapred.',
        'en': 'For every station we show the city, type (bus / rail) and the number of routes departing from it. '
              'The database holds dozens of stations grouped by city — browse the <a href="{prefix}/rute/">intercity route catalog</a> '
              'or jump to a key city pair directly, e.g. <a href="{prefix}/voznja/beograd-do-novi-sad/">Belgrade — Novi Sad</a> '
              'or <a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva</a>. '
              'Tickets are sold at station counters or on-board from the driver; in Belgrade and Novi Sad counters are open 05:00–23:00, '
              'with overnight service on major international departures. Smaller stations often lack a night shift — buy your ticket in advance.',
        'ru': 'По каждой станции показываем город, тип (автобусная / ж/д) и количество маршрутов отправления. '
              'В базе — десятки станций, сгруппированных по городам. Смотрите <a href="{prefix}/rute/">каталог междугородних маршрутов</a> '
              'или переходите сразу к ключевой паре, например <a href="{prefix}/voznja/beograd-do-novi-sad/">Белград — Нови-Сад</a> '
              'или <a href="{prefix}/voznja/beograd-do-budva/">Белград — Будва</a>. '
              'Билеты продаются в кассах или у водителя; в Белграде и Нови-Саде кассы работают 05:00–23:00, '
              'с ночными окнами на крупных международных рейсах. В малых городах ночной смены часто нет — покупайте билет заранее.',
    },
    'stations.faq_heading': {
        'sr': 'Često postavljana pitanja o stanicama',
        'en': 'Frequently asked questions about stations',
        'ru': 'Частые вопросы о станциях',
    },
    'stations.faq_q1': {
        'sr': 'Gde se nalazi glavna autobuska stanica u Beogradu?',
        'en': 'Where is Belgrade\'s main bus station?',
        'ru': 'Где находится главный автовокзал Белграда?',
    },
    'stations.faq_a1': {
        'sr': 'Glavna BAS (Beogradska autobuska stanica) nalazi se u Novom Beogradu, Blok 42, odmah pored železničke stanice Beograd Centar (Prokop). '
              'Od centra grada do nje se stiže linijama gradskog autobusa 78, 95 i E9 za oko 15 minuta. '
              'Stara stanica BAS na Savamali zatvorena je 2019. godine.',
        'en': 'The main BAS (Belgrade Bus Station) is in Novi Beograd, Block 42, next to Belgrade Centar railway station (Prokop). '
              'From the city centre it\'s reachable by city buses 78, 95 or E9 in about 15 minutes. '
              'The old BAS in Savamala closed in 2019.',
        'ru': 'Главный BAS (Белградский автовокзал) — в Новом Белграде, Блок 42, рядом с ж/д вокзалом Београд Центар (Прокоп). '
              'Из центра — городскими автобусами 78, 95 или E9 за ~15 минут. '
              'Старый автовокзал BAS в Савамале закрыт в 2019 году.',
    },
    'stations.faq_q2': {
        'sr': 'Mogu li da kupim kartu na stanici ili samo online?',
        'en': 'Can I buy a ticket at the station or only online?',
        'ru': 'Можно ли купить билет на станции или только онлайн?',
    },
    'stations.faq_a2': {
        'sr': 'Karte se uvek mogu kupiti na blagajni autobuske ili železničke stanice, bez dodatnih taksi. '
              'Online kupovina preko partnerskih sajtova ponekad nudi popust ili bržu rezervaciju mesta, naročito za popularne linije tokom letnje sezone ili praznika. '
              'Za međugradske linije tokom leta preporučujemo kupovinu 2–3 dana unapred.',
        'en': 'Tickets are always sold at bus and train station counters, with no booking fees. '
              'Online purchase via partner sites sometimes offers a discount or faster seat reservation, especially for popular routes in summer and around holidays. '
              'For intercity lines in summer we recommend buying 2–3 days in advance.',
        'ru': 'Билеты всегда можно купить в кассах автовокзала или ж/д вокзала без дополнительных сборов. '
              'Онлайн-покупка через партнёров иногда даёт скидку или быстрое бронирование места, особенно на популярных рейсах летом и в праздники. '
              'Для междугородних рейсов летом советуем покупать билет за 2–3 дня.',
    },
    'stations.faq_q3': {
        'sr': 'Koja je najbliža međunarodna stanica u Srbiji?',
        'en': 'What is Serbia\'s closest international station?',
        'ru': 'Какая ближайшая международная станция в Сербии?',
    },
    'stations.faq_a3': {
        'sr': 'Zavisi od pravca putovanja: Subotica za Mađarsku, Dimitrovgrad za Bugarsku, Preševo za Severnu Makedoniju, '
              'Priboj ili Užice za Bosnu i Hercegovinu, Prijepolje ili Novi Pazar za Crnu Goru. '
              'Beogradski BAS takođe opslužuje najviše međunarodnih linija, uključujući direktne polaske ka Istanbulu, Beču, Minhenu, Frankfurtu i Zurich-u.',
        'en': 'It depends on direction: Subotica for Hungary, Dimitrovgrad for Bulgaria, Preševo for North Macedonia, '
              'Priboj or Užice for Bosnia, Prijepolje or Novi Pazar for Montenegro. '
              'Belgrade BAS also handles the most international lines, including direct departures to Istanbul, Vienna, Munich, Frankfurt and Zurich.',
        'ru': 'Зависит от направления: Суботица — в Венгрию, Димитровград — в Болгарию, Прешево — в С. Македонию, '
              'Прибой или Ужице — в БиГ, Приеполе или Нови-Пазар — в Черногорию. '
              'BAS Белграда также имеет больше всего международных рейсов, включая прямые на Стамбул, Вену, Мюнхен, Франкфурт и Цюрих.',
    },

    # ── Hub SEO intros & FAQ: destinations (/destinacije/) ──
    'dest.intro_h': {
        'sr': 'Popularne destinacije iz Srbije',
        'en': 'Popular destinations from Serbia',
        'ru': 'Популярные направления из Сербии',
    },
    'dest.intro_p1': {
        'sr': 'Sa centralnim položajem na Balkanu, Srbija je odlična polazna tačka za putovanja autobusom ili vozom ka glavnim turističkim i poslovnim centrima regiona. '
              'Letnji pravci ka <strong>Crnogorskom primorju</strong> (Budva, Herceg Novi, Kotor, Bar, Tivat, Ulcinj) imaju pojačane polaske tokom juna–septembra, '
              'sa noćnim autobusima iz Beograda koji stižu ujutru na obalu. '
              'Gradovi bivše Jugoslavije — <strong>Sarajevo, Mostar, Banja Luka, Zagreb, Split, Dubrovnik, Ljubljana, Skoplje, Bitola</strong> — '
              'su dostupni direktnim autobuskim linijama, sa putovanjem od 4 do 10 sati. '
              'Centralnoevropski pravci (<strong>Budimpešta, Beč, Minhen, Frankfurt, Prag</strong>) imaju dnevne i noćne autobuske rute sa Beogradske autobuske stanice, '
              'a za Tursku (<strong>Istanbul</strong>) polazi direktan autobus iz Beograda i Niša.',
        'en': 'With its central Balkan location, Serbia is a superb starting point for bus and rail travel to the region\'s main tourism and business hubs. '
              'Summer routes to the <strong>Montenegrin coast</strong> (Budva, Herceg Novi, Kotor, Bar, Tivat, Ulcinj) run on increased frequency June–September, '
              'with overnight buses from Belgrade arriving on the coast by morning. '
              'Former-Yugoslavia cities — <strong>Sarajevo, Mostar, Banja Luka, Zagreb, Split, Dubrovnik, Ljubljana, Skopje, Bitola</strong> — '
              'are reachable by direct bus lines, with journeys of 4–10 hours. '
              'Central-European routes (<strong>Budapest, Vienna, Munich, Frankfurt, Prague</strong>) run day and night from Belgrade Bus Station, '
              'and a direct bus to Turkey (<strong>Istanbul</strong>) departs from Belgrade and Niš.',
        'ru': 'Благодаря центральному положению на Балканах Сербия — отличная отправная точка для автобусных и ж/д поездок по региону. '
              'Летние рейсы на <strong>побережье Черногории</strong> (Будва, Херцег-Нови, Котор, Бар, Тиват, Улцинь) усилены июнь–сентябрь — '
              'ночные автобусы из Белграда приходят на побережье утром. '
              'Города бывшей Югославии — <strong>Сараево, Мостар, Баня-Лука, Загреб, Сплит, Дубровник, Любляна, Скопье, Битола</strong> — '
              'доступны прямыми автобусами, поездка 4–10 часов. '
              'Центральноевропейские направления (<strong>Будапешт, Вена, Мюнхен, Франкфурт, Прага</strong>) — дневные и ночные автобусы с BAS, '
              'в Турцию (<strong>Стамбул</strong>) прямой автобус отправляется из Белграда и Ниша.',
    },
    'dest.intro_p2': {
        'sr': 'Ispod je kratak pregled top 14 destinacija sa direktnim linkovima na stranice konkretnih ruta — '
              'za svaku destinaciju navedene su glavne polazišne tačke iz Srbije (Beograd, Novi Sad, Niš, Subotica). '
              'Za kompletan katalog međugradskih ruta posetite <a href="{prefix}/rute/">/rute/</a>, '
              'a za pretragu po imenu grada iskoristite <a href="{prefix}/pretraga/">pretragu polazaka</a>. '
              'Cene karata, broj dnevnih polazaka i prosečno trajanje putovanja prikazani su na stranici svake rute, sa mogućnošću online kupovine preko partnerskih sajtova. '
              'Savet: za letnje pravce ka obali rezervišite kartu bar 7 dana unapred, a za međunarodne linije ka Turskoj i Nemačkoj čak 14 dana — '
              'cene rastu kako se datum polaska približava, a kapacitet noćnih polazaka je ograničen.',
        'en': 'Below is a quick overview of the top 14 destinations with direct links to the route pages — '
              'each destination lists the main starting points from Serbia (Belgrade, Novi Sad, Niš, Subotica). '
              'For the full intercity catalog visit <a href="{prefix}/rute/">/rute/</a>, '
              'and for name-based search use <a href="{prefix}/pretraga/">the departures search</a>. '
              'Ticket prices, daily-departure counts and average journey time are listed on each route page, with online booking available via partner sites. '
              'Tip: for summer coastal routes book at least 7 days ahead, for international lines to Turkey and Germany as much as 14 days — '
              'prices rise as departure nears and night-bus capacity is limited.',
        'ru': 'Ниже — краткий обзор топ-14 направлений с прямыми ссылками на страницы маршрутов; '
              'у каждого направления указаны основные отправные точки в Сербии (Белград, Нови-Сад, Ниш, Суботица). '
              'Полный каталог — на <a href="{prefix}/rute/">/rute/</a>, '
              'поиск по названию города — в <a href="{prefix}/pretraga/">поиске рейсов</a>. '
              'Цены билетов, число рейсов в день и среднее время в пути — на странице каждого маршрута, с возможностью онлайн-покупки через партнёров. '
              'Совет: на летнее побережье бронируйте минимум за 7 дней, на международные рейсы в Турцию и Германию — за 14; '
              'цены растут по мере приближения даты, а ночные автобусы ограничены по вместимости.',
    },
    'dest.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'dest.faq_q1': {
        'sr': 'Koliko traje putovanje autobusom od Beograda do Budve?',
        'en': 'How long is the bus ride from Belgrade to Budva?',
        'ru': 'Сколько едет автобус из Белграда в Будву?',
    },
    'dest.faq_a1': {
        'sr': 'Putovanje autobusom Beograd — Budva traje u proseku 11–12 sati, u zavisnosti od prevoznika i rute (preko Užica/Prijepolja ili Zlatibora). '
              'Noćni polasci (u 20:00–22:00) stižu u Budvu oko 07:00–09:00 ujutru, što je najpovoljniji izbor za letnju sezonu. '
              'Detalji na <a href="{prefix}/voznja/beograd-do-budva/">stranici Beograd — Budva</a>.',
        'en': 'The Belgrade — Budva bus ride averages 11–12 hours, depending on operator and routing (via Užice/Prijepolje or Zlatibor). '
              'Overnight departures (20:00–22:00) reach Budva around 07:00–09:00, the best option for summer. '
              'Details on the <a href="{prefix}/voznja/beograd-do-budva/">Belgrade — Budva page</a>.',
        'ru': 'Автобус Белград — Будва едет в среднем 11–12 часов в зависимости от перевозчика и маршрута (через Ужице/Приеполе или Златибор). '
              'Ночные рейсы (20:00–22:00) приходят в Будву ~07:00–09:00 — лучший вариант летом. '
              'Подробности на <a href="{prefix}/voznja/beograd-do-budva/">странице Белград — Будва</a>.',
    },
    'dest.faq_q2': {
        'sr': 'Treba li mi viza ili pasoš za Crnu Goru, BiH, Severnu Makedoniju?',
        'en': 'Do I need a visa or passport for Montenegro, Bosnia or North Macedonia?',
        'ru': 'Нужна ли виза или паспорт для Черногории, БиГ или С. Македонии?',
    },
    'dest.faq_a2': {
        'sr': 'Građani Srbije mogu da putuju sa ličnom kartom u Crnu Goru, Bosnu i Hercegovinu, Severnu Makedoniju i Albaniju — bez pasoša. '
              'Za Hrvatsku (članica Šengena od 2023.) potreban je pasoš ili lična karta u zavisnosti od dokumenta. '
              'Za zemlje EU van Šengena i Tursku preporučujemo pasoš sa važenjem od najmanje 6 meseci od datuma ulaska.',
        'en': 'Serbian citizens can travel with a national ID to Montenegro, Bosnia and Herzegovina, North Macedonia and Albania — no passport required. '
              'For Croatia (in Schengen since 2023) a passport or national ID is needed depending on the document. '
              'For non-Schengen EU countries and Turkey, carry a passport valid at least 6 months from the entry date.',
        'ru': 'Граждане Сербии могут ездить по внутреннему ID в Черногорию, Боснию и Герцеговину, С. Македонию и Албанию — без загранпаспорта. '
              'Для Хорватии (в Шенгене с 2023) нужен паспорт или ID в зависимости от документа. '
              'В страны ЕС вне Шенгена и Турцию — заграничный паспорт со сроком действия не менее 6 месяцев.',
    },
    'dest.faq_q3': {
        'sr': 'Koja destinacija ima najjeftiniji autobuski polazak iz Beograda?',
        'en': 'Which destination has the cheapest bus from Belgrade?',
        'ru': 'В какое направление самый дешёвый автобус из Белграда?',
    },
    'dest.faq_a3': {
        'sr': 'Za blize destinacije cene počinju od oko 10€: Novi Sad, Niš, Subotica, Kragujevac. '
              'Za regionalne destinacije najpovoljnije su Sarajevo, Skoplje i Banja Luka (20–30€). '
              'Letnji polasci na crnogorsko primorje mogu biti skuplji (30–45€) zbog veće tražnje — bukiranje unapred je ključno za niže cene.',
        'en': 'Nearby destinations start around €10: Novi Sad, Niš, Subotica, Kragujevac. '
              'In the region, the best-value are Sarajevo, Skopje and Banja Luka (€20–30). '
              'Summer coastal runs to Montenegro can cost €30–45 due to high demand — early booking matters for lower fares.',
        'ru': 'Ближние направления — от ~10€: Нови-Сад, Ниш, Суботица, Крагуевац. '
              'Из региональных выгоднее всего Сараево, Скопье и Баня-Лука (20–30€). '
              'Летние рейсы на побережье Черногории дороже (30–45€) из-за спроса — ранняя бронь снижает цену.',
    },

    # ── home FAQ (only) ──
    'home.faq_heading': {
        'sr': 'Često postavljana pitanja',
        'en': 'Frequently asked questions',
        'ru': 'Частые вопросы',
    },
    'home.faq_q1': {
        'sr': 'Šta je Prevozni.com?',
        'en': 'What is Prevozni.com?',
        'ru': 'Что такое Prevozni.com?',
    },
    'home.faq_a1': {
        'sr': 'Prevozni.com je besplatan agregator reda vožnje autobusa, vozova, tramvaja i trolejbusa u Srbiji. '
              'Pokrivamo gradski prevoz u Beogradu, Novom Sadu, Nišu i Kragujevcu, kao i više od 270 međugradskih i međunarodnih ruta. '
              'Nema registracije, nema reklama, podaci se ažuriraju svakodnevno iz zvaničnih izvora.',
        'en': 'Prevozni.com is a free aggregator of bus, train, tram and trolleybus schedules in Serbia. '
              'We cover city transit in Belgrade, Novi Sad, Niš and Kragujevac, plus 270+ intercity and international routes. '
              'No signup, no ads, data refreshes daily from official sources.',
        'ru': 'Prevozni.com — бесплатный агрегатор расписания автобусов, поездов, трамваев и троллейбусов Сербии. '
              'Охватываем городской транспорт Белграда, Нови-Сада, Ниша и Крагуеваца, плюс 270+ междугородних и международных маршрутов. '
              'Без регистрации, без рекламы, данные обновляются ежедневно из официальных источников.',
    },
    'home.faq_q2': {
        'sr': 'Koje gradove i rute pokriva sajt?',
        'en': 'Which cities and routes does the site cover?',
        'ru': 'Какие города и маршруты покрывает сайт?',
    },
    'home.faq_a2': {
        'sr': 'U bazi imamo 4 grada sa detaljnim gradskim prevozom (610 linija, 3700+ stajališta) i 517 međugradskih/međunarodnih ruta '
              '(Crna Gora, BiH, Hrvatska, Mađarska, Severna Makedonija, Turska, Nemačka, Austrija i dr.). '
              'Puni pregled je na <a href="{prefix}/gradski/">stranici gradskog prevoza</a> i <a href="{prefix}/rute/">katalogu ruta</a>.',
        'en': 'The database holds 4 cities with detailed city transit (610 lines, 3,700+ stops) and 517 intercity/international routes '
              '(Montenegro, Bosnia, Croatia, Hungary, North Macedonia, Turkey, Germany, Austria and more). '
              'Full overview on the <a href="{prefix}/gradski/">city transit page</a> and <a href="{prefix}/rute/">route catalog</a>.',
        'ru': 'В базе — 4 города с подробным городским транспортом (610 линий, 3700+ остановок) и 517 междугородних/международных маршрутов '
              '(Черногория, БиГ, Хорватия, Венгрия, С. Македония, Турция, Германия, Австрия и др.). '
              'Полный обзор на <a href="{prefix}/gradski/">странице городского транспорта</a> и <a href="{prefix}/rute/">каталоге маршрутов</a>.',
    },
    'home.faq_q3': {
        'sr': 'Da li je sajt besplatan i bez reklama?',
        'en': 'Is the site free and ad-free?',
        'ru': 'Бесплатный ли сайт и без рекламы?',
    },
    'home.faq_a3': {
        'sr': 'Da, Prevozni.com je potpuno besplatan i bez registracije. Ne prikazujemo invazivne reklame i ne prodajemo vaše podatke. '
              'Posetu pratimo samo putem anonimne analitike (Umami), a projekat se izdržava povremenim affiliate provizijama kod kupovine karata preko naših partnera.',
        'en': 'Yes, Prevozni.com is fully free and no-signup. We do not display intrusive ads and do not sell your data. '
              'Visits are tracked only with anonymous analytics (Umami); the project is funded by occasional affiliate commissions when you buy tickets via our partners.',
        'ru': 'Да, Prevozni.com полностью бесплатный и без регистрации. Мы не показываем навязчивую рекламу и не продаём ваши данные. '
              'Посещения фиксируются только анонимной аналитикой (Umami); проект живёт за счёт редких партнёрских комиссий при покупке билетов через партнёров.',
    },

    # ── Popular / "See also" blocks ──
    'city_transport.popular_routes_h': {
        'sr': 'Popularne međugradske rute iz {city}a',
        'en': 'Popular intercity routes from {city}',
        'ru': 'Популярные междугородние маршруты из {city}',
    },
    'route_index.related_cities_h': {
        'sr': 'Otkrijte gradski prevoz',
        'en': 'Explore city transit',
        'ru': 'Изучите городской транспорт',
    },
}

SUPPORTED_LANGS = ('sr', 'en', 'ru')
DEFAULT_LANG = 'sr'


def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """Get translated string. Falls back to Serbian, then to key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key

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
}

SUPPORTED_LANGS = ('sr', 'en', 'ru')
DEFAULT_LANG = 'sr'


def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """Get translated string. Falls back to Serbian, then to key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or key

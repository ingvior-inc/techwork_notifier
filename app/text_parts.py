HAPPENED_FAILURE = '#технический_сбой'
HAPPENED_TECHNICAL_WORK = '#технические_работы'

HAPPENED_FAILUTE_RESOLVE = HAPPENED_FAILURE + ' устранён'
HAPPENED_TECHNICAL_WORK_RESOLVE = HAPPENED_TECHNICAL_WORK + ' завершены'

######################################################

PROVIDER = '<b>Ответственный: </b>'

PROVIDER_SELF = 'VEPAY'
PROVIDER_TKB = 'Банк ТКБ'
PROVIDER_FORTA_TECH = 'Провайдер Forta Tech'
PROVIDER_BRS = 'Банк Русский Стандарт (БРС)'
PROVIDER_WALLETTO = 'Провайдер Walletto'

#######################################################

DATE_AND_TIME = '<b>Когда: </b>'

#######################################################

situations = [HAPPENED_FAILURE, HAPPENED_TECHNICAL_WORK,
              HAPPENED_FAILUTE_RESOLVE, HAPPENED_TECHNICAL_WORK_RESOLVE]
providers = [PROVIDER_SELF, PROVIDER_TKB, PROVIDER_FORTA_TECH, PROVIDER_BRS,
             PROVIDER_WALLETTO]

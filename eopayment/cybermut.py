from common import PaymentCommon, FORM
from collections import namedtuple
import hmac
import hashlib

CREDIT_MUTUEL = 'Credit Mutuel'
CIC = 'CIC'
OBC = 'OBC'

TEST = 'test'
PRODUCTION = 'production'

URL_BANQUES = {
        CREDIT_MUTUEL: {
            TEST: 'https://paiement.creditmutuel.fr/test/paiement.cgi',
            },
        CIC: {
            TEST: 'https://ssl.paiement.cic-banques.fr/test/paiement.cgi',
        },
        OBC: {
            TEST: 'https://ssl.paiement.banque-obc.fr/test/paiement.cgi',
        },
}

Parameter = namedtuple('Parameter', ['name', 'default', 'sign'])

class Payment(PaymentCommon):
    REQUEST_FIELDS = [
            Parameter('TPE', '', True),
            Parameter('date', '', True),
            Parameter('montant', '', True),
            Parameter('reference', '', True),
            Parameter('texte_libre', '', True),
            Parameter('version', '1.2open', True),
            Parameter('lgue', 'FR', True),
            Parameter('societe', '', True),
            Parameter('url_retour', '', False),
            Parameter('url_retour_ok', '', False),
            Parameter('url_retour_err', '', False),
    ]


    def __init__(self, options):
        self.cle = options.pop('cle')
        banque = options.pop('banque')
        plateforme = options.pop('plateforme')
        try:
            self.url = URL_BANQUES[banque][plateforme]
        except KeyError:
            raise RuntimeError('cybermut: there is no %s URL for bank %s' % (plateforme, banque))
        self.tpe = options.pop('tpe')
        self.options = options

    def cybermut_request(self, **parameters):
        datagramme = []
        form = {}
        data = self.options.copy()
        data.update(parameters)
        for parameter in self.REQUEST_FIELDS:
            value = data.get(parameter.name, parameter.default)
            if parameter.sign:
                datagramme.append(value)
            form[parameter.name] = value
        datagramme = '*'.join(datagramme)
        form['MAC'] = hmac.new(self.cle, datagramme, hashlib.sha1
                1;4
                1;2P
        


    def request(self, 

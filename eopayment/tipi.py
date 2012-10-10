# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_DOWN
from common import (PaymentCommon, PaymentResponse, URL, PAID, DENIED,
        CANCELED, ERROR)
from urllib import urlencode
from urlparse import parse_qs
from gettext import gettext as _
import logging

from systempayv2 import isonow

__all__ = ['Payment']

TIPI_URL = 'http://www.jepaiemesserviceslocaux.dgfip.finances.gouv.fr' \
        '/tpa/paiement.web'
LOGGER = logging.getLogger(__name__)
SEPARATOR = '#'

class Payment(PaymentCommon):
    '''Produce requests for and verify response from the TIPI online payment
    processor from the French Finance Ministry.

    '''

    description = {
            'caption': 'TIPI, Titres Payables par Internet',
            'parameters': [
                {
                    'name': 'numcli',
                    'caption': _(u'Numéro client'),
                    'help_text': _(u'un numéro à 6 chiffres communiqué par l’administrateur TIPI'),
                    'validation': lambda s: str.isdigit(s) and (0 < int(s) < 1000000),
                    'required': True,
                },
                {
                    'name': 'service_url',
                    'default': TIPI_URL,
                    'caption': _(u'URL du service TIPI'),
                    'help_text': _(u'ne pas modifier si vous ne savez pas'),
                    'validation': lambda x: x.startswith('http'),
                    'required': True,
                }
            ],
    }

    def __init__(self, options, logger=LOGGER):
        self.service_url = options.pop('service_url', TIPI_URL)
        self.numcli = options.pop('numcli', '')
        self.logger = logger

    def request(self, amount, next_url=None, exer=None, refdet=None,
            objet=None, mel=None, saisie=None, **kwargs):
        try:
            montant = Decimal(amount)
            if Decimal('0') > montant > Decimal('9999.99'):
                raise ValueError('MONTANT > 9999.99 euros')
            montant = montant*Decimal('100')
            montant = montant.to_integral_value(ROUND_DOWN)
        except ValueError:
            raise ValueError('MONTANT invalid format, must be '
                    'a decimal integer with less than 4 digits '
                    'before and 2 digits after the decimal point '
                    ', here it is %s' % repr(amount))
        if next_url is not None:
            if not isinstance(next_url, str) or \
                not next_url.startswith('http'):
                raise ValueError('URLCL invalid URL format')
        try:
            if exer is not None:
                exer = int(exer)
                if exer > 9999:
                    raise ValueError()
        except ValueError:
            raise ValueError('EXER format invalide')
        try:
            refdet = str(refdet)
            if len(refdet) != 18:
                raise ValueError('len(REFDET) != 18')
        except Exception, e:
            raise ValueError('REFDET format invalide, %r' % refdet, e)
        if objet is not None:
            try:
                objet = str(objet)
            except Exception, e:
                raise ValueError('OBJET must be a string', e)
            if not objet.replace(' ','').isalnum():
                raise ValueError('OBJECT must only contains '
                        'alphanumeric characters, %r' % objet)
            if len(objet) > 99:
                raise ValueError('OBJET length must be less than 100')
        try:
            mel = str(mel)
            if '@' not in mel:
                raise ValueError('no @ in MEL')
            if not (6 <= len(mel) <= 80):
                raise ValueError('len(MEL) is invalid, must be between 6 and 80')
        except Exception, e:
            raise ValueError('MEL is not a valid email, %r' % mel, e)

        if saisie not in ('M', 'T', 'X', 'A'):
            raise ValueError('SAISIE invalid format, %r, must be M, T, X or A' % saisie)

        iso_now = isonow()
        transaction_id = '%s_%s' % (iso_now, refdet)
        if objet:
            objet = objet[:100-len(iso_now)-2] + ' ' + SEPARATOR \
                    + iso_now
        else:
            objet = SEPARATOR + iso_now
        params = {
                'NUMCLI': self.numcli,
                'REFDET': refdet,
                'MONTANT': montant,
                'MEL': mel,
                'SAISIE': saisie,
                'OBJET': objet,
        }
        if exer:
            params['EXER'] = exer
        if next_url:
            params['URLCL'] = next_url
        url = '%s?%s' % (self.service_url, urlencode(params))
        return transaction_id, URL, url

    def response(self, query_string):
        fields = parse_qs(query_string, True)
        for key, value in fields.iteritems():
            fields[key] = value[0]
        refdet = fields.get('REFDET')
        if refdet is None:
            raise ValueError('REFDET is missing')
        if 'OBJET' in fields and SEPARATOR in fields['OBJET']:
            iso_now = fields['OBJET'].rsplit(SEPARATOR, 1)[1]
        else:
            iso_now = isonow()
        transaction_id = '%s_%s' % (iso_now, refdet)

        result = fields.get('RESULTRANS')
        if result == 'P':
            result = PAID
            bank_status = ''
        elif result == 'R':
            result = DENIED
            bank_status = 'refused'
        elif result == 'A':
            result = CANCELED
            bank_status = 'canceled'
        else:
            bank_status = 'wrong return: %r' % result
            result = ERROR
        return PaymentResponse(
                result=result,
                bank_status=bank_status,
                signed=True,
                bank_data=fields,
                transaction_id=transaction_id)

if __name__ == '__main__':
    p = Payment({'numcli': '12345'})
    print p.request(amount=Decimal('123.12'),
            exer=9999,
            refdet=999900000000999999,
            objet='tout a fait',
            mel='bdauvergne@entrouvert.com',
            urlcl='http://example.com/tipi/test',
            saisie='T')
    print p.response('OBJET=tout+a+fait+%2320121010131958&MONTANT=12312&SAISIE=T&MEL=bdauvergne%40entrouvert.com&NUMCLI=12345&EXER=9999&REFDET=999900000000999999&RESULTRANS=P')
